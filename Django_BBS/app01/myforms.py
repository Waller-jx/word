
from django import forms
from django.forms import  widgets
from app01 import models




class MyRegForm(forms.Form):
    # username字段及校验条件
    username = forms.CharField(max_length=8,min_length=3,label='用户名',
                               error_messages={
                                   'max_length':'用户名最大八位',
                                   'min_length':'用户名最小三位',
                                   'required':'用户名不能为空',
                               },widget=widgets.TextInput(attrs={'class':'form-control'})
                               )
    # password字段及校验条件
    password = forms.CharField(max_length=8,min_length=3,label='密码',
                               error_messages={
                                   'max_length': '密码最大八位',
                                   'min_length': '密码最小三位',
                                   'required': '密码不能为空',
                               },widget=widgets.PasswordInput(attrs={'class':'form-control'})
                               )
    confirm_password = forms.CharField(max_length=8,min_length=3,label='确认密码',
                               error_messages={
                                   'max_length': '密码最大八位',
                                   'min_length': '密码最小三位',
                                   'required': '确认密码不能为空',
                               },widget=widgets.PasswordInput(attrs={'class':'form-control'})
                               )
    email = forms.EmailField(label='邮箱',error_messages={
        'required': '邮箱不能为空',
        'invalid':'邮箱格式错误',
    },widget=widgets.EmailInput(attrs={'class':'form-control'}))


    # 局部钩子 校验用户是否存在
    def clean_username(self):
        # 先在cleaned_data字典中拿出username
        username = self.cleaned_data.get('username')
        # 到UserInfo表中查询用户是否存在
        is_user = models.UserInfo.objects.filter(username=username)
        # 判断
        if is_user:
            # 若存在添加错误提示到error中
            self.add_error('username','用户已存在')
        # 将username返回
        return username

    # 全局钩子 校验两次密码是一致
    def clean(self):
        # 先在cleaned_data字典中拿出password与confirm_password
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        # 判断
        if not password == confirm_password:
            self.add_error('confirm_password','两次密码不一致')
        return self.cleaned_data








