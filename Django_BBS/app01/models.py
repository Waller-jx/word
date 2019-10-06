from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.



# 扩展默认的auth_user表(自定义auth_user表)
# 用户表
class UserInfo(AbstractUser):
    # 电话字段
    phone = models.BigIntegerField(null=True,blank=True)  # blank用来告诉admin后台该字段可以不填
    # 用户头像字段,用户上传的头像自动保存到avatar问价夹内,若内上传头像,使用默认的
    avatar = models.FileField(upload_to='avatar/', default='avatar/default.jpg')

    # 用户表与个人站点表是一对一关系
    blog = models.OneToOneField(to='Blog',null=True)

    class Meta:
        verbose_name_plural = '用户表'

    def __str__(self):
        return self.username


# 个人站点表
class Blog(models.Model):
    site_title = models.CharField(max_length=32)
    site_name = models.CharField(max_length=32)
    # 站点样式主题字段
    site_them = models.CharField(max_length=255)

    def __str__(self):
        return self.site_name


# 分类表
class Category(models.Model):
    name = models.CharField(max_length=32)
    # 一个个人站点可以有多个分类
    blog = models.ForeignKey(to='Blog')

    def __str__(self):
        return self.name


# 标签表
class Tag(models.Model):
    name = models.CharField(max_length=32)
    # 一个个人站点可以有多个标签
    blog = models.ForeignKey(to='Blog')

    def __str__(self):
        return self.name


# 文章表
class Article(models.Model):
    # 文章台头
    title = models.CharField(max_length=255)
    # 文章描述
    desc = models.CharField(max_length=255)
    # 文章内容
    content = models.TextField()  # 存大段文本
    create_time = models.DateField(auto_now_add=True)

    # 数据库优化字段,创建事务,不用频繁跨表查询
    # 评论数字段
    comment_num = models.IntegerField(default=0)
    # 点赞数字段
    up_num = models.IntegerField(default=0)
    down_num = models.IntegerField(default=0)

    # 文章表与个人站点表是一对多关系
    blog = models.ForeignKey(to='Blog')
    # 分类表与文章表是一对多关系,一个分类可以有多篇文章
    category = models.ForeignKey(to='Category', null=True)
    # 标签表与文章表是多对多关系
    tag = models.ManyToManyField(to='Tag',through='Article2Tag',through_fields=('article','tag') )

    def __str__(self):
        return self.title


# 文章表与标签表多对多关系的第三张表
class Article2Tag(models.Model):
    # 文章外键字段
    article = models.ForeignKey(to='Article')
    # 标签外键字段
    tag = models.ForeignKey(to='Tag')



# 点赞表 该表与用户表以及文章表是一对多的关系
class UpAndDown(models.Model):
    # 一对多用户表外键字段
    user = models.ForeignKey(to='UserInfo')
    # 一对多文章表
    article = models.ForeignKey(to='Article')
    # 是否点赞字段
    is_up = models.BooleanField()  # 传布尔值 0/1


# 评论表
class Comment(models.Model):
    # 一对多用户表外键字段
    user = models.ForeignKey(to='UserInfo')
    # 一对多文章表
    article = models.ForeignKey(to='Article')
    # 评论的内容字段
    content = models.CharField(max_length=255)
    create_time = models.DateField(auto_now_add=True)
    # 一对多评论表(自关联)字段 如果有值说明你是子评论  如果没有值说明你是父评论
    parent = models.ForeignKey(to='self', null=True)







