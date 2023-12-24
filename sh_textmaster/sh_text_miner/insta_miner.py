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


class SHInstaMiner(Source, Driver):

    def __init__(self, query, userid, userpw, install=False, head_option='default', driver=None):
        if len(re.findall(' ', query))==0:
            self._query = quote(query)
        elif len(re.findall(' ', query))!=0:
            raise ValueError("No spacing allowed for query")
        self._userid = userid
        self._userpw = userpw
        loginURL = 'https://www.instagram.com/accounts/login/'
        Driver.__init__(self, loginURL, install, head_option='default', driver=None)
        time.sleep(5)
        self._driver.find_element(By.NAME, "username").send_keys(userid)
        self._driver.find_element(By.NAME, "password").send_keys(userpw)
        time.sleep(5)
        self._driver.find_element(By.CSS_SELECTOR, "#loginForm > div > div:nth-child(3) > button > div").click()
        time.sleep(5)
        url = "https://www.instagram.com/explore/tags/{}/".format(self._query)
        self._driver.get(url)
        time.sleep(8)
        Source.__init__(self, source='insta')
        self._driver.switch_to.window(self._driver.window_handles[0])


    def extract(self, start=None, end=None, save_num=1):
        self.extract_source(start, end, save_num)
        account_list = []
        date_list = []
        main_text_list = []
        main_text_notag_list = []
        tag_list = []
        like_list = []
        hit_list = []
        feed_links_list = []
        place_list = []
        self._driver.switch_to.window(self._driver.window_handles[0])

        for x in self._feed_url_list[self._start:self._end]:
            url = x
            self._driver.execute_script(f"window.open('{url}');")
            self._driver.switch_to.window(self._driver.window_handles[1])
            time.sleep(5.5)
            #accounts
            try:
                account = self._driver.find_element(By.CLASS_NAME, '_aaqt').text
                account = unicodedata.normalize('NFC', account)
            except:
                account=''

            #dates
            try:
                dates = self._driver.find_element(By.CLASS_NAME, "_aaqe").get_attribute('datetime')
                dates = unicodedata.normalize('NFC', dates)
                dates = dates.split("T")[0]
            except:
                dates=''

            #text plus replies
            text_plus_reply_list = []
            try:
                texts = self._driver.find_elements(By.CLASS_NAME, '_a9zs')
                for text in texts:
                    text = text.text
                    text = unicodedata.normalize('NFC', text)
                    text_plus_reply_list.append(text)
                    text = ' '.join(text_plus_reply_list)
            except:
                text=''

            #text_notag
            try:
                #maintext_notag_pre = unicodedata.normalize('NFC', main_text)
                text_notag = re.sub('#[A-Za-z0-9가-힣]+', '', text).strip()
            except:
                text_notag=''

            #tags
            try:
                tags = re.findall('#[A-Za-z0-9가-힣]+', text)
                tags = ''.join(tags).replace('#',' ') # #제거
                tag_data = tags.split()
                tag_final = ', '.join(tag_data)
            except:
                tag_final=''

            #likes
            try:
                likes = self._driver.find_element(By.CLASS_NAME, '_aacl._aaco._aacw._aacx._aada._aade').text
                likes = unicodedata.normalize('NFC', likes)
            except:
                likes=''

            #hits
            try:
                hits = self._driver.find_element(By.CLASS_NAME, '_aauv').text
                hits = unicodedata.normalize('NFC', hits)
                hits
            except:
                hits=''
                
            #place
            try:
                place = self._driver.find_element(By.CLASS_NAME, '_aaql').text
                place = unicodedata.normalize('NFC', place)
            except:
                place = ''
                
            
            # insta_df.loc[idx] = [account, dates, main_text, maintext_notag, tag_final, likes, hits]
            # idx += 1
            account_list.append(account)
            date_list.append(dates)
            main_text_list.append(text)
            main_text_notag_list.append(text_notag)
            tag_list.append(tag_final)
            like_list.append(likes)
            hit_list.append(hits)
            feed_links_list.append(url)
            place_list.append(place)
            
            #time.sleep(3)
            #time.sleep(1.5)
            self._driver.close()
            time.sleep(2)
            self._driver.switch_to.window(self._driver.window_handles[0])
        dict_ = {'feed_link': feed_links_list, 'account': account_list, 'date': date_list, 
                'main_text': main_text_list, 'main_text_notag': main_text_notag_list,
                'place': place_list, 'tags': tag_list, 'likes': like_list, 'hits': hit_list}
        insta_df = pd.DataFrame(dict_)
        self._insta = insta_df
        self._save_num = str(save_num)
        insta_df.to_csv(f"D:\\Data_Repository\\insta\\insta_raw\\{self._save_num}.csv",  encoding='utf-8-sig', index=False)
        print("Mining Completed")
        return insta_df

# import os
# import pandas as pd
# master_df = pd.DataFrame()

# for file in os.listdir('D:\\4. LH 제안\\crawling\\블로그'):
#     if file.endswith('csv'):
#         master_df = master_df.append(pd.read_csv('D:\\4. LH 제안\\crawling\\블로그\\' + file))
    
    def preprocessor(self):
        master_df = preprocessor(kind='insta')
        master_df['date'] = pd.to_datetime(master_df['date'])
        pd.set_option('mode.chained_assignment',  None)
        for i in range(len(master_df['place'])):
            if (type(master_df['place'][i])==float) and np.isnan(master_df['place'][i]):
                master_df['place'][i] = " "
        master_df.reset_index(drop=True, inplace=True)
        master_df['text'] = master_df['main_text'] + " " + master_df['place']
        master_df.drop(columns=['feed_link', 'account', 'main_text', 'main_text_notag', 'place', 'tags', 'likes', 'hits'], inplace=True)
        master_df.reset_index(inplace=True, drop=True)
        master_df.to_csv("D:\\Data_Repository\\insta\\insta_preprocessed\\insta.csv", encoding="utf-8-sig", index=False)
        self._preprocessed_insta = master_df
        return master_df  
    
    @property
    def query(self):
        return self._query

    @property
    def userid(self):
        return self._userid

    @property
    def userpw(self):
        return self._userpw

    @property
    def insta(self):
        return self._insta

    @property
    def preprocessed_insta(self):
        return self._preprocessed_insta