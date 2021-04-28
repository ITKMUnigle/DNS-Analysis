# -*- coding: utf-8 -*-
# !/usr/bin/python3
from json import loads
from re import search
from time import sleep, time
import urllib.parse
import urllib.request
# from multiprocessing import Pool


def _domain_taskid(_domain, url='https://www.ping.cn/check'):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/89.0.4389.90 Safari/537.36 ',
        'cookies': 'boce_session'
                   '=eyJpdiI6ImlLQTM1QStRSXVkKzVkOTQxQXliNEE9PSIsInZhbHVlIjoiSVJWbkNPRVJENHNnUk4xeWNld09qd2lrWWJHeUs1ZE'
                   'hudjJGVWo2RlQ3c1pPMWJJaElcL3V6OE5BMDFlNmtOYmd5WXFISHBScVJ2NlR1NmJMZ2VGQTFBPT0iLCJtYWMiOiJkMjlkYTk5Y'
                   'TdjMzUyMTVhOTMxNjIzMmM3NTRmMTNmNWQyNTlmNWE5NGU4NmVmM2U4OGNkNmQ0ZjdmMDA0ZjBkIn0%3D',
        'referer': 'https://www.ping.cn/dns/' + urllib.parse.quote(_domain)
    }
    data = {
        'host': urllib.parse.quote(_domain),
        'host2': '',
        'type': 'dns',
        # '_token': '40WWIxFRWKNwTTbgCo0ZvjucpBknMKZK6OJrjyqz',
        'create_task': '1',
        'node_ids': '',
        'isp': '1,2,3,9,10,11',
        'dns_server': '',
        'dns_type': 'A'
    }
    # 发送请求获取带有taskID的数据
    data = urllib.parse.urlencode(data).encode('utf-8')
    # data 如果要传bytes（字节流）类型的，如果是一个字典，先用urllib.parse.urlencode()编码。
    req = urllib.request.Request(url=url, data=data, headers=headers)
    response = urllib.request.urlopen(req)
    result = response.read().decode('utf-8')
    json_dict = loads(result)
    # 提取出需要的taskID
    if json_dict.get('code') == -1:
        code = 0
        taskid = json_dict.get('msg')
    elif json_dict.get('code') == 1:
        code = 1
        taskid = json_dict.get('data').get('taskID')
    else:
        code = 2
        taskid = ""
    return code, _domain, taskid


def _taskid_iplist(_domain, taskid, url='https://www.ping.cn/check'):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/89.0.4389.90 Safari/537.36 ',
        'cookies': 'boce_session'
                   '=eyJpdiI6ImlLQTM1QStRSXVkKzVkOTQxQXliNEE9PSIsInZhbHVlIjoiSVJWbkNPRVJENHNnUk4xeWNld09qd2lrWWJHeUs1ZE'
                   'hudjJGVWo2RlQ3c1pPMWJJaElcL3V6OE5BMDFlNmtOYmd5WXFISHBScVJ2NlR1NmJMZ2VGQTFBPT0iLCJtYWMiOiJkMjlkYTk5Y'
                   'TdjMzUyMTVhOTMxNjIzMmM3NTRmMTNmNWQyNTlmNWE5NGU4NmVmM2U4OGNkNmQ0ZjdmMDA0ZjBkIn0%3D',
        'referer': 'https://www.ping.cn/dns/' + urllib.parse.quote(_domain)
    }
    data = {
        'task_id': taskid,
        # '_token': '40WWIxFRWKNwTTbgCo0ZvjucpBknMKZK6OJrjyqz',
        'host': urllib.parse.quote(_domain),
        'type': 'dns',
        'create_task': '0'
    }
    # 发送请求获取包含ip的数据
    data = urllib.parse.urlencode(data).encode('utf-8')
    # data 如果要传bytes（字节流）类型的，如果是一个字典，先用urllib.parse.urlencode()编码。
    req = urllib.request.Request(url=url, data=data, headers=headers)
    response = urllib.request.urlopen(req)
    result = response.read().decode('utf-8')
    # 筛选出ip数据
    json_dict = loads(result)
    if json_dict.get('code') == -1:
        code = 0
        ip_list = []
        ip_list2 = []
    elif json_dict.get('code') == 1:
        exam = json_dict.get('data').get('initData').get('ipPre')
        ip_list = []
        ip_list2 = []
        for item in exam:
            ip_list.append(item.get('ip'))
            ip_list2.append(item.get('pre'))
        if sum(ip_list2) < 25:
            code = 3
            ip_list = []
            ip_list2 = []
        else:
            code = 1
            ip_list_sel = []
            for i in range(len(ip_list2)):
                if ip_list2[i] >= 3:
                    ip_list_sel.append(ip_list[i])
            # 删去CNAME解析的域名数据与可能存在的，不知道为什么会掺入的本机地址
            ip_list = [i for i in ip_list_sel if not (bool(search(r'[^.\d]', i) or i in ['0.0.0.0', '127.0.0.1']))]
    else:
        code = 2
        ip_list = []
        ip_list2 = []
    return code, _domain, ip_list, ip_list2


