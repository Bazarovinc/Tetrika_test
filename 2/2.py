import re

file_name = 'hits.txt'
with open(file_name, 'r') as file_obj:
    lines = file_obj.readlines()  # чтиние данных из файла
ips = {}
for line in lines:
    ip = re.search(r'\d+.\d+.\d+.\d+', line)  # парсинг IP
    ip = ip.group()
    """занесение IP в словарь с подсчетом того, сколько раз один и тот же IP встречается"""
    if ip in ips:
        ips[ip] += 1
    else:
        ips[ip] = 0
sort_ips = sorted(ips, key=ips.get, reverse=True)  # сортировка словаря по значениям (сколько раз встречается IP)
"""Вывод первых пяти наиболее встречающихся IP-адресов"""
for i in range(5):
    print(sort_ips[i])
