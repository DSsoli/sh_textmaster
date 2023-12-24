from ..sh_utils2 import *


class SHTextAnalyzer(TextGenerator, MultiIndex):

    def __init__(self, text_type):
        TextGenerator.__init__(self, text_type)

    
    def info_quantity(self, date_from='2022-08', date_to='2022-09'):
        self._date_from = date_from
        self._date_to = date_to
        date_df = self._text_df[(self._text_df.date >= self._date_from) & (self._text_df.date<=self._date_to)]
        print(f"Total info quantity from {self._date_from} and before {self._date_to}:  {len(date_df)}")
        return date_df

    
    def text_analyze(self, context_word_num = 50):
        self._context_word_num = context_word_num
        stop, positiveset, negativeset = open_dictionary('stopwords'), open_dictionary("positive"), open_dictionary("negative")
        okt = Okt()
        
        clean_list = []
        for i in range(len(self._text_df['text'])):
            clean_sentence = clean(self._text_df['text'][i])
            clean_list.append(clean_sentence)
        clean_list_lower = [sentence.lower() for sentence in clean_list]
        
        pos_list_total = []
        for sentence in clean_list_lower:
            temp = [pos for pos in okt.pos(sentence, stem=True, norm=True)]
            if temp:
                pos_list_total.append(temp)
        
        pos_list_selected_list = []
        for lists in pos_list_total:
            temp = []
            for i in range(len(lists)):
                if lists[i][1] in ['Adjective', 'Noun', "Verb", "VerbPrefix"]:
                    temp.append(list(lists[i]))
            pos_list_selected_list.append(temp)

        for lists in pos_list_selected_list:
            for x in range(len(lists)):
                if lists[x][1]=='Verb' and lists[x-1][1]=='VerbPrefix':
                    lists[x][0] = lists[x-1][0] + lists[x][0]
                    lists[x][1] = 'VerbPrefix + Verb'
                    lists[x-1][0] = 'del'
                    lists[x-1][1] = 'del'

        pos_list_selected_final = []
        for lists in pos_list_selected_list:
            temp = []
            for x in range(len(lists)):
                if (lists[x][0] != 'del') and (lists[x][1] != 'del'):
                    temp.append(lists[x])
            pos_list_selected_final.append(temp)
        
        words = []
        for lists in pos_list_selected_final:
            for word, pos in lists:
                words.append(word)
        
        words_final = [word for word in words if word not in stop and len(word) > 1]
        w_pos = dict_(words_final, positiveset)
        w_neg = dict_(words_final, negativeset)
        sum_pos = 0
        x_pos = nltk.Text(w_pos).vocab().most_common()
        
        for word, freq in x_pos:
            sum_pos+=freq
        sum_neg = 0
        
        x = nltk.Text(w_neg).vocab().most_common()
        for word, freq in x:
            sum_neg+=freq
        
        self._freq = wcount(words_final)
        count = pd.DataFrame({'pos_count':[sum_pos, ratio(sum_pos, sum_neg)], 'neg_count': [sum_neg, ratio(sum_neg, sum_pos)]})
        w_pos = wcount(w_pos)
        w_neg = wcount(w_neg)
        list_ = [self._freq, w_pos, w_neg]
        
        pos_list_total2 = []
        for sentence in clean_list_lower:
            temp = [pos for pos in okt.pos(sentence, norm=True, stem=True, join=True)]
            if temp:
                pos_list_total2.append(temp)
        
        pos_list_selected_list2 = []
        for lists in pos_list_total2:
            temp = []
            for x in range(len(lists)):
                if lists[x].split('/')[1] in ['Adjective', 'Noun', "Verb", "VerbPrefix"]:
                    temp.append(lists[x])
            pos_list_selected_list2.append(temp)
        for lists in pos_list_selected_list2:
            for x in range(len(lists)):
                if lists[x].split('/')[1]=='Verb' and lists[x-1].split('/')[1]=='VerbPrefix':
                    
                    lists[x] = lists[x-1].split('/')[0] + lists[x].split('/')[0] + '/' + "VerbPrefix+Verb"
                    lists[x-1] = 'del'        
        
        pos_list_selected_final2 = []
        for lists in pos_list_selected_list2:
            temp = []
            for x in range(len(lists)):
                if lists[x] != 'del':
                    temp.append(lists[x])
            pos_list_selected_final2.append(temp)
                
        ngram_1word = []
        for i in range(len(pos_list_selected_final2)):
            temp = []
            for j in range(len(pos_list_selected_final2[i])-1):
                ngram_word = pos_list_selected_final2[i][j] + " " + pos_list_selected_final2[i][j+1]
                temp.append(ngram_word)
            ngram_1word.append(temp)
                
        ngram_words_1word = []
        for lists in ngram_1word:
            for word in lists:
                ngram_words_1word.append(word)

        pos_list_selected_final_no_1word = []
        for lists in pos_list_selected_final2:
            temp = []
            for x in range(len(lists)):
                if len(lists[x].split('/')[0]) > 1:
                    temp.append(lists[x])
            pos_list_selected_final_no_1word.append(temp)

        ngram_no_1word = []
        for i in range(len(pos_list_selected_final_no_1word)):
            temp = []
            for j in range(len(pos_list_selected_final_no_1word[i])-1):
                ngram_word = pos_list_selected_final_no_1word[i][j] + " " + pos_list_selected_final_no_1word[i][j+1]
                temp.append(ngram_word)
            ngram_no_1word.append(temp)

        ngram_words_no_1word = []
        for lists in ngram_no_1word:
            for word in lists:
                ngram_words_no_1word.append(word)

        ngram_3 = []
        for i in range(len(pos_list_selected_final2)):
            temp = []
            for j in range(len(pos_list_selected_final2[i])-2):
                ngram_word = pos_list_selected_final2[i][j] + " " + pos_list_selected_final2[i][j+1] + " " + pos_list_selected_final2[i][j+2]
                temp.append(ngram_word)
            ngram_3.append(temp)

        ngram_3_words_1word = []
        for lists in ngram_3:
            for word in lists:
                ngram_3_words_1word.append(word)

        ngram_3_no_1word = []
        for i in range(len(pos_list_selected_final_no_1word)):
            temp = []
            for j in range(len(pos_list_selected_final_no_1word[i])-2):
                ngram_word = pos_list_selected_final_no_1word[i][j] + " " + pos_list_selected_final_no_1word[i][j+1] \
                    + " " + pos_list_selected_final_no_1word[i][j+2]
                temp.append(ngram_word)
            ngram_3_no_1word.append(temp)
                
        ngram_3_words_no1word = []
        for lists in ngram_3_no_1word:
            for word in lists:
                ngram_3_words_no1word.append(word)        

        listofwords = []
        for lists in pos_list_selected_final:
            temp = []
            for word, tag in lists:
                temp.append(word)
            if temp:
                listofwords.append(temp)
        import pickle
        with open('listofwords.txt', 'wb') as fp:
            pickle.dump(listofwords, fp)

        with pd.ExcelWriter('D:\\Data_Repository\\analysis_result\\analysis.xlsx') as writer:
            self._freq.to_excel(writer, sheet_name='Freq', index=False)
            w_pos.to_excel(writer, sheet_name='Pos', index=False)
            w_neg.to_excel(writer, sheet_name='Neg', index=False)
            count.to_excel(writer, sheet_name='Pos_Neg_Count', index=False)
            #neg_count.to_excel(writer, sheet_name='Neg_Count', index=False)            
            for i in range(len(list_)):
                temp = list_[i]['word'][:self._context_word_num]
                context_df = context(temp[0], ngram_words_no_1word, ngram_3_words_no1word)
                empty_df = pd.DataFrame(columns=['--------'])
                j=0
                while j<len(temp)-1:
                    j += 1
                    context_df = pd.concat([context_df, empty_df, context(temp[j], ngram_words_no_1word, ngram_3_words_no1word)], axis=1)
                    context_df.to_excel(writer, sheet_name=f'Context{i}', index=False)

        
    def multi_indexing(self, query, dictionary='dictionary'):
        MultiIndex.__init__(self, query, dictionary)
        return self._result

    
    @property
    def text_df(self):
        return self._text_df
    
    
    