def get_iplist(_domain):
    # time1 = time()
    taskid = _domain_taskid(_domain)  # 尝试获取taskid
    if taskid[0] == 0:  # 检测是否成功获取taskid
        code = 0
        iplist = taskid[2]
    elif taskid[0] == 1:
        sleep(5)
        _get_list = 0
        iplist = []
        temlist = []
        temtemlist = []
        xxxx = time()
        for i in range(6):  # 循环6次，利用taskid获取ip列表
            xxx = time()
            iplist = _taskid_iplist(taskid[1], taskid[2])
            temlist = iplist[3]
            print(_domain + '.第%d次获取，' % (i+1) + '耗时{:.2f}s'.format(time() - xxx))
            if time() - xxx < 2:
                sleep(1)

            if iplist[0] == 1:  # 检测是否成功获取ip列表
                # print('查询到')
                # print(time() - xxxx)
                if temlist == temtemlist:
                    print(_domain + '.获取成功，总耗时{:.2f}s'.format(time() - xxxx))
                    break
                temtemlist = temlist
            elif iplist[0] == 2:  # 两次未收到返回数据时结束运行
                if _get_list != 2:
                    _get_list = 2
                    sleep(2)
                else:
                    break
            elif iplist[0] == 3:
                break
        if iplist[0] == 0:  # 根据获得数据输出返回值
            code = 0
            iplist = "提取IP失败，网络差或未知原因"
        elif iplist[0] == 1:
            code = 1
            iplist = iplist[2]
        elif iplist[0] == 2:
            code = 0
            iplist = "未收到返回数据，请检查网络"
        elif iplist[0] == 3:
            code = 0
            iplist = "提取IP失败,请检查域名是否正确"
        else:
            code = 0
            iplist = "未知错误2"
    elif taskid[0] == 2:
        code = 0
        iplist = "未连接到查询入口，请检查网络"
    else:
        code = 0
        iplist = "未知错误"
    # print("查询时间：", time() - time1, _domain)
    return code, _domain, iplist


if __name__ == "__main__":
    # aaa = get_iplist("dst.metrics.klei.com")
    aaa = "sukemcce.xyz"
    # aaa = input("请输入要查询的域名：\n（如 www.baidu.com )\n多个域名以英文逗号“,”分开\n")
    print(get_iplist(aaa))

    # if not aaa:
    #     print("未输入内容")
    # else:
    #     aaa_list = []
    #     if ',' in aaa:
    #         aaa_list = aaa.split(",")
    #     else:
    #         aaa_list.append(aaa)
    #     print("查询域名数量：%d个" % len(aaa_list))
    #     pool = Pool(processes=len(aaa_list))
    #     results = [pool.apply_async(get_iplist, (aa,))
    #                for aa in aaa_list
    #                ]
    #     pool.close()
    #     pool.join()
    #     output = [p.get() for p in results]
    #     for _i in output:
    #         print(_i)
    #     print("结束")
