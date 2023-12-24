from selenium import webdriver
import chromedriver_autoinstaller
import subprocess
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import unicodedata
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import time
from ..sh_utils1 import Driver, Source, Header, preprocessor
import os
import random
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import quote #인코딩 utf8로 변환을 위해
import pandas as pd
import numpy as np
import ssl
import requests
from bs4 import BeautifulSoup
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import pandas as pd
import numpy as np
import unicodedata
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import quote


class SHTwitterMiner(Source, Driver):

    def __init__(self, query, start_date='2021-09-01', end_date='2022-09-01', install=False, head_option='default', driver=None):
        self._query = query
        self._start_date = start_date
        self._end_date = end_date
        self._url = f'https://twitter.com/search?f=live&q={self._query}%20until%3A{self._end_date}%20since%3A{self._start_date}&src=typed_query'
        Driver.__init__(self, self._url, install, head_option, driver=None)
        Source.__init__(self, source='twitter')
        time.sleep(5)
        self._driver.switch_to.window(self._driver.window_handles[0])

    
    def extract(self, start=None, end=None, save_num=1):
        self.extract_source(start, end, save_num)
        account_list = []
        date_list = []
        main_text_list = []
        link_list = []
        self._driver.switch_to.window(self._driver.window_handles[0])

        for x in self._feed_url_list[self._start:self._end]:
            url = x
            self._driver.execute_script(f"window.open('{url}');")
            time.sleep(4)
            self._driver.switch_to.window(self._driver.window_handles[1])
            try:
                #accounts
                account = self._driver.find_element(By.CLASS_NAME, 'css-1dbjc4n.r-1awozwy.r-18u37iz.r-1wbh5a2.r-dnmrzs').text
                account = unicodedata.normalize('NFC', account)
            except:
                account = ''
            try:
                #dates
                #date = driver.find_element_by_css_selector('span.css-901oao.css-16my406.r-poiln3.r-bcqeeo.r-qvutc0').text
                #date = driver.find_element(By.CSS_SELECTOR, '#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div.css-1dbjc4n.r-kemksi.r-1kqtdi0.r-1ljd8xs.r-13l2t4g.r-1phboty.r-1jgb5lz.r-11wrixw.r-61z16t.r-1ye8kvj.r-13qz1uu.r-184en5c > div > section > div > div > div:nth-child(1) > div > div > div > article > div > div > div > div:nth-child(3) > div.css-1dbjc4n.r-1r5su4o > div > div.css-901oao.r-1bwzh9t.r-37j5jr.r-a023e6.r-16dba41.r-rjixqe.r-1b7u577.r-bcqeeo.r-qvutc0 > a:nth-child(1) > span').text
                date = self._driver.find_element(By.CLASS_NAME, 'css-4rbku5.css-18t94o4.css-901oao.css-16my406.r-1bwzh9t.r-1loqt21.r-poiln3.r-bcqeeo.r-qvutc0').text
                date = unicodedata.normalize('NFC', date)
            except:
                date= ''
            
            try:
                #maintext
                #main_text = driver.find_element(By.CSS_SELECTOR, '#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div.css-1dbjc4n.r-kemksi.r-1kqtdi0.r-1ljd8xs.r-13l2t4g.r-1phboty.r-1jgb5lz.r-11wrixw.r-61z16t.r-1ye8kvj.r-13qz1uu.r-184en5c > div > section > div > div > div:nth-child(1) > div > div > div > article > div > div > div > div:nth-child(3) > div:nth-child(1)').text
                main_text = self._driver.find_element(By.CLASS_NAME, 'css-901oao.r-1nao33i.r-37j5jr.r-1blvdjr.r-16dba41.r-vrz42v.r-bcqeeo.r-bnwqim.r-qvutc0').text
                main_text = unicodedata.normalize('NFC', main_text)
            except:
                main_text= ''
            
            #link
            link_list.append(url)
            
            account_list.append(account)
            date_list.append(date)
            main_text_list.append(main_text)
            
            
            time.sleep(4)
            self._driver.close()
            time.sleep(2)
            self._driver.switch_to.window(self._driver.window_handles[0])
        feed_dict = {'account': account_list, 'link':link_list, 'main_text': main_text_list, 'date': date_list}
        twitter_df = pd.DataFrame(feed_dict)
        self._tweet = twitter_df
        twitter_df.to_csv(f"D:\\Data_Repository\\twitter\\twitter_raw\\{self._save_num}.csv",  encoding='utf-8-sig', index=False)
        print("Mining Completed")
        return twitter_df

    
    def preprocessor(self):
        master_df = preprocessor(kind='twitter')
        master_df['date'] = master_df['date'].apply(lambda x: x.split("·")[1].strip())
        master_df['date'] = pd.to_datetime(master_df['date'], format="%Y년 %m월 %d일")
        master_df.reset_index(drop=True, inplace=True)
        master_df['text'] = master_df['main_text']
        master_df.drop(columns=['account', 'link', 'main_text'], inplace=True)
        master_df.reset_index(drop=True, inplace=True)
        master_df.to_csv("D:\\Data_Repository\\twitter\\twitter_preprocessed\\twitter.csv", encoding="utf-8-sig", index=False)
        self._preprocessed_tweet = master_df
        return master_df
    
    @property
    def query(self):
        return self._query

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    @property
    def tweet(self):
        return self._tweet

    @property
    def preprocessed_tweet(self):
        return self._preprocessed_tweet