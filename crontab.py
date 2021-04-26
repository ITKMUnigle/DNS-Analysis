# -*- coding: utf-8 -*-
# !/usr/bin/env python
from os import name, rename, remove
from os.path import abspath, dirname, exists, join as pathjoin
from subprocess import PIPE, Popen
from time import sleep

# 根据系统获取脚本绝对路径
path_domain = abspath(pathjoin(dirname(__file__), 'domain'))
path_log = abspath(pathjoin(dirname(__file__), 'ipget.log'))
path_rc = '/etc/rc.d/rc.local'
if name == 'nt':
    path = abspath(pathjoin(dirname(__file__), 'ipget.exe'))
elif name == 'posix':
    path = abspath(pathjoin(dirname(__file__), 'ipget.py'))


def check_cron_run():
    # 检测计划任务服务是否运行
    check_run = Popen(r'service --status-all | grep cron', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout_check_run, stderr_check_run = check_run.communicate()
    if 'cron' in stdout_check_run.decode('UTF8'):
        if '+' in stdout_check_run.decode('UTF8'):
            code = 1  # 计划任务服务正在运行
        else:
            code = 0
    else:
        code = 2  # 计划任务服务不存在
    return code


def addcron(is_add, xxxx=5):  # 1 <= xxxx <= 23 linux部分可按开机自启重写
    code = 0
    text, text_check_cron_win, text_del_cron_win, text_creat_cron_win = '', '', '', ''
    text_check_cron_running, text_restart_cron, text_check_cron_li, text_del_cron_li, text_creat_cron_li = [''] * 5
    if name == 'nt':
        try:
            # 检测是否已存在计划任务
            check_cron_win = Popen('schtasks | find "ipget_cron"'
                                   '', shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE, encoding='GBK')
            stdout_check_win, stderr_check_win = check_cron_win.communicate('\n')
            if stdout_check_win == stderr_check_win:
                pass  # 引用一下消除警告
            # 已有的情况下，删除原任务
            if check_cron_win.returncode == 0:
                text_check_cron_win = '任务已存在'
                # print(text_check_cron_win)
                # 删除原有任务
                del_cron_win = Popen('schtasks /delete /f /tn ipget_cron'
                                     '', shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE, encoding='GBK')
                stdout_del_win, stderr_del_win = del_cron_win.communicate('\n')
                if stdout_del_win == stderr_del_win:
                    pass  # 引用一下消除警告
                if del_cron_win.returncode == 0:
                    code = 1
                    text_del_cron_win = '原有任务已删除'
                else:
                    text_del_cron_win = '删除原有任务失败，请以管理员权限运行，未创建计划任务'
                    return 0, text_check_cron_win + ' ' + text_del_cron_win
            else:
                if is_add != 'add':
                    text_check_cron_win = '任务不存在'

            if is_add == 'add':
                # 创建计划任务
                creat_cron_win = Popen(
                    r'schtasks /create /sc hourly /mo ' + str(xxxx) + r' /tn ipget_cron /ru System /tr "' +
                    path + ' ipget >> ' + path_log + '"'
                    # r'schtasks /create /sc hourly /mo 5 /tn ipget_cron /tr ' + path
                    # r'schtasks /delete /f /tn ipget_cron'
                                                     '', shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE,
                    encoding='GBK')
                stdout, stderr = creat_cron_win.communicate('\n')  # 记录错误日志文件
                if creat_cron_win.returncode == 0:
                    code = 1
                    text_creat_cron_win = '计划任务已成功添加'
                else:
                    code = 0
                    if '拒绝访问' in stderr:
                        text_creat_cron_win = '请以管理员权限运行'
                    else:
                        text_creat_cron_win = stderr
        except Exception as e:
            return 0, e
    elif name == 'posix':
        try:
            check_cron_running = check_cron_run()
            if check_cron_running == 2:
                text_check_cron_running = '未找到cron服务，请百度自行安装'
                return 0, text_check_cron_running
            elif check_cron_running == 0:
                code = 0
                text_check_cron_running = '计划任务服务未运行，尝试启动中'

                restart = Popen(r'service cron start', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                stdout_check_run, stderr_check_run = restart.communicate()
                if stdout_check_run == stderr_check_run:
                    pass  # 引用一下消除警告
                sleep(0.5)
                restart_cron = check_cron_run()
                if restart_cron == 0:
                    text_restart_cron = '启动失败，请检查是否以root权限运行'
                    return 0, text_check_cron_running + '，' + text_restart_cron
                else:
                    text_restart_cron = '启动成功'

            # 检测是否已经存在计划任务
            check_cron_li = Popen(r"cat /etc/crontab | grep ipget", shell=True, stdout=PIPE, stderr=PIPE)
            stdout_check_cron_li, stderr_check_cron_li = check_cron_li.communicate()
            if 'ipget' not in stdout_check_cron_li.decode('UTF8'):
                if is_add != 'add':
                    text_check_cron_li = '任务不存在'
            else:
                text_check_cron_li = '任务已存在'
                # 删除原有任务
                del_cron_li = Popen(r"ex +g/ipget/d -cwq /etc/crontab", shell=True, stdout=PIPE, stderr=PIPE)
                # r"sed -i '/ipget/d' /etc/crontab"
                stdout_del_cron_li, stderr_del_cron_li = del_cron_li.communicate()
                if stdout_del_cron_li == stderr_del_cron_li:
                    pass  # 引用一下消除警告
                # print(stdout_del_cron_li.decode('UTF8'))
                if del_cron_li.returncode == 0:
                    code = 1
                    text_del_cron_li = '原有任务已删除'
                else:
                    text_del_cron_li = '原有任务删除失败，请以root权限运行，未创建新的计划任务'
                    if check_cron_running == 0:
                        return 0, text_check_cron_running + '，' + text_restart_cron + '，' + \
                               text_check_cron_li + '，' + text_del_cron_li + '。'
                    else:
                        return 0, text_check_cron_li + '，' + text_del_cron_li + '。'

            if is_add == 'add':
                creat_cron_li = Popen(
                    r'echo "30 */' + str(xxxx) + ' * * * root python3 ' + path + ' ipget >> '
                    + path_log + ' 2>&1" >> /etc/crontab'
                                 '', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                stdout_creat_cron_li, stderr_creat_cron_li = creat_cron_li.communicate()
                if creat_cron_li.returncode == 0:
                    code = 1
                    text_creat_cron_li = '成功添加计划任务'
                else:
                    code = 0
                    text_creat_cron_li = stderr_creat_cron_li.decode('UTF8')
        except Exception as e:
            code = 0
            text = e
    else:
        code = 0
        text = '仅支持linux与windows系统'
    send_text_full = [text, text_check_cron_win, text_del_cron_win, text_creat_cron_win, text_check_cron_running,
                      text_restart_cron, text_check_cron_li, text_del_cron_li, text_creat_cron_li]
    send_text = [x.strip() for x in send_text_full if x]
    send_text = [x.strip('。') for x in send_text]
    return code, send_text


def write():
    code = 1
    try:
        if not exists(path_domain):  # 没有domain文件则创建
            with open(path_domain, 'a+', encoding='utf-8') as ff:
                if ff:
                    pass
        with open(path_domain, 'r', encoding='utf-8') as f, open(path_domain + '.bak', 'w+', encoding='utf-8') as f2:
            domain_list_full = f.readlines()  # 获取以行分割的列表
            domain_list = list(set(domain_list_full))  # 去重
            domain_list = [x.strip() for x in domain_list]  # 去元素空白符
            domain_list_true = [x for x in domain_list if x and '一行一个域名' not in x]  # 去空行和提示行
            # print(domain_list_true)
            print('当前要查询的域名有%d个，如下：' % len(domain_list_true))
            print(','.join(domain_list_true))
            while 1:
                domain_do = input('请输入要执行的操作：\n1.添加域名\n2.删除域名\n')
                if domain_do in ['1', '2']:
                    break
                print('请输入数字“1”、“2”并回车')
            if domain_do == '1':
                while 1:
                    domain_add = input('请输入要添加的域名：（输入多个域名时，域名间用英文逗号”,“分开）\n')
                    if domain_add:
                        break
                    print('未输入内容')
                domain_list_add_full = domain_add.split(',')  # 根据”,“分割成列表
                domain_list_add, domain_list_add_wrong = [], []
                for domain in domain_list_add_full:  # 分离出无效域名
                    if '.' in domain:
                        domain_list_add.append(domain)
                    else:
                        domain_list_add_wrong.append(domain)
                print('有效域名%d个，无效域名%d个，如下：' % (len(domain_list_add), len(domain_list_add_full) - len(domain_list_add)))
                print('有效域名：%s' % ', '.join(
                    map(str, [str(x + 1) + ': ' + domain_list_add[x] for x in range(len(domain_list_add))])))
                print('无效域名：%s' % ', '.join(
                    map(str,
                        [str(x + 1) + ': ' + domain_list_add_wrong[x] for x in range(len(domain_list_add_wrong))])))
                domain_list_fin = list(set(domain_list_true + domain_list_add))
                if len(domain_list_fin) != len(domain_list_true + domain_list_add):
                    print('重复%d个域名，已删除旧的重复项。' % (len(domain_list_true + domain_list_add) - len(domain_list_fin)))
                print('将添加%d个域名，如下：' % len(domain_list_add))
                print(
                    ', '.join(map(str, [str(x + 1) + ': ' + domain_list_add[x] for x in range(len(domain_list_add))])))
                print('处理后有%d个域名，如下：' % len(domain_list_fin))
                print(
                    ', '.join(map(str, [str(x + 1) + ': ' + domain_list_fin[x] for x in range(len(domain_list_fin))])))
            else:
                while 1:
                    domain_del = input('请输入要删除的域名：（输入多个域名时，域名间用英文逗号”,“分开）\n')
                    if domain_del:
                        break
                    print('未输入内容')
                domain_list_del_full = domain_del.split(',')  # 根据”,“分割成列表
                domain_list_del, domain_list_del_wrong = [], []  # 分离出无效域名
                for domain in domain_list_del_full:
                    if '.' in domain:
                        domain_list_del.append(domain)
                    else:
                        domain_list_del_wrong.append(domain)
                print('有效域名%d个，无效域名%d个，如下：' % (len(domain_list_del), len(domain_list_del_full) - len(domain_list_del)))
                print('有效域名：%s' % ', '.join(
                    map(str, [str(x + 1) + ': ' + domain_list_del[x] for x in range(len(domain_list_del))])))
                print('无效域名：%s' % ', '.join(
                    map(str,
                        [str(x + 1) + ': ' + domain_list_del_wrong[x] for x in range(len(domain_list_del_wrong))])))
                domain_list_fin = list(set(domain_list_true) - set(domain_list_del))  # 删去要删除项
                print('将删去%d个域名，如下：' % len(domain_list_del))
                print(
                    ', '.join(map(str, [str(x + 1) + ': ' + domain_list_del[x] for x in range(len(domain_list_del))])))
                print('处理后有%d个域名，如下：' % len(domain_list_fin))
                print(
                    ', '.join(map(str, [str(x + 1) + ': ' + domain_list_fin[x] for x in range(len(domain_list_fin))])))
            if len(domain_list_fin) == len(domain_list_true):
                print('未修改域名名单')
            print('正在写回文件')
            f2.write('一行一个域名，行内除了域名不要加其他字符。不支持中文域名。不要修改或删除该行\n')
            for line in domain_list_fin:
                f2.write(line + '\n')
        remove(path_domain)
        rename(path_domain + '.bak', path_domain)
        print('已完成修改')
        return code
    except Exception as e:
        print('失败', e)
        return 0


def onstart(xxxx):  # /etc/rc.d/rc.local
    if name == 'nt':  # 直接复制的计划任务的，不统一返回值了
        code, text, text_check_onstart_win, text_del_onstart_win, text_creat_onstart_win = 0, '', '', '', ''
        try:
            # 检测是否已经有计划任务
            check_onstart_win = Popen('schtasks | find "ipget_onstart"'
                                      '', shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE, encoding='GBK')
            stdout_check_win, stderr_check_win = check_onstart_win.communicate('\n')
            if stdout_check_win == stderr_check_win:
                pass  # 引用一下消除警告
            # 已有的情况下，删除原任务
            if check_onstart_win.returncode == 0:
                text_check_onstart_win = '任务已存在，'
                # print(text_check_onstart_win)
                # 删除原有任务
                del_onstart_win = Popen('schtasks /delete /f /tn ipget_onstart'
                                        '', shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE, encoding='GBK')
                stdout_del_win, stderr_del_win = del_onstart_win.communicate('\n')
                if stdout_del_win == stderr_del_win:
                    pass  # 引用一下消除警告
                if del_onstart_win.returncode == 0:
                    code = 1
                    text_del_onstart_win = '原有任务已删除，'
                else:
                    text_del_onstart_win = '删除原有任务失败，请以管理员权限运行，未创建计划任务'
                    return 0, text_check_onstart_win + ' ' + text_del_onstart_win
            else:
                if xxxx != 'add':
                    code = 0
                    text_check_onstart_win = '任务不存在'

            if xxxx == 'add':
                # 创建开机启动任务
                creat_onstart_win = Popen(
                    r'schtasks /create /sc onstart /tn ipget_onstart /delay 0002:00 /ru System /tr "' +
                    path + ' ipget >> ' + path_log + '"'
                                                     '', shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE,
                    encoding='GBK')
                stdout, stderr = creat_onstart_win.communicate('\n')  # 记录错误日志文件
                if creat_onstart_win.returncode == 0:
                    code = 1
                    text_creat_onstart_win = '开机启动已成功添加。'
                else:
                    code = 0
                    if '拒绝访问' in stderr:
                        text_creat_onstart_win = '请以管理员权限运行。'
                    else:
                        text_creat_onstart_win = stderr
            return code, text + text_check_onstart_win + text_del_onstart_win + text_creat_onstart_win
        except Exception as e:
            return 0, e

    elif name == 'posix':
        try:
            text, text1 = '', ''
            with open(path_rc, 'r', encoding='utf-8') as f, open(path_rc + '.bak', 'w+', encoding='utf-8') as f2:
                data_full = f.read()  # 获取以行分割的列表
                data = data_full.split('\n')
                data = [x for x in data if x]
                data_new = []
                if xxxx == 'add':
                    for line in data:
                        if 'ipget' not in line:
                            data_new.append(line)
                        else:
                            text = '任务已存在，正在删除原有任务，'
                    f2.write('\n'.join(data_new))
                    f2.write('\nsudo python3 ' + path + ' ipget >> ' + path_log + ' 2>&1')
                    text1 = '已添加开机启动'
                else:
                    for line in data:
                        if 'ipget' not in line:
                            data_new.append(line)
                    f2.write('\n'.join(data_new))
                    text1 = '已取消开机启动'
            remove(path_rc)
            rename(path_rc + '.bak', path_rc)
            return 1, text + text1
        except Exception as e:
            return 0, e
    else:
        return 0, '仅支持linux与windows系统'


if __name__ == "__main__":
    # print(write())
    # print(onstart('add'))
    print(addcron('add'))
