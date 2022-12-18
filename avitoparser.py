import requests     # что бы работать с интернетом
from bs4 import BeautifulSoup
# import самописного класса для быстрой работы с БД
from mysql_wrapper import UseDataBase
from mysql_wrapper import UsePoolConnectionToDB
import numpy as np
import multiprocessing as multi


base_url = 'https://www.avito.ru/'
page = '?p='
page_num = '1'
query = '&q='

pool_db = 0     # глобальная переменная для пула БД переназначится внутри main()


def get_url(city, search):
    url = base_url + city + page + page_num + query + search
    return url


def get_html(url): # возвращает html код с запрашиваемой страницы    
    r = requests.get(url).text
    return r


def get_total_pages(html): # возвращает номер последней страницы  -> int
    soup = BeautifulSoup(html, "lxml")
    pages = soup.find('div', class_='pagination-pages').find_all('a', class_='pagination-page')[-1].get('href')
    total_pages = pages.split('=')[1].split('&')[0]
    return int(total_pages)


def get_all_pages_urls(city, search, total_pages):  # добавляет url всех страниц в список, сработает если нужно парсить номера телефонов (мультипроцессингом)
    all_pages_urls = []
    for i in range(1, total_pages+1):
        url = base_url + city + page + str(i) + query + search
        all_pages_urls.append(url)
    return all_pages_urls


def chunks(n, page_list):       # делит содержимое списка с url всех страницы на несколько списков
    return np.array_split(page_list,n)      # вернет массив внутри которого еще несколько массивовб равные количеству ядер


def parsing(links):
    try:
        cursor = pool_db.create_cursor()
        print('Connection opened')
        for link in links:
            html = get_html(link)
            get_page_data(html, cursor)
    except:
        # тут костыль
        print("Error while connecting to MySQL using Connection pool")
        try:
            cursor = pool_db.create_cursor()
            print('Connection opened')
            for link in links:
                html = get_html(link)
                get_page_data(html, cursor)
        except:
            print("Error #2")
    finally:
        pool_db.close()
        print("MySQL connection is closed")


def full_parsing(city_input, search_input):
    city = city_input.replace(' ', '_').lower()
    search = search_input.replace(' ', '+')  
    url = get_url(city, search)
    total_pages = get_total_pages(get_html(url))
    cpus = multi.cpu_count()

    if total_pages < cpus:
        cpus = total_pages

    global pool_db
    pool_db = UsePoolConnectionToDB('parserpool', cpus)
    workers = []

    all_pages_urls = get_all_pages_urls(city, search, total_pages)
    page_bins = chunks(cpus, all_pages_urls)

    parser_db = UseDataBase()
    parser_db.create_connection()
    parser_db.query_insert('truncate table parse')
    parser_db.close()

    for cpu in range(cpus):
        worker = multi.Process(name=str(cpu),target=parsing,args=(page_bins[cpu],))
        workers.append(worker)
        worker.start()

    for worker in workers:
        worker.join()

    return True


def parsing_without_phones(city_input, search_input):
    city = city_input.replace(' ', '_').lower()
    search = search_input.replace(' ', '+')  
    url = get_url(city, search)
    total_pages = get_total_pages(get_html(url))

    parser_db = UseDataBase()
    cursor = parser_db.create_connection()
    parser_db.query_insert('truncate table parse')

    for i in range(1, total_pages + 1):
        url = base_url + city + page + str(i) + query + search
        get_page_data(get_html(url), cursor, False)

    parser_db.close()


def get_page_data(html, cursor, phone=True): # парсит страницу и импортирует данные в БД
    soup = BeautifulSoup(html, 'lxml')
    ads = soup.find('div', class_ = 'js-catalog_after-ads').find_all('div', class_ = 'item_table')
    _SQL = ''' insert into parse
            (title, price, time, place, phone, url)
            values
            (%s, %s, %s, %s, %s, %s) '''

    if phone:
        for ad in ads:
            try:
                title = ad.find('div', class_ = 'description').find('div', class_='item_table-header').find('h3').text.strip()
            except:
                title = 'Заголовок не задан'

            try:
                price = ad.find('div', class_ = 'description').find('div', class_='item_table-header').find('div',class_='about').text.replace('₽', '').strip()
            except:
                price = 'Цена не указана'

            try:
                time = ad.find('div', class_ = 'description').find('div', class_='data').find('div').text.strip()
            except:
                time = 'Время размещения неизвестно'      

            try:
                data = ad.find('div', class_ = 'description').find('div', class_='data').find_all('p')
                if len(data) <= 1:
                    place = 'Район не указан'
                else:
                    place = data[-1].text.strip()
            except:
                place = 'Район не указан'

            try:
                url = base_url + ad.find('div', class_ = 'description').find('div', class_='item_table-header').find('h3').find('a').get('href').strip()
            except:
                url = 'Невозможно прочитать URL'

            try:
                tel = get_tel(url)
            except:
                tel = 'Не удалось распознать номер телефона'
            # импорт в БД
            cursor.execute(_SQL, (title, price, time, place, tel, url))

    else:
        for ad in ads:
            try:
                title = ad.find('div', class_ = 'description').find('div', class_='item_table-header').find('h3').text.strip()
            except:
                title = 'Заголовок не задан'

            try:
                price = ad.find('div', class_ = 'description').find('div', class_='item_table-header').find('div',class_='about').text.replace('₽', '').strip()
            except:
                price = 'Цена не указана'

            try:
                time = ad.find('div', class_ = 'description').find('div', class_='data').find('div').text.strip()
            except:
                time = 'Время размещения неизвестно'      

            try:
                data = ad.find('div', class_ = 'description').find('div', class_='data').find_all('p')
                if len(data) <= 1:
                    place = 'Район не указан'
                else:
                    place = data[-1].text.strip()
            except:
                place = 'Район не указан'

            try:
                url = base_url + ad.find('div', class_ = 'description').find('div', class_='item_table-header').find('h3').find('a').get('href').strip()
            except:
                url = 'Невозможно прочитать URL'

            tel = ''
            # импорт в БД
            cursor.execute(_SQL, (title, price, time, place, tel, url))


def get_tel(url):
    url = url.replace('www', 'm').replace('ru//', 'ru/')
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    phone_number = soup.find('a', class_ = "_2MOUQ").get('href').replace('tel:', '')
    return phone_number