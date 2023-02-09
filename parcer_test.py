import requests
import json


CATALOG_ID_EXCEPTION = [2192, 130255, 61037, 4853, 12, 13, 14]


def get_child_catalog_wb(catalogs, catalogs_list):
    for catalog in catalogs:
        childs = catalog.get('childs')
        if childs and catalog['id'] not in CATALOG_ID_EXCEPTION:
            catalogs_list = get_child_catalog_wb(childs, catalogs_list)
        elif catalog['id'] not in CATALOG_ID_EXCEPTION:
            catalogs_list.append({
                'id': catalog['id'], 
                'name': catalog['name'],
                'parent': catalog['parent'],
                'shard': catalog.get('shard'),
                'query': catalog.get('query')
            })
    return catalogs_list


def get_catalog_wb():
    url = "https://static-basket-01.wb.ru/vol0/data/main-menu-ru-ru-v2.json"
    headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    data = response.json()
    catalogs_list = []
    return get_child_catalog_wb(data, catalogs_list)


def get_content(shard, query, low_price=0, top_price=0):
    headers = {'Accept': "*/*", 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    data_list = []
    for page in range(1, 101):
        print(f'Сбор позиций со страницы {page} из 100')
        url = f'https://catalog.wb.ru/catalog/{shard}/catalog?appType=1&curr=rub&dest=-1075831,-77677,-398551,12358499' \
              f'&locale=ru&page={page}&price={low_price * 100};{top_price * 100}' \
              f'®=0®ions=64,83,4,38,80,33,70,82,86,30,69,1,48,22,66,31,40&sort=popular&spp=0&{query}'
        response = requests.get(url, headers=headers)
        data = response.json()
        products = data['data']['products']
        if not products:
            print(f'Сбор данных завершен.')
            break
        data_list.extend(get_data_from_json(products))
    print(f'Собрана информация по {len(data_list)} позиций')
    return data_list


def get_data_from_json(products):
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
    catalogs = get_catalog_wb()
    # with open('wb_catalogs_data.json', 'w', encoding='UTF-8') as file:
    #     json.dump(catalogs, file, indent=2, ensure_ascii=False)
    #     print(f'Данные сохранены в wb_catalogs_data.json')
    """Раскоментировать если нужно сохранить список каталогов"""
    for catalog in catalogs:
        name = catalog['name']
        print(f'Загрузка данных из каталога {name}')
        result = get_content(catalog['shard'], catalog['query'])
        with open('wb_goods_data.json', 'a', encoding='UTF-8') as file:
            json.dump(result, file, indent=2, ensure_ascii=False)
            print(f'Данные раздела {catalog} сохранены в wb_goods_data.json')
