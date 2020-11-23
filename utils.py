import csv
import pandas


def write_header(csv_file_name, fieldnames):
    with open('csv/' + csv_file_name + '.csv', 'w+', encoding='utf-8') as csv_file:
        fieldnames = fieldnames
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()


def write2csv(csv_file_name, item, fieldnames):
    with open('csv/' + csv_file_name + '.csv', 'a+', encoding='utf-8') as csv_file:
        fieldnames = fieldnames
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writerow(item)


def csv2xlsx(csv_file_name, xlsx_file_name=None):
    csv_file = pandas.read_csv('csv/' + csv_file_name + '.csv', encoding='utf-8')
    if xlsx_file_name is not None:
        csv_file.to_excel('xlsx/' + xlsx_file_name + '.xlsx', sheet_name='results')
    csv_file.to_excel('xlsx/' + csv_file_name + '.xlsx', sheet_name='results')
