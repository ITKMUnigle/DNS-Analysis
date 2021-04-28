# -*- coding: utf-8 -*-
# !/usr/bin/python3
import ctypes
import os
from multiprocessing import freeze_support, Pool
from os.path import abspath, dirname, join as pathjoin
from sys import argv, executable, exit
from time import time, sleep, localtime, strftime

from crontab import addcron, onstart, write
from get_better_ip import get_better_ip
from get_iplist import get_iplist
from modify_hosts import add, recover
from ping import ping

# ctypes, os 使用了这两个库中不支持win或linux的函数，只能全部导入，只导入不支持的函数会报错

path = abspath(dirname(__file__))
path_domain = pathjoin(path, 'domain')
path_main = pathjoin(path, 'ipget.py')
os.chdir(path)

if __name__ == "__main__":
    # 使打包的win端可执行文件支持多进程
    freeze_support()

    if len(argv) > 1:
        print('当前时间：%s' % strftime("%Y-%m-%d %H:%M:%S", localtime()))
        if argv[1] == 'ipget':
            print()
            with open(path_domain, 'r', encoding='utf-8') as f:
                data = f.read()  # 获取文件内容
                domain_list_full = data.split('\n')
        else:
            print(argv)
            print(__file__)
            print("只支持参数：\n'ipget'--读取当前目录下的'domain'文件内容，自动为其中的域名(一行一个)添加hosts。用于支持计划任务")
            print('10s后自动关闭')
            sleep(10)
            exit()
    else:
        # 获取root或管理员权限 不知道会不会出运行环境的问题
        if os.name == 'nt':
            if not ctypes.windll.shell32.IsUserAnAdmin():
                while 1:
                    restart = input('没有管理员权限，请选择：（留空默认“1”）\n'
                                    '1.尝试获取管理员权限（若要自动以管理员权限运行，可右键程序，将“属性”中“兼容性”选项卡中的“以管理员身份运行”勾选）\n'
                                    '2.以当前权限运行（仅可查询域名对应IP后查看结果，其它操作均不会生效）\n') or '1'
                    if restart in ['1', '2']:
                        break
                    print('请输入数字“1”、“2”并回车')
                if restart == '1':
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, None, None, 1)
                    # executable和之后的一个None，一个是要打开的程序，一个是带的参数
                    exit()
            else:
                print('\n已获取管理员权限')
        elif os.name == 'posix':
            if os.geteuid():  # 检测是不是root权限，不是就加sudo运行一次
                while 1:
                    restart = input('没有root权限，请选择：（留空默认“1”）\n1.尝试获取root权限\n'
                                    '2.以当前权限运行（仅可查询域名对应IP后查看结果，其它操作均不会生效）\n') or '1'
                    if restart in ['1', '2']:
                        break
                    print('请输入数字“1”、“2”并回车')
                if restart == '1':
                    args = [executable] + argv
                    os.execlp('sudo', 'sudo', *args)

            else:
                print('\n已获取root权限')

        print('\n******！！！请确认具有root或管理员权限，否则修改不会生效！！！******\n\n说明：\n'
              ' 手动模式，以高权限打开工具，输入要查询的域名，之后会自动查询对应IP并根据延迟选出连接较好的IP加入hsots文件。\n'
              ' 自动模式，以高权限打开工具，添加要查询的域名名单，添加计划任务(ubuntu以外系统未测试，设置后请检查验证)，可选添加开机自启。之后工具会按照设置定时运行。\n')
        while 1:
            tool = input('请选择功能：（留空默认"1"）\n'
                         '1.为输入域名添加连接情况较好的hosts\n'
                         '2.清理本工具修改项，恢复原hosts\n3.设置自动运行\n') or '1'
            if tool in ['1', '2', '3']:
                break
            print('请输入数字“1”、“2”、“3”并回车')
        if tool == '2':
            while 1:
                recovery = input('请选择功能：\n'
                                 '1.清理本工具修改项，不影响其他来源修改的项\n'
                                 '2.恢复为第一次使用本工具时的hosts文件\n')
                if recovery in ['1', '2']:
                    break
                print('请输入数字“1”、“2”并回车')
            if recovery == '1':
                xx = recover('del')
                if xx[0] == 1:
                    print('成功，%s' % xx[1])
                else:
                    print('失败，%s' % xx[1])
            elif recovery == '2':
                xx = recover('recover')
                if xx[0] == 1:
                    print('成功，%s' % xx[1])
                else:
                    print('失败，%s' % xx[1])
            input('回车退出')
            exit()
        elif tool == '3':
            while 1:
                tool1 = input('请选择功能：\n1.设置计划任务\n2.修改计划任务运行时，要查询的域名\n3.设置开机运行\n')
                if tool1 in ['1', '2', '3']:
                    break
                print('请输入数字“1”、“2”、“3”并回车')
            if tool1 == '1':
                while 1:
                    tool2 = input('请选择：\n1.添加/更新计划任务\n2.删除计划任务\n')
                    if tool2 in ['1', '2']:
                        break
                    print('请输入数字“1”、“2”并回车')
                if tool2 == '1':
                    while 1:
                        tool3 = input('将每5小时运行一次，无特殊需求不用更改。\n'
                                      '若要更改，请从1-23间选取整数，对应每1-23小时运行一次。（回车默认’5‘）\n') or '5'
                        if int(tool3) in [x for x in range(1, 24)]:
                            break
                        print('请输入1-23之间的整数并回车')
                    crontab = addcron('add', tool3)
                    if crontab[0] == 1:
                        print('成功：%s%s' % ('，'.join(crontab[1]), '。'))
                    else:
                        print('失败：%s%s' % ('，'.join(crontab[1]), '。'))
                else:
                    crontab = addcron('del')
                    if crontab[0] == 1:
                        print('成功：%s%s' % ('，'.join(crontab[1]), '。'))
                    else:
                        print('失败：%s%s' % ('，'.join(crontab[1]), '。'))
            elif tool1 == '2':
                crontab = write()
            elif tool1 == '3':
                while 1:
                    tool4 = input('请选择：\n1.添加/更新开机启动任务\n2.删除开机启动任务\n')
                    if tool4 in ['1', '2']:
                        break
                    print('请输入数字“1”、“2”并回车')
                if tool4 == '1':
                    crontab = onstart('add')
                else:
                    crontab = onstart('del')
                if crontab[0] == 1:
                    print('成功：%s' % crontab[1])
                else:
                    print('失败：%s' % crontab[1])
            input('回车退出')
            exit()

        domain = input("请输入要查询的域名：\n（如 www.baidu.com 不支持中文域名)\n多个域名以英文逗号“,”分开\n")
        # domain = "sukeme.xyz,dst.metrics.klei.com,dfewgsdfgst.xyz"
        domain_list_full = domain.split(",")

    domain_list, domain_list_bad = [], []
    for _domain in domain_list_full:
        if '.' in _domain:
            domain_list.append(_domain)
        elif '一行一个域名' in _domain:
            pass
        else:
            domain_list_bad.append(_domain)
    if not domain_list:  # 检测是否有输入值
        print("无有效域名")
        if len(argv) <= 1:
            input('回车退出')
        exit()

    print('有效域名%d个，无效域名%d个，如下：' % (len(domain_list), len(domain_list_bad)))
    print('有效域名：%s' % ', '.join(map(str, [str(x + 1) + ': ' + domain_list[x] for x in range(len(domain_list))])))
    print(
        '无效域名：%s' % ', '.join(map(str, [str(x + 1) + ': ' + domain_list_bad[x] for x in range(len(domain_list_bad))])))

    '''
    以下开始
    '''

    time_begin = time()  # 记录开始时间戳，用于计算总耗时

    if len(domain_list) > 60:  # 限制线程数量，在win端线程过多会报错
        processes = 60
    else:
        processes = len(domain_list)
    print("\n查询域名数量：%d个" % len(domain_list), "耗时%ds左右" % ((len(domain_list) // 60 + 1) * 30))
    time_get_iplist_begin = time()  # 记录当前时间戳，用于计算查询IP耗时
    # 启动多线程查询IP，一个域名一个线程。由于win端不支持在上面调用，只能全堆在这里。
    pool_get_iplist = Pool(processes=processes)
    results_get_iplist = [pool_get_iplist.apply_async(get_iplist, (item,))
                          for item in domain_list
                          ]
    pool_get_iplist.close()
    pool_get_iplist.join()
    # 查询IP多线程结束
    time_get_iplist_end = time()  # 记录当前时间戳，用于计算查询IP耗时
    print("查询IP耗时：%.2fs" % (time_get_iplist_end - time_get_iplist_begin))
    iplist_full = [item.get() for item in results_get_iplist]

    iplist_success, iplist_failure = [], []
    for x in iplist_full:  # 检查状态码，分离错误项，记录错误信息
        if x[0]:
            iplist_success.append((x[1], x[2]))
        else:
            iplist_failure.append((x[1], x[2]))

    if iplist_success:
        print("查询成功：%d个，域名如下" % len(iplist_success))
        num = 0
        for x in iplist_success:
            num += 1
            print("域名%s：%s" % (num, x[0]))
    if iplist_failure:
        print("查询失败：%d个，错误信息如下：" % len(iplist_failure))
        num = 0
        for x in iplist_failure:
            num += 1
            print("域名%d：%s\n失败原因：%s" % (num, x[0], x[1]))

    iplist, domainlist = [], []
    for item in iplist_success:  # 记录域名iplist中对应的索引
        _i = list(item[1])
        _i = _i[:50]
        iplist += _i  # 提取出所有的IP
        domainlist += [(item[0], len(iplist))]

    if not len(iplist):
        if len(argv) <= 1:
            input('未解析到IP，回车退出。')
        exit()

    if len(iplist) > 60:  # 限制线程数量，在win端线程过多会报错
        processes = 60
    else:
        processes = len(iplist)
    print("\n测试Ping值，IP数量：%d个" % len(iplist), "耗时%ds左右" % ((len(iplist) // 60 + 1) * 10))
    time_ping_begin = time()  # 记录当前时间戳，用于计算Ping耗时
    # 启动多线程Ping，一个IP一个线程。由于win端不支持在上面调用，只能全堆在这里。
    pool_ping = Pool(processes=processes)
    results_ping = [pool_ping.apply_async(ping, (item,))
                    for item in iplist
                    ]
    pool_ping.close()
    pool_ping.join()
    # Ping多线程结束
    time_ping_end = time()  # 记录当前时间戳，用于计算Ping耗时
    print("测试Ping值耗时：%.2fs" % (time_ping_end - time_ping_begin))
    ping_test = [item.get() for item in results_ping]

    domain_ping_test_list = []
    x = 0
    for item in domainlist:  # 对返回的IP根据对应域名分组，以便筛选
        domain_ping_test_list.append(ping_test[x:item[1]])
        x = item[1]

    if len(domain_ping_test_list) > 60:  # 限制线程数量，在win端线程过多会报错
        processes = 60
    else:
        processes = len(domain_ping_test_list)
    # print("\n选取较优连接，数量：%d组" % len(domain_ping_test_list), "耗时%ds左右" % 1)
    # time_get_better_ip = time()  # 记录当前时间戳，用于计算筛选IP耗时
    # 启动多线程筛选IP，一组IP一个线程。由于win端不支持在上面调用，只能全堆在这里。
    pool_get_better_ip = Pool(processes=processes)
    results_get_better_ip = [pool_get_better_ip.apply_async(get_better_ip, (item,))
                             for item in domain_ping_test_list
                             ]
    pool_get_better_ip.close()
    pool_get_better_ip.join()
    # 筛选IP多线程结束
    # print("选取较优连接耗时：%.2fs" % (time()-time_get_better_ip))
    better_ip_full = [item.get() for item in results_get_better_ip]

    better_ip, warn_ip, false_ip = [], [], []
    num = -1
    for item in better_ip_full:  # 检查状态码，分离错误项，记录错误信息
        num += 1
        if item[0] == 0:
            false_ip.append((domainlist[num][0], item[2]))
        elif item[0] == 1:
            better_ip.append((domainlist[num][0], item[1]))
        elif item[0] == 2:
            better_ip.append((domainlist[num][0], item[1]))
            warn_ip.append((domainlist[num][0]))
        else:
            print("未知错误，域名：%s" % domainlist[num][0])

    if better_ip:
        print("Ping成功：%d个，域名如下" % len(better_ip), )
        num = 0
        for x in better_ip:
            num += 1
            print("域名%d：%s" % (num, x[0]))
    if warn_ip:
        print("其中有%d个连接情况较差，域名如下：" % len(warn_ip))
        num = 0
        for x in warn_ip:
            num += 1
            print("域名%d：%s" % (num, x))
    if false_ip:
        print("Ping失败：%d个，错误信息如下：" % len(false_ip))
        num = 0
        for x in false_ip:
            num += 1
            print("域名：%s\n失败原因：%s" % (x[0], x[1]))

    time_end = time()
    print("\n总耗时：%.2fs" % (time_end - time_begin))
    for item in better_ip:
        print(item[0], end=': ')
        print(', '.join(map(str, item[1])))

    if len(argv) > 1:
        result = add(better_ip, 'Y')
        if result[0] == 1:
            print('写入hosts文件成功。\n%s' % result[1])
        else:
            print('写入hosts文件失败。\n%s' % result[1])
        print('------------')
        print()
    else:
        while True:
            result = add(better_ip, 'N')
            if result[0] == 1:
                print('操作成功。\n%s' % result[1])
                break
            else:
                print('操作失败。\n%s' % result[1])
                print('请确认工具具有root或管理员权限，关闭加速软件，并退出所有占用hosts文件的软件，之后再重试写入。\n若依然失败，请重启电脑。\n若依然失败，请根据错误信息自行百度解决。')
                while True:
                    readd = input('\n写入hosts文件失败，是否重试：（留空默认“1”）\n1.重试\n2.不重试，结束\n') or '1'
                    if readd in ['1', '2']:
                        break
                    print('请输入整数“1”、“2”并回车')
                if readd == '1':
                    pass
                else:
                    break

        input('回车退出')

        # # 域名查询IP相关
        # print(domain_list)  # 输入的有效域名的列表
        # print(iplist_full)  # 由"域名查询IP"返回的IP列表
        # print(iplist_success)  # iplist_full中查询成功的列表
        # print(iplist_failure)  # iplist_full中查询失败的列表
        # print(iplist)  # 提取出iplist_success中的所有IP
        # print(domainlist)  # 域名在iplist中对应IP的索引
        # print("查询IP耗时：%.2fs" % (time_get_iplist_end - time_get_iplist_begin))

        # # PingIP相关w
        # print(ping_test)  # "PingIP"返回的数据列表
        # print(domain_ping_test_list)  # 将ping_test中数据根据domainlist进行分组后的列表
        # print("测试Ping值耗时：%.2fs" % (time_ping_end - time_ping_begin))

        # # 筛选IP相关
        # print(better_ip_full)  # 筛选IP后返回的IP列表
        # print(better_ip)  # better_ip_full中丢包率符合要求的IP分组与对应域名的列表
        # print(warn_ip)  # better_ip_full中丢包率高于要求的IP分组与对应域名的列表
        # print(false_ip)  # better_ip_full中丢包率过高或未能连接的IP分组与对应域名的列表

    # if len(argv) <= 1:
    #     input('回车退出')
