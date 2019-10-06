from django.shortcuts import render,HttpResponse,redirect
from app01 import myforms
from app01 import models
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import F


# Create your views here.


# 注册功能
def register(request):
    # 注册用户需要校验账户,密码,邮箱等信息,我们可以利用forms组件帮助校验渲染以及提示报错信息
    # 实例化自定义的MyRegForm类
    form_obj = myforms.MyRegForm
    if request.method == 'POST':
        # 定义一个字典,携带报错错误信息准备发到前端
        back_dic = {'code':100,'msg':''}
        # 校验用户信息是否合法
        form_obj = myforms.MyRegForm(request.POST)  # MyRegForm需要传一个字典,request.POST就是字典,且里是要校验的数据
        # 判断所有校验的信息是否合法
        if form_obj.is_valid():
            # 若都合法,合法的信息都存在cleaned_data字典中,且此时里面含有confirm_password,需要去除,因为后续要将信息存到库中
            clean_data = form_obj.cleaned_data
            clean_data.pop('confirm_password')
            # 用户头像不在request.POST中,需要手动获取用户头像
            user_file = request.FILES.get('myfile')
            # print(user_file,type(user_file))
            # 判断用户是否传了头像
            if user_file:
                # 若传了头像再添加到字典中,没传就用默认的
                clean_data['avatar'] = user_file  # avatar 是表中的字段名
                # print(1)
            # 创建用户
            models.UserInfo.objects.create_user(**clean_data)  # 将clean_data字典打散传入
            back_dic['msg'] = '注册成功'
            back_dic['url'] = '/login/'
        else:
            back_dic['code'] = 101
            # 若注册失败,将字段错误的信息返回前端
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)
    return render(request, 'register.html',locals())



