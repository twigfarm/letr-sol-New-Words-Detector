from sub_noun import *
#from time import process_time 
#import numpy as np

#start = process_time() 
#print('실행시작') 

df = get_data()

df = basic_preprocessing(df) # 1차 전처리
df['content'] = df['content'].apply(preprocessing) # 2차 전처리
df = df[df['content'].str.len() > 1] # 댓글 길이가 한 글자면 제거
df= df.reset_index(drop=True)

sents = word_extractor(df)

nouns = noun_extractor(sents)

nouns = ExistNoun_filter(nouns)

nouns = stopword_filter(nouns)  

nouns = profanity_filter(nouns)

nouns = dic_filter(nouns)

nouns = pos_tag(nouns) 
nouns = pos_combo1(nouns)
nouns = pos_combo2(nouns)
nouns = pos_combo3(nouns)
nouns = pos_combo4(nouns)
nouns = pos_combo5(nouns)
nouns = pos_combo6(nouns)
nouns = pos_combo7(nouns)
nouns = pos_combo8(nouns)

nouns = english_filter(nouns)

nouns = pykospacing_filter(nouns)

ner_result = ner_tag(nouns, df)   
nouns = ner_filter(ner_result, 'PS', nouns)
nouns = ner_filter(ner_result, 'OGG', nouns)


result = get_result(nouns, df) 
print(result)

#end = process_time()
#print('총 ',np.round(end-start,3),'초 걸렸다.') 

#print(result) -> temp_noun.xlsx에서 확인가능
