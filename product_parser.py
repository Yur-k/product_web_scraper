import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd
import os

class Scraper:
    def __init__(self, headers):
        self.session = requests.Session()
        self.session.headers = headers
        

    def load_page(self, url):
        result = self.session.get(url, headers=self.session.headers)
        result.raise_for_status()
        print(f'Loaded page - {url}')
        print(f'Status code- {result.status_code}')
        return result.text
    

    def read_html(self, html):
        with open(f'{html}', 'r', encoding="utf-8") as file:
            src = file.read()
        return src


    def get_soup_file(self, html_file):
        soup = BeautifulSoup(html_file, 'lxml')
        print('Got soup object')
        return soup


    def parse_all_url(self, soup_file, site_name: str, class_name: str):
        all_eligible_href = soup_file.find_all(class_=class_name)
        all_hrefs_dict = {item.text.strip() : site_name+item.get('href') for item in all_eligible_href}
        print('Parsed all target url')
        return all_hrefs_dict


    def get_html_all_target_urls(self, dict_urls):
        # Retutn list of lots html pages
        #dict_of_html = {text : requests.get(href, headers=self.session.headers).text for text in dict_urls.keys() for href in dict_urls.values()}
        dict_of_html = {}
        count = len(dict_urls)+1
        for item in dict_urls:
            request = requests.get(dict_urls[item], headers=self.session.headers)
            src = request.text
            dict_of_html[item] = src
            time.sleep(3)
            count-=1
            print(f'{count} links left, got {item}')
        return dict_of_html


    def get_table_from_web(self, url_or_html):
        table = pd.read_html(url_or_html)
        return table


class Saver():

    def save_main_html_page(html_page, file_name='index'):
        with open(f'{file_name}.html', 'w', encoding="utf-8") as file:
            file.write(html_page)
            print(f'Saved html page {file_name}')

    def save_json(file_to_save, file_name='my_json'):
        with open(f'{file_name}.json', 'w', encoding='utf-8') as file:
            json.dump(file_to_save, file, indent=4, ensure_ascii=False)
            print(f'Saved json file - {file_name}')

    def save_html(html_file, file_name:str):
        with open(f'data/{file_name}.html', 'w', encoding="utf-8") as file:
            file.write(html_file)
            print(f'{file_name} saved')
    
    def save_csv(file, name:str):
        """ Save data frame to csv
        Args:
            file ([pandas.dataframe]): table data
            name (str): file name to save
        """
        file.to_csv('data/'+name)
        print(f"{name} saved to csv")



def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
    main_url = 'https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie'
    class_name_for_all_url = "mzr-tc-group-item-href"
    site_name = 'https://health-diet.ru'

    products = Scraper(headers)
    try:
        page = products.load_page(main_url)
    except Exception:
        print("Can't load the page")

    Saver.save_main_html_page(page, 'main_file')
    first_html = products.read_html('main_file.html')
    soup = products.get_soup_file(first_html)
    all_eligible_url = products.parse_all_url(soup, site_name=site_name, class_name=class_name_for_all_url)

    #html_dict = products.get_html_all_target_urls(all_eligible_url)
    os.mkdir('data')

    for name, url in all_eligible_url.items():
        try:
            df = products.get_table_from_web(url)
            Saver.save_csv(df[0], name)
            time.sleep(3)
        except Exception:
            print(f"Can't save {name}")
            continue

    
if __name__ == "__main__":
    main()
    