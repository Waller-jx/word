from lowb版本.notify import *

def run(content):
    wechat(content)
    msg(content)
    email(content)

if __name__ == '__main__':
    run('国庆八天假 我该去哪玩?')
