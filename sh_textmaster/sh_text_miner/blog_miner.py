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
from ..sh_utils1 import Driver, Header
import random
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import quote
import pandas as pd
import ssl
import re


class SHBlogMiner(Driver):

    def __init__(self, query, start_date='20220801', end_date='20220901', install=False, head_option='default', driver=None):
        self._query = query
        self._start_date = start_date
        self._end_date = end_date
        self._url = f'https://search.naver.com/search.naver?where=blog&query={self._query}&sm=tab_opt&nso=so%3Add%2Cp%3Afrom{self._start_date}to{self._end_date}'
        super().__init__(self._url, install, head_option, driver)


    def extract(self, article_num_toextract='all'):
        if article_num_toextract == 'all':
            self._blog_num = None
        else:
            self._blog_num = article_num_toextract
        html = self._driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('div', {'class':'total_area'})
        blog_url_list = []
        for link in links:
            try:
                blog_url = link.find('a', {'class':'api_txt_lines total_tit'}).get('href')
                blog_url_list.append(blog_url)
            except:
                continue
        blog_url_list = [x for x in blog_url_list if 'https://blog.naver.com/' in x]
        
        title_list = []
        link_list = []
        account_list = []
        datetime_list = []
        main_text_list = []
        self._driver.switch_to.window(self._driver.window_handles[0])
        
        for i in range(len(blog_url_list[:self._blog_num])):
            url = blog_url_list[i]
            self._driver.execute_script(f"window.open('{url}');")
            time.sleep(3)
            self._driver.switch_to.window(self._driver.window_handles[1])
            time.sleep(3)
            iframe_element = self._driver.find_element(By.ID, 'mainFrame') #iframe 있으면 프레임 이동해야됨 씨발
            self._driver.switch_to.frame(iframe_element)

            try:
                title = self._driver.find_element(By.CLASS_NAME, 'pcol1').text
                title = unicodedata.normalize('NFC', title)
            except:
                title = ''
            
            #link
            #link_list.append(url)
            
            #account
            try:
                account = self._driver.find_element(By.CLASS_NAME, 'writer').text
                account = unicodedata.normalize('NFC', account)
            except:
                account = ''
            
            #datetime
            try:
                datetime_ = self._driver.find_element(By.CLASS_NAME, 'se_publishDate.pcol2').text
                datetime_ = unicodedata.normalize('NFC', datetime_)
            except NoSuchElementException:
                try:
                    datetime_ = self._driver.find_element(By.CLASS_NAME, 'date.fil5.pcol2._postAddDate').text
                    datetime_ = unicodedata.normalize('NFC', datetime_)
                except:
                    datetime_ = ''
            
            #main_text
            try:
                main_text = self._driver.find_element(By.CLASS_NAME, 'se-main-container').text
                main_text = unicodedata.normalize('NFC', main_text)
                main_text = main_text.replace('\n', '')
                main_text = main_text.replace('\t', '')        
            except NoSuchElementException:
                try:
                    main_text = self._driver.find_element(By.ID, 'postViewArea').text
                    main_text = unicodedata.normalize('NFC', main_text)
                    main_text = main_text.replace('\n', '')
                    main_text = main_text.replace('\t', '')   
                except NoSuchElementException:
                    try:
                        main_text = self._driver.find_element(By.CSS_SELECTOR, 'p.se_textarea').text
                        main_text = unicodedata.normalize('NFC', main_text)
                        main_text = main_text.replace('\n', '')
                        main_text = main_text.replace('\t', '')
                    except NoSuchElementException:
                        main_text = ''
                    # try:
                    #     main_text = self._driver.find_element_by_css_selector('p.se_textarea').text
                    #     main_text = unicodedata.normalize('NFC', main_text)
                    #     main_text = main_text.replace('\n', '')
                    #     main_text = main_text.replace('\t', '')   
                    # except:
                    #     main_text=''
            # except:
            #     main_text=''
                
            title_list.append(title)
            link_list.append(url)
            account_list.append(account)
            datetime_list.append(datetime_)
            main_text_list.append(main_text)
            
            #time.sleep(1)
            self._driver.switch_to.default_content()
            self._driver.close()
            
            print('#', end='')
                
            time.sleep(2)
            self._driver.switch_to.window(self._driver.window_handles[0])
                    
        df_dict = {'title': title_list, 'link': link_list, 'account': account_list, 'date': datetime_list, 'main_text':main_text_list}
        blog_df = pd.DataFrame(df_dict)     
        self._blog = blog_df
        print('Mining Completed')
        return blog_df
    
    def preprocessor(self, save_num=1):
        blog_df = self._blog
        self._save_num = str(save_num)
        blog_df.reset_index(drop=True, inplace=True)
        blog_df = blog_df[blog_df['date'].notna()]
        blog_df = blog_df[blog_df['date']!='']
        blog_df = blog_df[blog_df['main_text'].notna()]
        blog_df = blog_df[blog_df['main_text']!='']
        blog_df.reset_index(drop=True, inplace=True)
        # for i in range(len(blog_df['date'])):
        #     try:
        #         blog_df['date'][i] = pd.to_datetime(blog_df['date'][i])
        #     except ValueError:
        #         blog_df['date'][i] = datetime.today().strftime("%Y.%m.%d") 
        #         blog_df['date'][i] = pd.to_datetime(blog_df['date'][i])
        for i in range(len(blog_df['date'])):
            if re.search('[가-힣]', blog_df['date'][i]):
                blog_df['date'][i] = datetime.today().strftime("%Y.%m.%d") 
                blog_df['date'][i] = pd.to_datetime(blog_df['date'][i])
            else:
                blog_df['date'][i] = pd.to_datetime(blog_df['date'][i])
        blog_df['date'] = pd.to_datetime(blog_df['date'])
        blog_df.reset_index(drop=True, inplace=True)
        blog_df['date'] = pd.to_datetime(blog_df['date'])
        blog_df.reset_index(drop=True, inplace=True)
        blog_df.drop_duplicates(subset=['title', 'main_text'], inplace=True)
        blog_df = blog_df[blog_df['title'].notna()]
        blog_df = blog_df[blog_df['title']!='']
        blog_df = blog_df[blog_df['main_text'].notna()]
        blog_df.reset_index(drop=True, inplace=True)
        blog_df['text'] = blog_df['title'] + " " + blog_df['main_text']
        blog_df.drop(columns=['title', 'link', 'account', 'main_text'], inplace=True)
        blog_df.to_csv(f"D:\\Data_Repository\\blogs\\blogs_{self._save_num}.csv",  encoding='utf-8-sig', index=False)
        self._preprocessed_blogs = blog_df
        return blog_df
        
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
    def url(self):
        return self._url

    @property
    def blog_num(self):
        return self._blog_num

    @property
    def blog(self):
        return self._blog

    @property
    def preprocessed_blogs(self):
        return self._preprocessed_blogs