# 登录功能
def login(request):
    if request.method == 'POST':
        back_dic = {'code':100, 'msg':''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 1.验证码
        code = request.POST.get('code')
        # 先校验验证码,忽略大小写
        if request.session.get('code').upper() == code.upper():
            # 2.利用auth模块校验
            user_obj = auth.authenticate(username=username,password=password)  # 有值是对象,没值时None
            if user_obj:
                # 3.保存用户用户状态
                auth.login(request,user_obj)
                back_dic['msg'] = '登陆成功'
                back_dic['url'] = '/home/'
            else:
                back_dic['code'] = 101
                back_dic['msg'] = '用户或密码错误'
        else:
            back_dic['code'] = 102
            back_dic['msg'] = '验证码错误'
        return JsonResponse(back_dic)
    return render(request,'login.html')


from PIL import Image,ImageDraw,ImageFont
'''
Image 用来生成图片
ImageDraw 用来在图片上写的东西
ImageFont 控制字体样式
'''
from io import BytesIO, StringIO
'''
io 是一个内存管理器模块
BytesIO 能够帮你存储数据,二进制格式
StringIO 能够帮你存储数据,字符串格式
'''
import random

# 用来所及生成图片三原色的值
def get_random():
    return random.randint(0,255),random.randint(0,255),random.randint(0,255)

# 验证码相关
def get_code(request):
    # 推导步骤1:直接将本地已经存在的图片以二进制方式读取发送
    # with open(r'图片路径','rb') as f:
    #     data = f.read()
    # return HttpResponse(data)
    # 推导步骤2:能够产生任何多张的图片的方法
    #img_obj = Image.new('RGB',(35,360),get_random())  # 参数3 :可以是具体颜色,也可以是三原色数值
    # 以文件的形式保存下来
    # with open('xxx','wb') as f:
    #     img_obj.save(f,'png')
    # # 然后再打开这个文件发送
    # with open('xxx','rb') as f:
    #     data = f.read()
    # return HttpResponse(data)
    # 推导步骤3:需要找一个能够临时存储文件的地方  避免频繁文件读写操作
    # img_obj = Image.new('RGB', (35, 360), get_random())
    # io_obj = BytesIO()  # 实例化产生一个内存管理对象  你可以把它当成文件句柄
    # img_obj.save(io_obj,'png')
    # return HttpResponse(io_obj.getvalue())  # 从内存对象中获取二级制的图片数据
    # 推导步骤4:在产生的图片上 写验证码
    img_obj = Image.new('RGB',(360,35),get_random())  # 生成图片对象
    img_draw = ImageDraw.Draw(img_obj)  # 生成一个可以在图片写字的画笔对象
    img_font = ImageFont.truetype('static/font/222.ttf',30)  # 字体样式及大小
    io_obj = BytesIO()

    # 生成5位数的验证码
    code=''
    for i in range(5):
        upper_str = chr(random.randint(65,90))
        low_str = chr(random.randint(97,122))
        random_int = str(random.randint(0,9))
        # 上面的三个中随机取一个
        temp_code = random.choice([upper_str,low_str,random_int])
        # 写在图片上
        img_draw.text((70+i*45,0),temp_code,get_random(),font=img_font)  # 大小,内容,三原色值,自体样式
        code += temp_code

    print(code)
    # 将随机生成的验证码存到session中,方便后续其他视图函数获取校验验证码
    request.session['code'] = code
    img_obj.save(io_obj,'png')
    return HttpResponse(io_obj.getvalue())



# 主页
# @login_required
def home(request):
    # 获取网站的所有文章,展示到前端
    article_list = models.Article.objects.all()
    # 文章多的情况需要做分页处理
    return render(request, 'home.html',locals())


# 注销登录
@login_required
def logout(request):
    auth.logout(request)
    return redirect('/login/')


# 修改密码
@login_required
def set_password(request):
    # 修改密码,前端是ajax提交,所以先判断此刻是否是ajax
    if request.is_ajax():
        back_dic = {'code':100,'msg':''}
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        # 先查看旧密码是否正确
        is_right = request.user.check_password(old_password)
        if is_right:
            # 判断两次密码是否一致
            if new_password == confirm_password:
                # 利用auth模块方法修改密码
                request.user.set_password(new_password)
                # 保存
                request.user.save()
                back_dic['msg'] = '密码修改成功'
                # 密码修改完成后应跳到登录页面
                back_dic['url'] = '/login/'
            else:
                back_dic['code'] = 102
                back_dic['msg'] = '两次密码不一致'
        else:
            back_dic['code'] = 101
            back_dic['msg'] = '原密码错误'
        return JsonResponse(back_dic)


# 个人站点
def site(request,username,**kwargs):
    # 先判断用户是否存在
    # print(kwargs)
    # username = kwargs.get('username')
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if  not user_obj:
        # 用户不存在返回404页面
        return render(request,'errors.html')
    # 用户对象获取个人站点,正向查询关系
    blog = user_obj.blog
    # 查询当前此人的所有文章
    article_list = models.Article.objects.filter(blog=blog)

    if kwargs:
        condition =kwargs.get('condition')
        param = kwargs.get('param')
        # 分类
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        # 标签
        elif condition == 'tag':
            article_list = article_list.filter(tag__id=param)
        # 日期
        else:
            year,month = param.split('-')
            article_list = article_list.filter(create_time__year=year,create_time__month=month)

    return render(request,'site.html',locals())


def article_detail(request,username,article_id):
    # 先获取用户用户名 查看是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        # 如果用户不存在 应该返回一个404页面
        return render(request, 'errors.html')
    blog = user_obj.blog
    # 根据文章id 查询出对应的文章 展示到前端 即可
    article_obj = models.Article.objects.filter(pk=article_id).first()

    # 根据文章 查询出对应文章的评论,展示到前端
    comment_list = models.Comment.objects.filter(article=article_obj)
    return render(request, 'article_detail.html', locals())



import json
from django.utils.safestring import mark_safe
# 点赞点踩
def up_or_down(request):
    # 先判断是否是ajax请求
    if request.is_ajax():
        back_dic = {'code':100,'msg':''}
        # 1 先校验用户是否登录
        if request.user.is_authenticated():
            # print(request.user)
            # print(request.user.is_authenticated())
            # 获取前端ajax发来的数据
            article_id = request.POST.get('article_id')
            is_up = request.POST.get('is_up')
            # post提交的数据是字符串形式的js布尔值,转成python的布尔值
            is_up = json.loads(is_up)
            # 2 判断当前文章是否是用户自己的,先获取文章对象,在获取文章的用户对象
            article_obj = models.Article.objects.filter(pk=article_id).first()
            if not article_obj.blog.userinfo == request.user:
                # 3 判断当前文章是否已经被当前用户点过赞/踩
                is_click = models.UpAndDown.objects.filter(article=article_obj,user=request.user)
                if not is_click:
                    # 4 操作数据库,记录数据,在记录的时候,需要做到文章表里的普通字段跟点赞/踩数据相同并且区分点赞点踩
                    if is_up:
                        # 如果是点赞,把文章表里的普通点赞字段加一(在原来的基础上加一)
                        models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                        back_dic['msg'] = '点赞成功'
                    else:
                        # 如果是点踩,把文章表里的普通点踩字段加一(在原来的基础上加一)
                        models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                        back_dic['msg'] = '点踩成功'
                    # 操作点赞点赞表
                    models.UpAndDown.objects.filter(article=article_obj,user=request.user,is_up=is_up)
                else:
                    back_dic['code'] = 101
                    back_dic['msg'] = '你已点过了'
            else:
                back_dic['code'] = 102
                back_dic['msg'] = '不能给自己点赞'
        else:
            back_dic['code'] = 103
            back_dic['msg'] = mark_safe('请先<a href="/login/">登录</a>')
        return JsonResponse(back_dic)


from django.db import transaction
def comment(request):
    print(000)
    if request.is_ajax():
        print(111)
        back_dic = {'code':100, 'msg':''}
        if request.user.is_authenticated():
            # 获取内容
            content = request.POST.get('content')
            article_id = request.POST.get('article_id')
            parent_id = request.POST.get('parent_id')
            '''事务'''
            # 将评论表 与 文章表中评论数的普通字段同步
            with transaction.atomic():
                models.Comment.objects.create(user=request.user,article_id=article_id,content=content,parent_id=parent_id)
                models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num')+1)
            back_dic['msg'] = '评论成功'
        else:
            back_dic['code'] = 101
            back_dic['msg'] = mark_safe('请先<a href="/login/">登录</a>')
        return JsonResponse(back_dic)



from utils.mypage import Pagination
# 后台管理
@login_required
def backend(request):
    # 将用户的所有文章展示出来
    article_list = models.Article.objects.filter(blog=request.user.blog)
    # 分页
    page_obj = Pagination(current_page=request.GET.get('page',1),all_count=article_list.count(),per_page_num=10)
    page_queryset = article_list[page_obj.start:page_obj.end]
    return render(request,'backend/backend.html',locals())



# 防止XSS攻击
from bs4 import BeautifulSoup

# 添加文章
@login_required
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        tags = request.POST.getlist('tag')
        category_id = request.POST.get('category')

        # 对html内容做放XSS攻击处理
        # 1 先生产一个BeautifulSoup对象
        soup = BeautifulSoup(content,'html.parser')  # 将收到的文本传入
        # 2 针对script标签,直接删除
        for tag in soup.find_all():
            # print(tag.name)  # 获取当前html页面所有的标签
            if tag.name == 'script':
                tag.decompose()  # 将符合的标签删除

        # 文章简介截取150个文本内容
        desc = soup.text[0:150]
        article_obj = models.Article.objects.create(
            title=title,
            desc=desc,
            content=str(soup),
            category_id=category_id,
            blog=request.user.blog,
        )

        # 因为文章与标签的第三张表是半自动创建不能用add方法添加字段数据,可以用批量添加的方法
        b_list = []
        for tag_id in tags:
            b_list.append(models.Article2Tag(
                article=article_obj,
                tag_id=tag_id),
            )
        models.Article2Tag.objects.bulk_create(b_list)
        return redirect('/backend/')

    # 标签和分类展示到添加文章页面
    tag_list = models.Tag.objects.filter(blog=request.user.blog)
    category_list = models.Category.objects.filter(blog=request.user.blog)
    return render(request,'backend/add_article.html',locals())


import os
from Django_BBS import settings

# 文章图片
def upload_img(request):
    # 接收用户写文章传的所有图片资源
    if request.method == 'POST':
        # 上传的图片都存在request.FILES这个字典中,{imgFile:file_obj}
        file_obj = request.FILES.get('imgFile')
        # 用户上传的文件图片存入media文件中,且要分门别类
        # 1.手动拼接出图片所在的文件夹路径
        base_path = os.path.join(settings.BASE_DIR,'media','article_img')
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        # 2.手动拼接文件的具体路径
        file_path = os.path.join(base_path,file_obj.name)  # file_obj.name 是文件(图片名)
        # 3.文件操作
        with open(file_path,'wb') as f:
            for line in file_obj:
                f.write(line)

        """
        //成功时
            {
                "error" : 0,
                "url" : "http://www.example.com/path/to/file.ext"
        }
        //失败时
            {
                "error" : 1,
                "message" : "错误信息"
            }
        """

        back_dic = {
            'error':0,
            'url':'/media/article_img/%s'%file_obj.name  # 文件的具体路径
        }
        return JsonResponse(back_dic)



# 修改头像
def edit_avatar(request):
    if request.method == 'POST':
        file_obj = request.FILES.get('myfile')
        if file_obj:
            request.user.avatar = file_obj
            request.user.save()
        return redirect('/%s/'%request.user.username)
    return render(request,'edit_avatar.html')









