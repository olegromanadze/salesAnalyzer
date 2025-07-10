import csv
from datetime import datetime
from collections import namedtuple, defaultdict
import json

Sale = namedtuple('Sale', ['order_id', 'product_name', 'quantity', 'unit_price', 'order_date'])

def parse_row(row):
    try:
        order_id = int(row['order_id'])
        product_name = row['product_name'].strip()
        quantity = int(row['quantity'])
        unit_price = float(row['unit_price'])
        order_date = datetime.strptime(row['order_date'], '%Y-%m-%d').date()
    except (KeyError, ValueError):
        return None
    if quantity <= 0 or unit_price <= 0:
        return None
    return Sale(order_id, product_name, quantity, unit_price, order_date)

def read_sales(file_path):
    sales = []
    try:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sale = parse_row(row)
                if sale:
                    sales.append(sale)
    except FileNotFoundError:
        print(f'Error: файл не найден: {file_path}')
    return sales

def aggregate_sales(sales):
    by_product = defaultdict(int)
    by_date = defaultdict(float)
    for s in sales:
        by_product[s.product_name] += s.quantity
        by_date[s.order_date] += s.quantity * s.unit_price
    return by_product, by_date

def write_reports(by_product, by_date):
    # JSON-отчет для продуктов
    with open('product_report.json', 'w', encoding='utf-8') as f:
        json.dump(by_product, f, ensure_ascii=False, indent=2)
    # CSV-отчет для ежедневной выручки
    with open('daily_revenue.csv', 'w', encoding='utf-8') as f:
        f.write('date,revenue\n')
        for date, rev in sorted(by_date.items()):
            f.write(f'{date},{rev:.2f}\n')

def main():
    sales = read_sales('sales200_.csv')
    print(f'Прочитано {len(sales)} валидных записей.')
    by_product, by_date = aggregate_sales(sales)

    # Вывод топ-3
    top3 = sorted(by_product.items(), key=lambda x: x[1], reverse=True)[:3]
    print("Топ-3 продуктов:")
    for name, qty in top3:
        print(f"{name}: {qty}")

    # День с максимальной выручкой
    best_day, max_rev = max(by_date.items(), key=lambda x: x[1])
    print(f"\nМаксимальная выручка {max_rev} — {best_day}")

    write_reports(by_product, by_date)

if __name__ == '__main__':
    main()