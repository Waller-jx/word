class  Msg(object):
    def __init__(self):
        pass  # 发送短信需要的代码配置

    def send(self,content):
        print('短信通知:%s' % content)