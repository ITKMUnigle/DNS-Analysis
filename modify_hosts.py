# -*- coding: utf-8 -*-
# !/usr/bin/python3
from os import name, remove, rename
from os.path import exists

if name == 'nt':
    path = r'C:\Windows\System32\drivers\etc\hosts'
elif name == 'posix':
    path = r'/etc/hosts'
else:
    path = ''
# path = r'C:\Users\suke\Desktop\hosts'
# path = r'hosts'
new_path = r'.tmp'
bak_path = r'.bak'


def add(host_list, del_others='N'):
    # host_list = [('www.sukeme.xyz', ['0.0.0.0', '1.1.1.1']), ...]
    if path == '':
        return 0, '仅支持linux与windows系统'
    try:
        with open(path, 'r+', encoding='utf-8') as f, open(path + new_path, 'w+', encoding='utf-8') as f2:
            data = f.readlines()  # 获取以行分割的列表
            old_domain, old_record, old_record_del, old_record_self, new_domain, new_record = 0, 0, 0, 0, 0, 0
            old_domain_list, old_domain_self_list, old_domain_del_list, old_domain_keep_list = [], [], [], []
            # 提取出已有的与要添加域名重复的项
            clash_data = [line for line in data for domain in (host[0] for host in host_list) if domain in line]
            for line in clash_data:  # 删去重复项
                old_record += 1
                domain = line.split(' ')[1]
                old_domain_list.append(domain)
                if '# by ipget' in line:
                    old_record_self += 1
                    old_domain_self_list.append(domain)
                    if line in data:
                        data.remove(line)
                    continue
                if domain in old_domain_del_list:
                    old_record_del += 1
                    if line in data:
                        data.remove(line)
                    continue
                if domain in old_domain_keep_list:
                    continue
                if del_others == 'Y':
                    old_recore_del_con = 'Y'
                else:
                    while 1:  # 确认该域名是否删除
                        old_recore_del_con = input('hosts文件中已存在域名%s且不是由本工具添加的，是否删除旧的记录？（Y/N）\n'
                                                   '不删除旧记录会使本域名后续添加的记录失效。（留空默认删除。）\n' % domain) \
                                             or "Y"
                        if old_recore_del_con in ['Y', 'N', 'y', 'n']:
                            break
                if old_recore_del_con in ['Y', 'y']:  # 执行删除
                    old_domain_del_list.append(domain)
                    old_record_del += 1
                    if line in data:
                        data.remove(line)
                else:  # 执行拷贝
                    old_domain_keep_list.append(domain)

            old_domain_list = list(set(old_domain_list))
            old_domain = len(old_domain_list)
            if old_domain:
                pass  # 引用一下，不然总是警告

            for host in host_list:  # 添加新记录
                new_domain += 1
                for ip in host[1]:
                    new_record += 1
                    new_ip = ip + ' ' + host[0] + ' # by ipget' + '\n'
                    data.append(new_ip)
            for line in data:
                f2.write(line)

        # 如果不存在备份则创建
        if exists(path + bak_path):
            remove(path)
        else:
            rename(path, path + bak_path)
        rename(path + new_path, path)

        return 1, "共添加%d个域名，%d条记录。其中%d条历史重复域名记录：%d条由本工具在之前添加，已全部清理。%d条其它来源记录，已删除%d条。" % (
            new_domain, new_record, old_record, old_record_self, old_record - old_record_self, old_record_del)
    except Exception as e:
        return 0, e


def recover(text):
    if path == '':
        return 0, '仅支持linux与windows系统'
    if text == 'recover':
        try:
            if exists(path + bak_path):
                if exists(path):
                    remove(path)
                rename(path + bak_path, path)
                return 1, '已恢复原hosts文件'
            else:
                return 0, '还未使用本工具修改过hosts'
        except Exception as e:
            return 0, e
    elif text == 'del':
        try:
            with open(path, 'r', encoding='utf-8') as f, open(path + new_path, 'w+', encoding='utf-8') as f2:
                data = f.readlines()  # 获取以行分割的列表
                clash_data = [line for line in data if '# by ipget' in line]
                old_record = len(clash_data)
                old_record_del = 0
                old_domain_list = []
                for line in clash_data:  # 删去添加项
                    domain = line.split(' ')[1]
                    if '.' in domain:
                        old_domain_list.append(domain)
                    if line in data:
                        old_record_del += 1
                        data.remove(line)
                for line1 in data:
                    f2.write(line1)
            remove(path)
            rename(path + new_path, path)
            old_domain_list = list(set(old_domain_list))
            old_domain = len(old_domain_list)
            return 1, '已清理本工具添加项：涉及%d个域名，%d条记录,已清理%d条。' % (old_domain, old_record, old_record_del)
        except Exception as e:
            return 0, e
    else:
        return 0, '未知错误，写错误提示好烦，就这样'


if __name__ == '__main__':
    # x = input("格式：add/del/change,0.0.0.0,www.sukeme.xyz")
    xx = [('www.sukeme.xyz', ['0.0.0.0', '1.1.1.1']), ('sdasdf.ccc', ['2.3.4.5', '23.43.43.55', '123.14.324.3'])]
    print('321\n%s' % add(xx)[1])
    print(add(xx)[1])
    # print(recover('recover'))
    # print(recover('del'))
    print(name)
