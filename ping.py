# -*- coding: utf-8 -*-
# !/usr/bin/python3
from select import select
import socket
from struct import pack, unpack
from time import sleep, time


def chesksum(data):
    n = len(data)
    m = n % 2
    _sum = 0
    for _i in range(0, n - m, 2):
        _sum += (data[_i]) + ((data[_i + 1]) << 8)  # 传入data以每两个字节（十六进制）通过ord转十进制，第一字节在低位，第二个字节在高位
    if m:
        _sum += (data[-1])
    # 将高于16位与低16位相加
    _sum = (_sum >> 16) + (_sum & 0xffff)
    _sum += (_sum >> 16)  # 如果还有高于16位，将继续与低16位相加
    answer = ~_sum & 0xffff
    #  主机字节序转网络字节序列（参考小端序转大端序）
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def request_ping(data_type, data_code, data_checksum, data_id, data_sequence, payload_body):
    #  把字节打包成二进制数据
    imcp_packet = pack('>BBHHH32s', data_type, data_code, data_checksum, data_id, data_sequence, payload_body)
    icmp_chesksum = chesksum(imcp_packet)  # 获取校验和
    #  把校验和传入，再次打包
    imcp_packet = pack('>BBHHH32s', data_type, data_code, icmp_chesksum, data_id, data_sequence, payload_body)
    return imcp_packet


def raw_socket(dst_addr, imcp_packet):
    """
       连接套接字,并将数据发送到套接字
    """
    # 实例化一个socket对象，ipv4，原套接字，分配协议端口
    rawsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    # 记录当前请求时间
    send_request_ping_time = time()
    # 发送数据到网络
    rawsocket.sendto(imcp_packet, (dst_addr, 80))
    # 返回数据
    return send_request_ping_time, rawsocket, dst_addr


def reply_ping(send_request_ping_time, rawsocket, data_sequence, timeout=2):
    while True:
        # 开始时间
        started_select = time()
        # 实例化select对象，可读rawsocket，可写为空，可执行为空，超时时间
        what_ready = select([rawsocket], [], [], timeout)
        # 等待时间
        wait_for_time = (time() - started_select)
        # 没有返回可读的内容，判断超时
        if not what_ready[0]:  # Timeout
            return -1
        # 记录接收时间
        time_received = time()
        # 设置接收的包的字节为1024
        received_packet, addr = rawsocket.recvfrom(1024)
        # 获取接收包的icmp头
        # print(icmp_header)
        icmp_header = received_packet[20:28]
        # 反转编码
        _type, code, checksum, packet_id, sequence = unpack(
            ">BBHHH", icmp_header
        )

        if _type == 0 and sequence == data_sequence:
            return time_received - send_request_ping_time

        # 数据包的超时时间判断
        timeout = timeout - wait_for_time
        if timeout <= 0:
            return -1


def ping(host):
    send, accept, lost = 0, 0, 0
    sumtime, short_time, longtime, avgtime = 0, 1000, 0, 0
    # todou icmp数据包的构建
    data_type = 8  # ICMP Echo Request
    data_code = 0  # must be zero
    data_checksum = 0  # "...with value 0 substituted for this field..."
    data_id = 0  # Identifier
    data_sequence = 1  # Sequence number
    payload_body = b'abcdefghijklmnopqrstuvwabcdefghi'  # data

    # 将主机名转ipv4地址格式，返回以ipv4地址格式的字符串，如果主机名称是ipv4地址，则它将保持不变
    dst_addr = socket.gethostbyname(host)
    # print("正在 Ping {0} [{1}] 具有 32 字节的数据:".format(host, dst_addr))
    for _i in range(0, 8):
        send = _i + 1
        # 请求ping数据包的二进制转换
        icmp_packet = request_ping(data_type, data_code, data_checksum, data_id, data_sequence + _i, payload_body)
        # 连接套接字,并将数据发送到套接字
        send_request_ping_time, rawsocket, addr = raw_socket(dst_addr, icmp_packet)
        # 数据包传输时间
        times = reply_ping(send_request_ping_time, rawsocket, data_sequence + _i)
        if times > 0:
            # print("来自 {0} 的回复: 字节=32 时间={1}ms".format(addr, int(times * 1000)))

            accept += 1
            return_time = int(times * 1000)
            sumtime += return_time
            if return_time > longtime:
                longtime = return_time
            if return_time < short_time:
                short_time = return_time
            sleep(0.7)
        else:
            lost += 1
            # print("请求超时。")

        if send == 8:
            # print("{0}的Ping统计信息:".format(dst_addr))
            # print("\t数据包：已发送={0},接收={1}，丢失={2}（{3}%丢失），\n往返行程的估计时间（以毫秒为单位）：\n\t最短={4}ms，最长={5}ms，平均={6}ms".format(
            # _i+1, accept, _i + 1 - accept, (_i + 1 - accept) / (_i + 1) * 100,  short_time, longtime, sumtime / send))
            return host, float((_i + 1 - accept) / (_i + 1) * 100), float(sumtime / send)


if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     sys.exit('Usage: ping.py <host>')
    # ping(sys.argv[1])

    i = input("请输入要ping的主机或域名\n")
    ping(i)
    # host='www.baidu.com'
    # ping(host)
