import random
from warnings import WarningMessage
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import quote
import pandas as pd
import ssl
from selenium import webdriver
import chromedriver_autoinstaller
import subprocess
from selenium.webdriver.chrome.options import Options
import time
import os
import warnings


class Header:
    DEFAULT_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
    HEADERS_LIST = [
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; x64; fr; rv:1.9.2.13) Gecko/20101203 Firebird/3.6.13',
        'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
        'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
        'Mozilla/5.0 (Windows NT 5.2; RW; rv:7.0a1) Gecko/20091211 SeaMonkey/9.23a1pre'
        ]
    RANDOM_HEADER = {'User-Agent': random.choice(HEADERS_LIST)}

    
    def __init__(self, head_option = 'default'):
        if head_option == 'default':
            self._header = Header.DEFAULT_HEADER
        elif head_option == 'random':
            self._header = Header.RANDOM_HEADER
            warnings.warn('"Random Header" is suitable for SHNaverNewsMiner and BlogMiner only.')
        else:
            raise ValueError("head_option should be either default or random (default value is recommended)")

    
    @property
    def header(self):
        return self._header



class Driver(Header):

    def __init__(self, url, install=False, head_option='default', driver=None):
        super().__init__(head_option)
        self._url = url
        self._install = install
        self._driver = driver
        if self._install == False:
            options = webdriver.ChromeOptions()
            options.add_argument('user-agent={}'.format(self.header['User-Agent']))
            self._driver = webdriver.Chrome('D:\\chromedriver.exe', options=options)
            #self._driver.maximize_window()
            #self._driver.get(url)
            
        elif self._install == True:
            subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"')
            option = Options()
            option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
            try:
                self._driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=option)
            except:
                chromedriver_autoinstaller.install(True)
                self._driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=option)
        self._driver.maximize_window()
        self._driver.get(self._url)


    def scroller(self):
        prev_height = self._driver.execute_script('return document.body.scrollHeight')
        while True:
            self._driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(1)
            curr_height = self._driver.execute_script('return document.body.scrollHeight')
            if curr_height == prev_height:
                break
            prev_height = curr_height
        print('scrolling completed')


    @property
    def driver(self):
        return self._driver

    @property
    def install(self):
        return self._install
    
    @property
    def url(self):
        return self._url



class Source(Driver):

    def __init__(self, source='insta'):
        self._source = source
        if source=='insta':
            self._loc_char = 'div'
            self._loc_class = '_aabd _aa8k _aanf'
            self._connect_url = 'https://www.instagram.com'
        elif source=='twitter':
            self._loc_char = 'a'
            self._loc_class = "css-4rbku5 css-18t94o4 css-901oao r-1bwzh9t r-1loqt21 r-xoduu5 r-1q142lx r-1w6e6rj r-37j5jr r-a023e6 r-16dba41 r-9aw3ui r-rjixqe r-bcqeeo r-3s2u2q r-qvutc0"
            self._connect_url = 'https://twitter.com'
        else:
            raise ValueError('Source should be either "insta" or "twitter"')

    
    def get_source(self, scroll_length=5):
        feed_url_list = []
        self._scroll_length = scroll_length
        for x in range(0, self._scroll_length):
            self._driver.execute_script('window.scrollTo(0, {})'.format(1200*x))
            html = self._driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all(self._loc_char, {'class': self._loc_class})
            for link in links:
                if self._source=='insta':
                    feed_tag = link.find('a').get('href')
                elif self._source=='twitter':
                    feed_tag = link.get('href')
                feed_url = self._connect_url + feed_tag
                feed_url_list.append(feed_url)
            time.sleep(2)
        temp = []
        for feed in feed_url_list:
            if feed not in temp:
                temp.append(feed)
        dict_feed = {'source': temp}
        feed_url_df = pd.DataFrame(dict_feed)
        feed_url_df.to_csv('source.csv', encoding='utf-8-sig', index=False)

    
    def extract_source(self, start=None, end=None, save_num=1):
        self._save_num = str(save_num)
        if type(start) != int:
            raise TypeError("Start value should be integer")
        elif start < 0:
            raise ValueError("Invalid Start number")
        else:
            self._start = start
        
        if type(end) != int:
            raise TypeError("End value should be integer")
        elif end < 1:
            raise ValueError("Invalid End number")
        elif end < start:
            raise ValueError("End number should be larger than Start number")
        else:
            self._end = end
        data_ = pd.read_csv('source.csv')
        self._feed_url_list = [link for link in data_.source]
        self._driver.switch_to.window(self._driver.window_handles[0])


    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def save_num(self):
        return self._save_num    

    @property
    def scroll_length(self):
        return self._scroll_length

    @property
    def loc_char(self):
        return self._loc_char

    @property
    def loc_class(self):
        return self._loc_class

    @property
    def source(self):
        return self._source

    @property
    def connect_url(self):
        return self._connect_url

    @property
    def feed_url_list(self):
        return self._feed_url_list



def preprocessor(kind='insta'):
        if kind=='insta':
            kind = 'insta'
        elif kind=='twitter':
            kind='twitter'
        else:
            raise ValueError('"kind" should be either "insta" or "twitter"')
        master_df = pd.DataFrame()
        for file in os.listdir(f"D:\\Data_Repository\\{kind}\\{kind}_raw"):
            if file.endswith("csv"):
                master_df = master_df.append(pd.read_csv(f"D:\\Data_Repository\\{kind}\\{kind}_raw\\" + file))
        master_df.reset_index(drop=True, inplace=True)
        master_df.drop_duplicates(subset=['main_text'], inplace=True)
        master_df = master_df[master_df['main_text'].notna()]
        master_df = master_df[master_df['main_text']!='']
        master_df = master_df[master_df['date'].notna()]
        master_df = master_df[master_df['date']!='']        
        master_df.reset_index(drop=True, inplace=True)
        return master_df