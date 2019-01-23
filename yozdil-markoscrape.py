#!/usr/bin/env python3

import datetime
import json
import markovify
import re
import requests
import time
from bs4 import BeautifulSoup

now = datetime.datetime.now()
current_month = now.month
months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
years = ['2015', '2016', '2017', '2018', '2019']
headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

hurriyet_urls = []
hurriyet_articles = []
sozcu_urls = []
sozcu_articles = []

input_file1 = 'hurriyet_yozdil_articles.txt'
input_file2 = 'sozcu_yozdil_articles.txt'
merged_file = 'merged_articles.txt'

def sozcu_fetch_urls():
    fetched_urls = []

    for year in years:
        for month in months:
            try:
                if (year == '2019' and (month == (current_month + 1))):
                    break
                
                print(month + '/' + year)
                r = requests.post('https://www.sozcu.com.tr/kategori/yazarlar/yilmaz-ozdil', 
                        headers=headers,
                        data = {'month':month,
                                'queryyear':year})

                soup = BeautifulSoup(r.text, 'html.parser')
                soup = soup.find("ul", {"class": "old-list"})
                links = soup.find_all('a')

                for link in links:
                    fetched_urls.append(link['href'])

            except Exception as error_mes:
                print(error_mes)
                print('Error was captured but program will continue to work!')
                continue

    return fetched_urls

def sozcu_fetch_articles(sozcu_urls):
    fetched_articles = []

    for url in sozcu_urls:
        try:
            print(url)
            r = requests.get(url, headers=headers)
            
            soup = BeautifulSoup(r.text, 'html.parser')
            soup = soup.find_all(type="application/ld+json")[3].string

            ld_json = json.loads(soup)
            article_body = ld_json['articleBody']
            fetched_articles.append(article_body)

        except Exception as error_mes:
            print(error_mes)
            print('Error was captured but program will continue to work!')
            continue

    return fetched_articles

def s_write_to_file(articles):
    with open('sozcu_yozdil_articles.txt', 'a') as f:
        for article in articles:
            f.write(article)

def hurriyet_fetch_urls():
    fetched_urls = []
    
    for page in range(1, 257):
        try:
            r = requests.get('https://www.hurriyet.com.tr/yazarlar/yilmaz-ozdil/?p=' + str(page), 
                            headers=headers)

            print('https://www.hurriyet.com.tr/yazarlar/yilmaz-ozdil/?p=' + str(page))
            soup = BeautifulSoup(r.text, 'html.parser')
            soup = soup.find_all("a", {"class": "title"})

            for link in soup:
                fetched_urls.append('https://www.hurriyet.com.tr' + link['href'])

        except Exception as error_mes:
            print(error_mes)
            print('Error was captured but program will continue to work!')
            continue

    return fetched_urls

def hurriyet_fetch_articles(hurriyet_urls):
    fetched_articles = []
    i = 0

    for url in hurriyet_urls:
        try:
            print(url)
            r = requests.get(url, headers=headers)
            
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find("div", {"class": "article-content news-description"})
            text = soup.find("div", {"class": "article-content news-text"})

            article_title = title.string
            article_body = str(text.contents[0]).replace('<p>', '\n').replace('</p>', '\n') \
            .replace('</strong>', '').replace('<strong>', '') \
            .replace('<br>', '\n').replace('<br/>', '\n') \
            .replace('</i>', '').replace('<i>', '') \
            .replace('<em>', '').replace('</em>', '') \
            .replace('</b>', '').replace('<b>', '')

            if (article_title is None):
                article_title = ''
            if (article_body is None):
                continue

            i += 1
            print(i)
            print(article_title)
            print(article_body)

            fetched_articles.append(article_title + '\n' + article_body)

        except Exception as error_mes:
            print(error_mes)
            print('Error was captured but program will continue to work!')
            continue

    return fetched_articles

def h_write_to_file(articles):
    with open('hurriyet_yozdil_articles.txt', 'a') as f:
        for article in articles:
            f.write(article)

def merge_normalize_files(input_file1, input_file2):
    with open(input_file1) as f1:
        data1 = f1.read()
        with open(input_file2) as f2:
            data2 = f2.read()
            merged_data = data1 + '\n' + data2
            merged_data = merged_data.replace('&amp;#8211;', '-') \
            .replace('&amp;#8230;', '...') \
            .replace('!.', '!') \
            .replace('?.', '?') \
            .replace('&amp;amp;', '&') \
            .replace('*** ', '\n***\n\n') \
            .replace('* ', '\n***\n\n') \
            .replace('/', '')

            merged_data = re.sub('<[^<]+?>', '', merged_data) # Remove HTML tags.
            merged_data = re.sub('(<!--.*?-->)', '', merged_data) # Remove HTML comments.

            with open(merged_file, 'w') as f3:
                f3.write(merged_data)

def markov_model_from_file(merged_file):
    with open(merged_file) as f:
        file_content = f.read()

    text_model = markovify.Text(file_content)

    for _ in range(10):
        generated_sentence = text_model.make_sentence()
        if (generated_sentence is not None):
            print(generated_sentence)

if __name__ == '__main__':
    hurriyet_urls = hurriyet_fetch_urls()
    hurriyet_articles = hurriyet_fetch_articles(hurriyet_urls)
    h_write_to_file(hurriyet_articles)

    sozcu_urls = sozcu_fetch_urls()
    sozcu_articles = sozcu_fetch_articles(sozcu_urls)
    s_write_to_file(sozcu_articles)

    merge_normalize_files(input_file1, input_file2)
    
    markov_model_from_file(merged_file)

