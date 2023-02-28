import requests
import json
import logging
import time


CATALOG_ID_EXCEPTION = [2192, 130255, 61037, 4853, 12, 13, 14, 128297, 128313, 128604]
HEADERS = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def get_data_from_wb(url):
    retry_counter = 0
    while retry_counter < 5:
        try:
            response = requests.get(url, headers=HEADERS)
            break
        except:
            time.sleep(3)
            retry_counter += 1
            logger.error(f'Ошибка доступа к ресурсу, попытка подключения №{retry_counter}')
            return None
    if response.status_code != 200:
        logger.error(f'Данные не загружены, сервер вернул код {response.status_code}')
        return None
    return response


def get_child_catalog_wb(catalogs, catalogs_list, full_name=''):
    for catalog in catalogs:
        parent_name = full_name
        childs = catalog.get('childs')
        if childs and catalog['id'] not in CATALOG_ID_EXCEPTION:
            parent_name = parent_name + ' > ' + catalog['name']
            catalogs_list = get_child_catalog_wb(childs, catalogs_list, parent_name)
        elif catalog['id'] not in CATALOG_ID_EXCEPTION:
            catalogs_list.append({
                'id': catalog['id'], 
                'name': parent_name + ' > ' + catalog['name'],
                'parent': catalog['parent'],
                'shard': catalog.get('shard'),
                'query': catalog.get('query')
            })
    return catalogs_list


def get_catalog_wb():
    logger.info('Загрузка списка каталогов')
    url = "https://static-basket-01.wb.ru/vol0/data/main-menu-ru-ru-v2.json"
    catalogs_list = []
    response = get_data_from_wb(url)
    if not response:
        logger.info('Список каталогов не загружен')
        return catalogs_list
    data = response.json()
    catalogs_list = get_child_catalog_wb(data, catalogs_list)
    logger.info('Список каталогов загружен')
    return catalogs_list


def get_goods_wb(shard, query, low_price=1000, top_price=1200):
    data_list = []
    for page in range(1, 101):
        url = f'https://catalog.wb.ru/catalog/{shard}/catalog?appType=1&curr=rub&dest=-1075831,-77677,-398551,12358499' \
              f'&locale=ru&page={page}&priceU={low_price * 100};{top_price * 100}&' \
              f'®=0®ions=64,83,4,38,80,33,70,82,86,30,69,1,48,22,66,31,40&sort=popular&spp=0&{query}'
        response = get_data_from_wb(url)
        if not response:
            logger.info(f'Страница {page} не загружена')
            continue
        
        data = response.json()
        products = data['data']['products']
        if not products:
            logger.info(f'Сбор данных завершен на странице {page - 1}')
            break
        data_list.extend(get_goods_from_json(products))

    logger.info(f'Собрана информация по {len(data_list)} позиций')
    return data_list


def get_goods_from_json(products):
    data_list = []
    for item in products:
        item_id = item['id']
        name = item['name']
        try:
            price = item['salePriceU'] // 100
        except:
            price = 0
        data_list.append({
            'id': item_id,
            'name': name,
            'price': price
        })
    return data_list


if __name__ == '__main__':
    logger= logging.getLogger()
    logger.setLevel(logging.INFO) 
    handler = logging.FileHandler('parcer_log.log', 'w', 'utf-8') 
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s') 
    handler.setFormatter(formatter) 
    logger.addHandler(handler)

    catalogs= get_catalog_wb()
    catalog_count = 0
    if catalogs:
        with open('wb_catalogs_data.json', 'w', encoding='UTF-8') as file:
            json.dump(catalogs, file, indent=2, ensure_ascii=False)
        for catalog in catalogs:
            catalog_count += 1
            name = catalog['name']
            logger.info(f'Загрузка товаров из каталога № {catalog_count} всего - '
                        f'{len(catalogs)} имя: {name}')
            print(f'Загрузка товаров из каталога № {catalog_count} всего - '
                  f'{len(catalogs)} имя: {name}')
            result = get_goods_wb(catalog['shard'], catalog['query'])
            with open('wb_goods_data.json', 'a', encoding='UTF-8') as file:
                json.dump(result, file, indent=2, ensure_ascii=False)
                logger.info(f'Данные каталога {name} сохранены')
