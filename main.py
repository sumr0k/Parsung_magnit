import json
import random
import time
from random import choice

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from proxy_good import proxies

count_product = 0
previous_count_product = 1
page = 0
result_list = []

while True:
    if previous_count_product == count_product:
        print(f'Работа завершена!\nВ файл {file.name} записано {count_product} товара со скидкой ')
        break
    # товары динамически подгружаются по 50 на странице
    # Магнит Экстра
    url = "https://magnit.ru/promo/"

    ua = UserAgent()
    fake_ua = {
        'user-agent': ua.random,
        'x-requested-with': 'XMLHttpRequest'
    }

    data = {
        "page": page,
        "format[]": 'me'
    }
    cookies = {'mg_geo_id': '1923'}  # id города (Волгоград, в моем случае)

    pr = choice(proxies)  # дергаем случайное прокси в формате 'host:port'
    proxy = {
        'http': f"{pr}",
        'https': f"{pr}"
    }

    try:
        response = requests.get(url=url, headers=fake_ua, params=data, cookies=cookies, proxies=proxy, timeout=4)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
    except:
        proxies.remove(pr)
        print(f'ip {pr} - забанен, осталось {len(proxies)} рабочих')
    else:
        previous_count_product = count_product
        get_products_from_page = soup.find_all('a', {'class': 'card-sale card-sale_catalogue'})
        for product in get_products_from_page:

            try:
                sale = product.find('div', {'class': 'label label_sm label_mextra card-sale__discount'}).text
            except:
                try:  # Некоторые имеют отличный класс, что странно
                    sale = product.find('div', {'class': 'label label_sm label_family card-sale__discount'}).text
                except:  # Около 10% вообще не имеет div'a со скидкой. Вроде как это кулинария
                    continue

            old_price_integer = product.find('div', {'class': 'label__price label__price_old'}) \
                .find('span', {'class': 'label__price-integer'}).text  # старая цена - рубли
            old_price_decimal = product.find('div', {'class': 'label__price label__price_old'}) \
                .find('span', {'class': 'label__price-decimal'}).text  # старая цена - копейки

            sale_price_integer = product.find('div', {'class': 'label__price label__price_new'}) \
                .find('span', {'class': 'label__price-integer'}).text  # цена со скидкой - рубли
            sale_price_decimal = product.find('div', {'class': 'label__price label__price_new'}) \
                .find('span', {'class': 'label__price-decimal'}).text  # цена со скидкой - копейки

            name_product = product.find('div', {'class': 'card-sale__title'}).text
            href = f"https://magnit.ru{product['href']}"
            time_action_start = product.find('div', {'class': 'card-sale__date'}). \
                text.replace('\n', ' ').strip().replace('  ', ' ')
            count_product += 1
            # словарь под каждый товар
            result_json_product = {
                'Название товара': name_product,
                'Цена без скидки': f"{old_price_integer}.{old_price_decimal}",
                'Цена со скидкой': f"{sale_price_integer}.{sale_price_decimal}",
                'Процент скидки': sale,
                'Ссылка на товар': href,
                'Время проведения акции': time_action_start,
                '№': count_product
            }

            result_list.append(result_json_product)
        page += 1  # считаем страницы, чтоб указывать их в качестве параметра
        time.sleep(random.randint(3, 5))  # спим перед следующей страницей
    try:
        with open('res.json', 'w', encoding='utf-8-sig') as file:
            json.dump(result_list, file, indent=4, ensure_ascii=False)
            print(f'{len(result_list)} товара записано')
    except:
        print("Ошибка записи")
