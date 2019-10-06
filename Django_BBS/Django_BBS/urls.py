"""Django_BBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app01 import views
from django.views.static import serve
from Django_BBS import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register/', views.register),
    url(r'^login/', views.login),

    # 验证码路由
    url(r'^get_code/', views.get_code),

    # 主页路由
    url(r'^home/', views.home),

    # 注销登录路由
    url(r'^logout/', views.logout),

    # 修改密码路由
    url(r'^set_password/', views.set_password),

    # 文章点赞功能
    url(r'^up_or_down/', views.up_or_down),



    # 后台管理
    url(r'^backend/',views.backend),
    # 后台添加文章
    url(r'^add_article/',views.add_article),
    # 文本编辑器上传图片功能
    url(r'^upload_img/',views.upload_img),



    # 修改头像功能
    url(r'^edit_avatar/',views.edit_avatar),





    # 评论路由
    url(r'^comment/',views.comment),

    # 个人站点路由
    url(r'^(?P<username>\w+)/$',views.site),  # 有名分组

    # 手动暴露后端media文件资源
    url(r'^media/(?P<path>.*)',serve,{'document_root':settings.MEDIA_ROOT}),

    # 侧边筛选功能
    url(r'^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/',views.site),

    # 文章详情路由
    url(r'^(?P<username>\w+)/article/(?P<article_id>\d+)/',views.article_detail),



]
