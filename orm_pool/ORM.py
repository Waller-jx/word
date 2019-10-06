from orm_pool.pymysql_singleton import Mysql


# 字段类的父类,所有字段类都有的基本属性,包括字段名,字段类型,是否是主键,默认值
class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default


# 定义varchar字段类型
class StringField(Field):
    def __init__(self, name, column_type = 'varchar(32)', primary_key = False, default = None):
        super().__init__(name, column_type, primary_key, default)

# 定义int字段类型
class IntegerField(Field):
    def __init__(self, name, column_type = 'init', primary_key = False, default = 0):
        super().__init__(name, column_type, primary_key, default)




# 把类映射成一张表(模型表),让类在创建后就应该有表的基本属性(表名,字段,主键)
# 通过控制类的创建过程,拦截__new__改写名称空间class_attrs,将表名,字段,主键添加进去
class MyMetaClass(type):
    def __new__(cls, class_name, class_bases, class_attrs):
        # 我们定义的元类是用来拦截模型表的创建过程,而Models不是模型表,所以不用拦截
        if class_name == 'Models':
            return type.__new__(cls,class_name, class_bases, class_attrs)

        # 表名 从模型表的名称空间中取出table_name,若没有class_name就是表名
        table_name = class_attrs.get('table_name', class_name)
        # 主键
        primary_key = None
        # 所有的表的字段
        mappings = {}
        # 将模型表的名称空间中键值对拿出解压赋值
        for k,v in class_attrs.items():
            # 判断 v 是否是 Field 的实例化,筛选出自己定义的表的字段属性
            if isinstance(v, Field):
                # 将自己定义的模型表的字段存入mappings字典中
                mappings[k] = v
                # 判断 v对象 中是否有主键属性
                if v.primary_key:
                    if primary_key:
                        raise TypeError('一张表有且只有一个主键')
                    # 如果有主键 就给 primary_key 赋值字段的名字
                    primary_key = v.name
        for k in mappings.keys():
            # 将 class_attrs 与 mappings 中重复的 k 删除
            class_attrs.pop(k)

        # 如果 模型表 没有主键 抛出异常
        if not primary_key:
            raise TypeError('一张表必须要有一个主键')
        # 将 table_name, primary_key, mappings 存到模型表的名空间中,方便对象点的形式取
        class_attrs['table_name'] = table_name
        class_attrs['primary_key'] = primary_key
        class_attrs['mappings'] = mappings
        return type.__new__(cls,class_name, class_bases, class_attrs)






class Models(dict, metaclass=MyMetaClass):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __getattr__(self, item):
        return self.get(item, '提示:没有该键')

    def __setattr__(self, key, value):
        self[key] = value

    # 查询的最小单位是表,查询表中有什么,所以是类(模型表绑定方法)
    @classmethod
    def select(cls, **kwargs):  # **kwargs 是筛选条件, 如 id = 1
        # 实例化查询对象
        ms = Mysql()
        # 当查询整张表没有筛选条件时
        # select * from %s
        if not kwargs:
            sql = "select * from %s"%cls.table_name   # cls.table_name 是表名
            res = ms.select(sql)

        else:
            # 当查询整张表有筛选条件时
            # select * from %s where %s = %s
            k = list(kwargs.keys())[0]
            v = kwargs.get(k)
            # 防止sql注入问题
            sql = "select * from %s where %s = ?"%(cls.table_name, k)  # select * from user where id = ?
            sql = sql.replace('?','%s')  # select * from user where id = %s
            res = ms.execute(sql, v)
        if res:
            # res 拿到的数据结构是列表套字典
            return [cls(**i) for i in res]  # 把列表里的一个个字典,传给 **i 变成 id = 1 的形式,cls() 实例化出一个个对象

    def save(self):
        ms = Mysql()
        # insert into user(name,password) values('jason','123')
        fields = []
        # 专门用来存储与字段对应数量的？
        args = []
        values = []
        for k,v in self.mappings.items():  # name:StringField(name='name')
            if not v.primary_key:  # 将id字段去除 因为id字段是自增，不需要人为的去操作
                fields.append(v.name)
                args.append('?')
                values.append(getattr(self,v.name,v.default))
        sql = "insert into %s(%s) values(%s)"%(self.table_name,','.join(fields),','.join(args))
        # insert into user(name,password) values(?,?)
        sql = sql.replace("?",'%s')
        # insert into user(name,password) values(%s,%s)
        ms.execute(sql,values)

    def update(self):
        ms = Mysql()
        # update user set name='jason',password='123' where id = 1
        # update user set name=%s,password=%s where id = 1
        # 定义一个列表存储该表的所有字段名
        fields = []
        # 定义一个变量用来存储当前数据对象的主键值
        pr = None
        values = []
        for k, v in self.mappings.items():
            # 先把当前数据对象对应的主键值拿到
            if v.primary_key:
                pr = getattr(self, v.name, v.default)
            else:
                # 除了主键之外的所有字段
                fields.append(v.name + '=?')  # [name=?,password=?...]
                values.append(getattr(self, v.name, v.default))

        sql = "update %s set %s where %s=%s" % (self.table_name, ','.join(fields), self.primary_key, pr)
        # update user set name=?,password=? where id=1
        sql = sql.replace('?', '%s')
        # update user set name=%s,password=%s where id=1
        ms.execute(sql, values)



if __name__ == '__main__':

    #模型表
    class User(Models):
        # 表名
        table_name = 'userinfo'
        # 字段 是否主键
        id = IntegerField(name='id',primary_key=True)
        name = StringField(name='name')
    # print(User.table_name)
    # print(User.primary_key)
    # # print(User.name)
    # print(User.mappings.get('name').name)
    # u = User()
    # # u.name = 'www'
    # print(u.name)
    # # print(u['name'])
    # print(u.__dict__)


    class Movie:
        pass

    class Notice:
        pass

#
# class Teacher(Models):
#     table_name = 'teacher'
#     tid = IntegerField(name='tid', primary_key=True)
#     tname = StringField(name='tname')
# res = Teacher.select()
# print(res)





