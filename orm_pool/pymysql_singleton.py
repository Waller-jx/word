import pymysql
from orm_pool.db_pool import POOL


class Mysql(object):
    # 单例
    # _instance = None


    def __init__(self):
        self.conn = POOL.connection()
        # 创建光标
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
    def close_db(self):
        self.cursor.close()
        self.conn.close()

    # 查询
    def select(self, sql, args=None):  # args 是where后面的查询条件
        self.cursor.execute(sql, args)
        res = self.cursor.fetchall()  # 拿到的数据结构是类别套字典
        return res

    # 插值,改值
    def execute(self, sql, args):
        # insert into table(name, password) values('www', '123')
        # update table set name = 'www',password = '123' where id = 1
        try:
            self.cursor.execute(sql, args)
        except BaseException as e:
            print(e)

    # @classmethod
    # def singleton(cls):
    #     # 判断_instance 是否有值
    #     if not cls._instance:
    #         # 没有值,实例化
    #         cls._instance = cls()
    #     return cls._instance  # 调用方拿到的永远是同一个实例化对象