# -*- coding: utf-8 -*-
# !/usr/bin/python3
def sort_ip(_ping_result_list):
    # _ping_result_list = [(IP, 丢包率, 延迟), ...]
    ip_a, ip_b, ip_c = [], [], []
    for _item in _ping_result_list:
        if not _item[1]:  # 符合要求的ip与其延迟编入列表
            ip_a.append((_item[0], _item[2]))
        elif _item[1] <= 25:
            ip_b.append((_item[0], _item[2]))
        elif _item[1] != 100:  # 丢包率这么高估计是没什么用了，舍弃
            ip_c.append((_item[0], _item[2]))
    # 指定第二个元素（延迟）正向排序
    ip_a.sort(key=lambda x: x[1], reverse=False)
    ip_b.sort(key=lambda x: x[1], reverse=False)
    ip_c.sort(key=lambda x: x[1], reverse=False)
    # print("丢包率为0的IP：", ip_a)
    # print("丢包率不大于25的IP：", ip_b)
    # print("丢包率超过25的IP：", ip_c)
    return ip_a, ip_b, ip_c
    # ip_a = [(IP, 延迟), ...]


def get_better_ip(_ping_result_list):
    # _ping_result_list = [(IP, 丢包率, 延迟), ...]
    ip_list = sort_ip(_ping_result_list)
    ip_a, ip_b, ip_c = ip_list[0], ip_list[1], ip_list[2]
    # 取出连接较优的三个ip
    ip = []
    text = 0
    if len(ip_a) >= 3:
        code = 1
        ip = [ip_a[0][0], ip_a[1][0], ip_a[2][0]]
    elif len(ip_a):
        code = 1
        for item in ip_a:
            ip.append(item[0])
        num = 3 - len(ip_a)
        for item in ip_b:
            ip.append(item[0])
            num -= 1
            if not num:
                break
    else:
        if ip_b:
            code = 2
            text = "与目标域名连接情况较差"
            num = 3
            for item in ip_b:
                ip.append(item[0])
                num -= 1
                if not num:
                    break
        else:
            code = 0
            if ip_c:
                text = "与目标域名连接情况极差，不进行操作"
            else:
                text = "未能与目标域名连接,不进行操作"
    return code, ip, text


if __name__ == "__main__":

    xx = get_better_ip([("1,1,1,1", 0, 50), ("1,1,1,2", 100, 20), ("1,1,1,3", 100, 30),
                        ("1,1,1,4", 100, 10), ("1,1,1,5", 100, 23), ("1,1,1,6", 100, 10),
                        ("1,1,1,7", 100, 10), ("1,1,1,8", 100, 23), ("1,1,1,9", 100, 10)])
    print(xx)
