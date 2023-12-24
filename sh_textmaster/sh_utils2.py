import os
import pandas as pd
from konlpy.tag import Okt
import nltk
import re
import pickle



class TextGenerator:

    def __init__(self, text_type='all'):
        self._text_type = text_type
        self._text_df = pd.DataFrame()
        text_types = ['blogs', 'insta\\insta_preprocessed', 'naver_news', 'twitter\\twitter_preprocessed']
        text_type_class = ['blog', 'insta', 'news', 'twitter']
        if text_type=='all':
            for i in range(len(text_types)):
                temp = pd.DataFrame()
                for file in os.listdir(f"D:\\Data_Repository\\{text_types[i]}"):
                    if file.endswith('.csv'):
                        temp = temp.append(pd.read_csv(f"D:\\Data_Repository\\{text_types[i]}\\" + file))
                self._text_df = self._text_df.append(temp)
        elif text_type in text_type_class:
            idx = text_type_class.index(text_type)
            self._text_df = pd.DataFrame()
            for file in os.listdir(f"D:\\Data_Repository\\{text_types[idx]}"):
                if file.endswith('.csv'):
                    self._text_df = self._text_df.append(pd.read_csv(f"D:\\Data_Repository\\{text_types[idx]}\\" + file))
        else:
            raise ValueError('Valid text type parameters include only "blog", "insta", "news", "twitter", or "all".')

        self._text_df.reset_index(drop=True, inplace=True)
        self._text_df = self._text_df.drop_duplicates(subset="text")
        self._text_df.reset_index(drop=True, inplace=True)
        self._text_df['date'] = pd.to_datetime(self._text_df['date'])
        self._text_df.sort_values(by='date', ascending=False, inplace=True)
        self._text_df.reset_index(drop=True, inplace=True)


def open_dictionary(dictionary):
    with open(f"D:\\Data_Repository\\dictionary\\{dictionary}.txt", 'r', encoding='utf-8') as file:
        list_ = [word.strip() for word in file]
        list_set = set(list_)
        return list_set

def clean(text):
    return re.sub(r'[^A-Za-z0-9가-힣]', " ", text).strip()

def dict_(list_, list_2):
    return [word for word in list_ if word in list_2]

def wcount(list_):
    x_list = []
    y_list = []
    for x, y in nltk.Text(list_).vocab().most_common(5000):
        x_list.append(x)
        y_list.append(y)
    return pd.DataFrame({"word":x_list, "freq":y_list})

def context_end(text, ngramWords):
    list_ = []
    for word in ngramWords:
        if word.split()[1][:len(text)] == text:
            list_.append(word)
    return nltk.Text(list_).vocab().most_common()

def context_front(text, ngramWords):
    list_ = []
    for word in ngramWords:
        if word.split()[0][:len(text)] == text:
            list_.append(word)
    return nltk.Text(list_).vocab().most_common()

def context_end2(text, ngramWords):
    list_ = []
    for word in ngramWords:
        if word.split()[1][:len(text)] == text:
            list_.append(word.split()[0].split('/')[0] + " " + word.split()[1].split('/')[0])
    return nltk.Text(list_).vocab().most_common()

def context_front2(text, ngramWords):
    list_ = []
    for word in ngramWords:
        if word.split()[0][:len(text)] == text:
            list_.append(word.split()[0].split('/')[0] + " " + word.split()[1].split('/')[0])
    return nltk.Text(list_).vocab().most_common()

def context_end3(text, ngramWords):
    list_ = []
    for word in ngramWords:
        if word.split()[2][:len(text)] == text:
            list_.append(word)
    return nltk.Text(list_).vocab().most_common()

def context_front3(text, ngramWords):
    list_ = []
    for word in ngramWords:
        if word.split()[0][:len(text)] == text:
            list_.append(word)
    return nltk.Text(list_).vocab().most_common()

def context_mid3(text, ngramWords):
    list_ = []
    for word in ngramWords:
        if word.split()[1][:len(text)] == text:
            list_.append(word)
    return nltk.Text(list_).vocab().most_common()

def context_end4(text, ngramWords):
    list_ = []
    for word in ngramWords:
        if word.split()[2][:len(text)] == text:
            list_.append(word.split()[0].split('/')[0] + " " + word.split()[1].split('/')[0] + \
                " " + word.split()[2].split('/')[0])
    return nltk.Text(list_).vocab().most_common()

