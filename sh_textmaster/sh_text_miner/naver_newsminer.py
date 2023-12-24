from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import quote
from ..sh_utils1 import Header
import pandas as pd
import ssl
context = ssl._create_unverified_context()
import re


class SHNaverNewsMiner(Header):

    def __init__(self, query, start_date='2022.08.01', end_date='2022.09.01', page_num=10, head_option='default'):
        self._query = quote(query)
        self._start_date = quote(start_date)
        self._end_date = quote(end_date)
        self._page_num = page_num
        super().__init__(head_option)

    
    def extract(self):
        news_df = pd.DataFrame(columns=('Title', 'Link', 'Press', 'Datetime', 'Article'))
        idx = 0
        start_date2 = re.sub("\.", '', self._start_date)
        end_date2 = re.sub("\.", '', self._end_date)
        url = f'https://search.naver.com/search.naver?where=news&query={self._query}&sm=tab_opt&sort=1&photo=0&field=0&pd=3&ds={self._start_date}&de={self._end_date}&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3Afrom{start_date2}to{end_date2}&is_sug_officeid=0'

        for _ in range(0, self._page_num):
            
            request = urllib.request.Request(url=url, headers=self.header)
            search_url = urllib.request.urlopen(request, context=context).read()
            soup = BeautifulSoup(search_url, 'html.parser')
            links = soup.find_all('div', {'class' : 'info_group'})
            
            for link in links:
                #press = link.find('a', {'class': 'info press'}).get_text()\
                try:
                    press = link.find('a', {'class': 'info press'}).get_text()
                except AttributeError:
                    press = link.find('span', {'class': 'info press'}).get_text()
                    
                try:
                    news_url = link.find_all('a')[1].get('href')
                except:
                    continue
                
                if (news_url  == '#'): #아무것도 없을 경우
                    continue
                else:
                    request_news = urllib.request.Request(url=news_url, headers=self.header)
                    news_link = urllib.request.urlopen(request_news, context=context).read()
                    news_html = BeautifulSoup(news_link, 'html.parser')
                    
                    try:
                        title = news_html.find('h2', {'class':'media_end_head_headline'}).get_text()
                        datetime = news_html.find("span", {"class":'media_end_head_info_datestamp_time _ARTICLE_DATE_TIME'}).get_text()
                        article = news_html.find(id = 'newsct_article').get_text()
                        article = article.replace('\n', '')
                        article = article.replace('\t', '')
                    except AttributeError:
                        try:
                            title = news_html.find('h4', {'class':'title'}).get_text()
                            datetime = news_html.find('div', {'class':'info'}).get_text()
                            article = news_html.find(id = 'newsEndContents').get_text()
                            article = article.replace('\n', '')
                            article = article.replace('\t', '')
                        except AttributeError:
                            try:
                                title = news_html.find('h3', {'id':'articleTitle'}).get_text()
                                datetime = news_html.find('span', {'class':'t11'}).get_text()
                                article = news_html.find('div', {'id':'articleBodyContents'}).get_text()
                                article = article.replace('// flash 오류를 우회하기 위한 함수 추가', '')
                                article = article.replace("function _flash_removeCallback() {}", '')
                                article = article.replace('\n', '')
                                article = article.replace('\t', '')
                            except AttributeError:
                                try:
                                    title = news_html.find('h2', {'class':'end_tit'}).get_text()
                                    datetime = news_html.find('span', {'class':'author'}).get_text()
                                    article = news_html.find('div', {'id':'articeBody'}).get_text()
                                    article = article.replace('\n', '')
                                    article = article.replace('\t', '')
                                except AttributeError:
                                    title = news_html.find('h3', {'class':'info_tit'}).get_text()
                                    datetime = news_html.find('span', {'class':'info_date'}).get_text()
                                    article = news_html.find('div', {'id':'newsEndContents'}).get_text()
                                    article = article.replace('\n', '')
                                    article = article.replace('\t', '')
                                
                    except:
                        continue
                    news_df.loc[idx] = [title, news_url, press, datetime, article]
                    idx += 1
                    print(news_url, end='\n')
                        # news_df.loc[idx] = [title, news_url, press, datetime, article]
                        # idx += 1
                        # print('#', end='')

                    # except:
                    #     continue

            try:            
                next = soup.find('a', {'class', 'btn_next'}).get('href')
                url = 'https://search.naver.com/search.naver' + next
            except:
                break
        
        print('Mining Completed')
        self._news = news_df
        return news_df

    
    def preprocessor(self, save_num=1):
        news_df = self._news
        self._save_num = str(save_num)
        news_df = news_df.drop(columns=['Link', 'Press'])
        news_df.drop_duplicates(inplace=True)
        news_df.reset_index(drop=True, inplace=True)
        news_df = news_df[news_df['Article'].notna()]
        news_df = news_df[news_df['Title'].notna()]
        news_df = news_df[news_df['Datetime'].notna()]
        news_df.reset_index(drop=True, inplace=True)
        def date_replace(x):
            return re.sub('[^0-9\.]', ' ', x).split()[0]
        news_df['Datetime'] = news_df['Datetime'].apply(date_replace)
        news_df['date'] = pd.to_datetime(news_df['Datetime'])
        news_df['text'] = news_df['Title'] + " " + news_df['Article']
        news_df = news_df.drop(columns=['Title', 'Article', 'Datetime'])
        news_df.reset_index(drop=True, inplace=True)
        news_df.to_csv(f"D:\\Data_Repository\\naver_news\\naver_news_{self._save_num}.csv",  encoding='utf-8-sig', index=False)
        self._preprocessed_news = news_df
        return news_df
    
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
    def page_num(self):
        return self._page_num

    @property
    def news(self):
        return self._news

    @property
    def preprocessed_news(self):
        return self._preprocessed_news