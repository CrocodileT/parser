from bs4 import BeautifulSoup
import requests
import csv
import re

def create_number(text):
    return  int(re.findall(r'.?(\d*)', text)[0])

def read_file(filename):
    with open(filename) as input_file:
        text = input_file.read()
    return text


#Класс необходимый для корректного выведения ошибки
class NotFound(Exception):
    pass

#Попытка подключения по url
def try_get(url):
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    else:
        raise ValueError(url + " not found, code: " + str(res.status_code))

all_products = list()

#По запросу(find) анализируем результаты поиска на каждой странице
def all_page(find, now_page, last_page):
    if now_page == last_page:
        return

    url_site = 'https://irecommend.ru/'
    key_word1 = 'srch?'
    #Если это не первая страница, то в url добавляется параметр page
    page = '' if now_page == 0 else 'page=' + str(now_page) + '&'
    key_word2 = 'query='
    add = '&op='
    #Т.к. сайт борется с ботами, пришлось сохранить hmtl код в файлы
    #text_file = read_file("scratch" + str(now_page) + '.html')
    #text = BeautifulSoup(text_file, features='lxml')

    #Если сайт даёт обращаться к себе, то можно использовать это
    text = BeautifulSoup(try_get(url_site + key_word1 + page + key_word2 + find + add), features='lxml')
    if now_page == 0:
        #Вообще-то можно попробовать и больше страниц обработать, но сайт блочит все это дело
        last_page = min(5,int(text.find('li', {'class': 'pager-last'}).find('a').text) - 1)
        #last_page = 2
    #Далее идет обработка html тэгов
    products = text.find_all('div', {'class': 'ProductTizer plate teaser-item'})

    for product in products:
        title = product.find('div', {'class': 'title'})
        link = title.find('a').get('href')
        name = title.find('a').text

        average_rating = product.find('span', {'class': 'average-rating'})
        rating = average_rating.text

        total_votes = product.find('span', {'class': 'total-votes'})
        number = create_number(total_votes.text)

        extract = product.find('div', {'class': 'extract'})
        opinion = extract.find('a').text
        #Формируем таблицу данных о технике
        all_products.append([rating, number, opinion, name, url_site + link])

    all_page(find, now_page+1, last_page)


print("""Ввидите имя того, что нужно искать(телефон, телевизор, холодильник и т.д.)\n
P.S. чем конкретнее будет запрос, тем конкретнее будет результат\n
\tВвод:""", end = '')

find = input()
all_page(find, 0, 1)
#Сортируем словарь техники
all_products.sort(reverse=True)
with open("result.csv", 'w') as output_file:
    writer = csv.writer(output_file)
    for product in all_products:
        writer.writerow(product)

