import re

file_name = 'names.txt'
with open(file_name, 'r') as file_obj:
    lines = file_obj.readline()  # считывание данных из файла
lines = re.findall(r'\w+', lines)  # парсинг имен
lines = sorted(lines)  # сортировка списка имен
sum_of_char = 0
sum_of_list = 0
index = 0
"""Произведение операций над каждым элементом списка по заданию"""
for line in lines:
    index += 1
    sum_of_char = 0
    line = line.upper()
    for char in line:
        sum_of_char += (ord(char) - 65 + 1)
    sum_of_list += (index + sum_of_char)
print(sum_of_list)  # Вывод суммы требуемой по заданию