def context_front4(text, ngramWords):
    list_ = []
    for word in ngramWords:
        if word.split()[0][:len(text)] == text:
            list_.append(word.split()[0].split('/')[0] + " " + word.split()[1].split('/')[0] \
                + " " + word.split()[2].split('/')[0])
    return nltk.Text(list_).vocab().most_common()

def context_mid4(text, ngramWords):
    list_ = []
    for word in ngramWords:
        if word.split()[1][:len(text)] == text:
            list_.append(word.split()[0].split('/')[0] + " " + word.split()[1].split('/')[0] \
                + " " + word.split()[2].split('/')[0])
    return nltk.Text(list_).vocab().most_common()

def context(text, ngram_words_no_1word, ngram_3_words_no1word):
    list_context_end = []
    for word in ngram_words_no_1word:
        if word.split()[1][:len(text)] == text:
            list_context_end.append(word.split()[0].split('/')[0] + " " + word.split()[1].split('/')[0])
    context_end = pd.Series(nltk.Text(list_context_end).vocab().most_common()) 
    list_context_front = []
    for word in ngram_words_no_1word:
        if word.split()[0][:len(text)] == text:
            list_context_front.append(word.split()[0].split('/')[0] + " " + word.split()[1].split('/')[0])
    context_front = pd.Series(nltk.Text(list_context_front).vocab().most_common())
    list_context_end_3gram = []
    for word in ngram_3_words_no1word:
        if word.split()[2][:len(text)] == text:
            list_context_end_3gram.append(word.split()[0].split('/')[0] + " " + word.split()[1].split('/')[0] + \
                " " + word.split()[2].split('/')[0])
    context_end_3gram = pd.Series(nltk.Text(list_context_end_3gram).vocab().most_common())
    list_context_front_3gram = []
    for word in ngram_3_words_no1word:
        if word.split()[0][:len(text)] == text:
            list_context_front_3gram.append(word.split()[0].split('/')[0] + " " + word.split()[1].split('/')[0] \
                + " " + word.split()[2].split('/')[0])
    context_front_3gram = pd.Series(nltk.Text(list_context_front_3gram).vocab().most_common())
    list_context_mid_3gram = []
    for word in ngram_3_words_no1word:
        if word.split()[1][:len(text)] == text:
            list_context_mid_3gram.append(word.split()[0].split('/')[0] + " " + word.split()[1].split('/')[0] \
                + " " + word.split()[2].split('/')[0])
    context_mid_3gram = pd.Series(nltk.Text(list_context_mid_3gram).vocab().most_common())
    context_df = pd.DataFrame({'context_end':context_end, 'context_front':context_front, 'context_end2':context_end_3gram, 'context_front2':context_front_3gram, 'context_mid':context_mid_3gram})
    return context_df

def ratio(num1, num2):
    return round(num1/(num1+num2)*100, 2)

def multi_preprocess(query):
    query = [query]
    okt = Okt()
    clean_list = []
    for i in range(len(query)):
        clean_sentence = clean(query[i])
        clean_list.append(clean_sentence)
    clean_list_lower = [x.lower() for x in clean_list]
    list_ = okt.pos(clean_list_lower[0], norm=True, stem=True)
    list_ = [word for word, tag in list_ if tag in ["Noun", "Verb"]]
    return list_


class MultiIndex:

    def __init__(self, query, dictionary='dictionary'):
        self._dictionary = dictionary
        dictionary = pd.read_excel(f"D:\\Data_Repository\\dictionary\\multi_index\\{dictionary}.xlsx")
        dictionary =  dictionary[dictionary.columns[0]].to_list()
        self._query = query
        self._query = multi_preprocess(self._query)
        with open('listofwords.txt', 'rb') as fp:
            listofwords = pickle.load(fp)
        indexed_list = []
        for i in range(len(listofwords)):
            if set(self._query).issubset(set(listofwords[i]))==True:
                indexed_list.append(listofwords[i])
        one_list_words_of_indexedlist = []
        for lists in indexed_list:
            for word in lists:
                one_list_words_of_indexedlist.append(word)
        region_words = [word for word in one_list_words_of_indexedlist if word in dictionary]
        self._result = nltk.Text(region_words).vocab().most_common()
        return self._result