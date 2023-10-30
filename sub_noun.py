from soynlp import DoublespaceLineCorpus
from soynlp.word import WordExtractor  
from soynlp.noun import LRNounExtractor_v2 
from collections import Counter
from konlpy.tag import Mecab
from konlpy.tag import Okt  
from g2pk import G2p 
from pykospacing import Spacing
from datetime import date
import pandas as pd
import urllib.request
import requests
import re 
import json 
from ner_model import predict_ner
import warnings 
warnings.filterwarnings(action  = 'ignore') 

# 데이터 가져오기
def get_data():
    with open('/home/sol4/workspace/dc_inside/dc_crawl/dc/dc/spiders/gall_comments.json', 'r') as f:
        comments = json.load(f)

    # json 파일을 df 형식으로 변환시키기
    big_data = []
    for lst in comments.values():
        limited = max(100, len(lst))
        for ls in lst[:limited]: # 한 게시물에 대한 댓글 개수 제한 
            big_data.append(ls)
            
    df = pd.read_csv(r'/home/sol4/workspace/dc_inside/dc_crawl/dc/dc_crawl.csv') # 제목과 본문 데이터    
    #json_df = pd.read_csv('/home/sol4/workspace/daeun/gall_comments_json.csv')
    json_df= pd.DataFrame(data = big_data, columns = ['comment'])
    temp = pd.DataFrame(columns = ['content'])
    temp['content']= df['title'] # 제목

    tmp = pd.DataFrame(columns = ['content'])
    tmp['content']= df['content'] # 내용 본문

    tp= pd.DataFrame(columns = ['content'])
    tp['content']= json_df['comment'] #댓글

    df = pd.concat([temp, tmp,tp]) # title, comment, content 다 합친 경우
    return df

# 1차 전처리
def basic_preprocessing(df): 
    # 중복값 확인
    #print(df.duplicated(['content'], keep='first').sum())
    # 중복값 제거
    df = df.drop_duplicates(['content'], keep='first')
    # df NaN 빈칸으로 바꾸기
    df.content=df['content'].fillna('')
    df= df.reset_index(drop=True)
    return df

# 2차 전처리
def preprocessing(text):
    import re
    #\n (줄바꿈) 제거
    text = re.sub('\n', ' ', text)
    #특수기호 제거(underscore, 0-9는 삭제 안됨)
    text = re.sub('[^\w\s]', '', text)
    #underscore 제거
    text = re.sub('_', '', text)
    # URL을 공백으로 치환
    pat =  r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    text = re.sub(pat, ' ', text)
    pattern = r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{2,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    text = re.sub(pattern, ' ', text)
    # 괄호 & 괄호 안 내용 제거 
    pattern = r'\([^)]*\)'
    text = re.sub(pattern, ' ', text)
    pattern  = r'\[[^)]*\]'
    text = re.sub(pattern, ' ', text)
    ## \xa0 공백으로 치환
    text= re.sub('\xa0', ' ', text)
    # \u3000 공백으로 치환
    text=re.sub('\u3000', ' ', text)
    # 영어랑 숫자 제거하기 r"[^0-9]"
    text= re.sub(r"[a-zA-Z]", ' ', text)
    text= re.sub(r"[0-9]", ' ', text)
    #자음, 모음만 따로 작성된 것들 삭제 
    text = re.sub(r"[ㄱ-ㅣ]", "", text)
    #공백 두개 이상 하나로 지우기 
    text = re.sub('  +', ' ', text)
    return text.strip()

def word_extractor(df, file_path = 'df.txt'): 
    #word_extractor 학습을 위한 txt 만들기
    f = open(file_path, 'w', encoding='utf-8') 
    for i in range(len(df)):
        try :
            data = df["content"].loc[i]
            f.write(data + '\n')
        except :
            pass
    f.close()
    
    sents = DoublespaceLineCorpus(file_path, iter_sent=True) #한 라인을 하나의 문서로 분리
    return sents

def load_model_noun_dict():
    df = get_data()

    df = basic_preprocessing(df) # 1차 전처리
    df['content'] = df['content'].apply(preprocessing) # 2차 전처리
    df = df[df['content'].str.len() > 1] # 댓글 길이가 한 글자면 제거
    df= df.reset_index(drop=True)

    dict_sents = word_extractor(df, file_path = 'model_dict.txt')

    nouns = noun_extractor(dict_sents)

    return nouns

def check_word_in_sentence(nouns, sents):
    word, cnt = [], []
    for sent in sents:
        for noun_word in nouns['noun']:
            if noun_word in sent:
                word.append(noun_word)
                cnt.append(sent.count(noun_word))
    return word, cnt 

def noun_extractor(sents):
        
    is_one_sentence = True if len(sents)==1 else False
    if is_one_sentence:
        print('단일 문장의 경우 모델 내부 딕셔너리를 불러옵니다.') 
        predict_sents = sents
        nouns = load_model_noun_dict()
        word, cnt = check_word_in_sentence(nouns, predict_sents)
        noun_df = pd.DataFrame({'noun': word, 'count': cnt})
        return noun_df

    noun_extractor = LRNounExtractor_v2(verbose=False)
    nouns = noun_extractor.train_extract(sents) #'환경동물인권민주': NounScore(frequency=1, score=0.5)
    frequency = [noun.frequency for noun in nouns.values()] 
    noun_df = pd.DataFrame({'noun': list(nouns.keys()), 'count': frequency})
    
    compounds = list(noun_extractor._compounds_components.keys()) 
    noun_df = noun_df[~noun_df['noun'].isin(compounds)]
    
    components = []
    compound_list = list(noun_extractor._compounds_components.values())
    for compound in compound_list:
        for c in compound:
            components.append(c)

    count = Counter(components)
    compound_df = pd.DataFrame(list(count.items()), columns = ['noun', 'count']) 

    nouns = noun_df.append(compound_df, ignore_index=True)
    
    nouns = nouns.groupby('noun', as_index=False)['count'].sum()
    
    nouns = nouns.sort_values(by=['count'], ascending=False)
    nouns= nouns.reset_index(drop=True) 
    
    drop_17idx = []
    for idx in range(len(nouns)):
        if len(nouns['noun'][idx])>=7 or len(nouns['noun'][idx])<=1:
            drop_17idx.append(idx)
    nouns = nouns.drop(drop_17idx,axis=0)
    nouns= nouns.reset_index(drop=True) 
    
    line = min(int(len(nouns)*0.1),3000)
    nouns= nouns[:line]
    return nouns

#신조어 사전에 있는 단어들 제거하기
def ExistNoun_filter(nouns): #(file_path, nouns):
    try: 
        file_path = '/home/sol4/workspace/DB/final_noun.xlsx'
        df = pd.read_excel(file_path)
        existword = df['noun'].tolist()
        existword_idx = []
        for i in range(len(nouns)):
            for word in existword:
                if word in nouns['noun'][i]:
                    existword_idx.append(i)
        #print(nouns.iloc[existword_idx])
        nouns.drop(existword_idx, axis = 0, inplace = True)
        nouns = nouns.reset_index(drop=True)  
    except FileNotFoundError: 
        pass
    return nouns 

# 불용어 DB로 거르기
def stopword_filter(nouns):
    nomean_db = []
    f = open("/home/sol4/workspace/DB/no_mean.txt", 'r')
    for line in f:
        nomean_db.append(line.replace('\n',''))
    f.close()

    nomean_idx = []
    for i in range(len(nouns)):
        for nomean in nomean_db:
            if nomean in nouns['noun'][i] :
                nomean_idx.append(i)
    #print('불용어 단어 탈락결과')
    #print(list(nouns.iloc[nomean_idx]['noun']))
    nouns.drop(nomean_idx, axis=0, inplace = True)       
    nouns = nouns.reset_index(drop=True)
    return nouns

# 욕 DB로 거르기
def profanity_filter(nouns):
    yok_db = []
    f = open("/home/sol4/workspace/DB/yoks.txt", 'r')
    for line in f:
        yok_db.append(line.replace('\n',''))
    f.close()

    yok_idx = []
    for i in range(len(nouns)):
        for yok in yok_db:
            if yok in nouns['noun'][i] :
                yok_idx.append(i)
    #print('욕 단어 탈락결과')
    #print(list(nouns.iloc[yok_idx]['noun']))
    nouns.drop(yok_idx, axis=0, inplace = True)       
    nouns = nouns.reset_index(drop=True)
    return nouns

def korword_in_dict(kw): #kw= 검색하고자 하는 단어 ex) 나무, 잼민이
    with open ((r'/home/sol4/workspace/api_key/stdic_api_key.txt'), 'r') as key:
        api_key = key.readline()
    keyword = kw
    opendict_api =f'https://stdict.korean.go.kr/api/search.do?certkey_no=5882&&key={api_key}&q={keyword}&req_type=json'
    res = requests.get(opendict_api, verify = False)
    # res.status_code 200이 나와야 정상
    result = res.text.replace("\n",'')
    if result == '' :
      return False # 사전에 존재하지 않음
    else :
      return True # 사전에 존재함

def dic_filter(nouns): #사전 필터링
   stddict_drop_index = []
   for idx, word in nouns['noun'].items():
      if korword_in_dict(word):
         stddict_drop_index.append(idx)
         
   nouns = nouns.drop(stddict_drop_index)
   nouns = nouns.reset_index(drop=True)  

   return nouns

def pos_tag(nouns): #형태소 분석
    mecab= Mecab()
    okt = Okt()
    nouns['mecab_pos']=nouns['noun'].map(lambda x:mecab.pos(x))
    nouns['okt_pos']=nouns['noun'].map(lambda x:okt.pos(x))
    return nouns 

def pos_combo1(nouns): # 1. okt_pos에서 Adverb로 분류된 단어들 탈락시키기
    adverb_index = []
    for idx in range(len(nouns)):
        if len(nouns['okt_pos'][idx]) == 1 and nouns['okt_pos'][idx][0][1] == 'Adverb':
            adverb_index.append(idx)
    #print('1. nouns에서 탈락되는 단어들')
    #print(list(nouns.iloc[adverb_index]['noun'])  )      
    nouns = nouns.drop(adverb_index,axis=0)
    nouns = nouns.reset_index(drop=True)  
    return nouns
    
def pos_combo2(nouns): # 2. okt_pos에서 Adjective 로 분류된 단어들 탈락시키기 
    adj_index = []
    for idx in range(len(nouns)):
        if len(nouns['okt_pos'][idx]) == 1 and nouns['okt_pos'][idx][0][1] == 'Adjective':
            adj_index.append(idx)
    #print('2. nouns에서 탈락되는 단어들')
    #print(list(nouns.iloc[adj_index]['noun'])  )      
    nouns = nouns.drop(adj_index,axis=0)
    nouns = nouns.reset_index(drop=True)  
    return nouns        
    
def pos_combo3(nouns): # 3. okt_pos에서 Suffix 로 분류된 단어들 탈락시키기 
    suffix_index = []
    for idx in range(len(nouns)):
        if len(nouns['okt_pos'][idx]) == 1 and nouns['okt_pos'][idx][0][1] == 'Suffix':
            suffix_index.append(idx)
    #print('3. nouns에서 탈락되는 단어들')
    #print(list(nouns.iloc[suffix_index]['noun'])  )      
    nouns = nouns.drop(suffix_index,axis=0)
    nouns = nouns.reset_index(drop=True)  
    return nouns 
        
def pos_combo4(nouns): # 4. okt_pos에서 Verb 로 분류된 단어들 중 몇가지 조합 탈락시키기 
    verb_index = []
    for idx in range(len(nouns)):
        if len(nouns['okt_pos'][idx]) == 1 and nouns['okt_pos'][idx][0][1] == 'Verb':
            if len(nouns['mecab_pos'][idx]) == 2 and nouns['mecab_pos'][idx][0][1] == 'VV+EP' and nouns['mecab_pos'][idx][1][1] == 'EC':
                verb_index.append(idx)
            elif len(nouns['mecab_pos'][idx]) == 3 and nouns['mecab_pos'][idx][0][1] == 'VV' and nouns['mecab_pos'][idx][1][1] == 'EP' and nouns['mecab_pos'][idx][2][1] == 'EC':
                verb_index.append(idx)
            elif len(nouns['mecab_pos'][idx]) ==1 and nouns['mecab_pos'][idx][0][1] == 'VV+EC' :
                verb_index.append(idx)
            elif len(nouns['mecab_pos'][idx]) ==1 and nouns['mecab_pos'][idx][0][1] == 'VV+ETM' :
                verb_index.append(idx)
            elif len(nouns['mecab_pos'][idx]) == 2 and nouns['mecab_pos'][idx][0][1] == 'VV+EP' :
                verb_index.append(idx) 
            elif 'JX' in str(nouns['mecab_pos'][idx])  : 
                verb_index.append(idx)
            elif len(nouns['mecab_pos'][idx]) ==2 and nouns['mecab_pos'][idx][0][1] == 'VV+ETM' and nouns['mecab_pos'][idx][1][1] == 'NNB' :
                verb_index.append(idx)
            elif len(nouns['mecab_pos'][idx]) ==3 and nouns['mecab_pos'][idx][0][1] == 'VV' and nouns['mecab_pos'][idx][1][1] == 'ETM'   and nouns['mecab_pos'][idx][2][1] == 'NNB':
                verb_index.append(idx)
            elif len(nouns['mecab_pos'][idx]) ==3 and nouns['mecab_pos'][idx][0][1] == 'VV' and nouns['mecab_pos'][idx][1][1] == 'ETM'   and nouns['mecab_pos'][idx][2][1] == 'NNG':
                verb_index.append(idx)
            elif len(nouns['mecab_pos'][idx]) ==2 and nouns['mecab_pos'][idx][0][1] == 'VA' and nouns['mecab_pos'][idx][1][1] == 'EC'   :
                verb_index.append(idx)
    #print('4. nouns에서 탈락되는 단어들')
    #print(list(nouns.iloc[verb_index]['noun'])  )      
    nouns = nouns.drop(verb_index,axis=0)
    nouns = nouns.reset_index(drop=True)
    return nouns             
    
def pos_combo5(nouns): # 5. Okt로 분석한 결과 Noun과 Suffix로 이루어져 있고, Mecab으로 분석한 결과 NNG와 XSN으로 이루어져 있으면 탈락
    drop_index = []
    for idx in range(len(nouns)):
        if len(nouns['mecab_pos'][idx])==2 :
            if nouns['mecab_pos'][idx][0][1]== 'NNG' and nouns['mecab_pos'][idx][1][1]== 'XSN'  :
                if len(nouns['okt_pos'][idx])==2 :
                    if nouns['okt_pos'][idx][0][1]== 'Noun' and nouns['okt_pos'][idx][1][1]== 'Suffix'  :
                        drop_index.append(idx)
    #print('5. nouns 탈락결과')
    #print(list(nouns.iloc[drop_index]['noun']))
    nouns.drop(drop_index, axis=0, inplace = True)       
    nouns = nouns.reset_index(drop=True)
    return nouns        
    
def pos_combo6(nouns): # 6. okt_pos에서 마지막이 josa인데, jos인 부분을 제외한 앞 단어가 사전에 등록되어 있으면 삭제, 앞 단어가 사전에 등록되어 있지만 않으면 내비둠. 
# 앞 단어가 이미 신조어 후보 목록에 올라와 있어도 삭제!
    josa_list = []
    for idx in range(len(nouns)):
        if nouns['okt_pos'][idx][len(nouns['okt_pos'][idx])-1][1] == 'Josa': # OKT_POS 마지막이 JOSA    
            josa = nouns['okt_pos'][idx][len(nouns['okt_pos'][idx])-1][0]
            no_josa_word = nouns['noun'][idx].replace(josa,'') # 조사를 제외한 단어
            # 1. 조사를 제외한 단어가 이미 신조어 후보 목록에 등록되어 있다 -> 조사 포함 단어 삭제 
            if no_josa_word in list(nouns['noun']):
                josa_list.append(idx)
            # 2. 조사를 제외한 단어가 사전에 등록되어있다. -> 조사포함 단어 삭제
            elif korword_in_dict(no_josa_word) : 
                josa_list.append(idx)
    #print('6. nouns 탈락결과')
    #print(list(nouns.iloc[josa_list]['noun']))
    nouns.drop(josa_list, axis=0, inplace = True)       
    nouns = nouns.reset_index(drop=True)
    return nouns 

def pos_combo7(nouns): # 7. okt_pos에서 마지막이 Suffix인데, suffix인 부분을 제외한 앞 단어가 이미 신조어 후보 목록에 올라와 있어도 삭제!  
    suffix_list = []
    for idx in range(len(nouns)):
        if nouns['okt_pos'][idx][len(nouns['okt_pos'][idx])-1][1] == 'Suffix': # OKT_POS 마지막이 Suffix 
            suffix = nouns['okt_pos'][idx][len(nouns['okt_pos'][idx])-1][0]
            no_suffix_word = nouns['noun'][idx].replace(suffix,'') #  Suffix 를 제외한 단어
            
            # 1. suffix를 제외한 단어가 이미 신조어 후보 목록에 등록되어 있다 ->  Suffix  포함 단어 삭제 
            if no_suffix_word in list(nouns['noun']):
                suffix_list.append(idx) 

    #print('7. nouns 탈락결과')
    #print(list(nouns.iloc[suffix_list]['noun']))
    nouns.drop(suffix_list, axis=0, inplace = True)       
    nouns = nouns.reset_index(drop=True)
    return nouns

def pos_combo8(nouns): # 8. Mecab_pos가 VV, EC로 구성, Okt_pos가 Verb로 되어있는 경우 삭제
    drop_index = [] 
    for idx in range(len(nouns)):
        if len(nouns['mecab_pos'][idx])==2 :
            if nouns['mecab_pos'][idx][0][1]== 'VV' and nouns['mecab_pos'][idx][1][1]== 'EC'  :
                if len(nouns['okt_pos'][idx])==1 :
                    if nouns['okt_pos'][idx][0][1]== 'Verb'  :
                        drop_index.append(idx)
    #print('8. nouns 탈락결과')
    #print(list(nouns.iloc[drop_index]['noun']))
    nouns.drop(drop_index, axis=0, inplace = True)       
    nouns = nouns.reset_index(drop=True)
    return nouns

# 한글을 input으로 넘겨주면 영어로 번역한 결과 제시 - PAPAGO
def translate_korean_to_english(text):
    with open ('/home/sol4/workspace/api_key/papago_api_key.txt', 'r') as f:
        client_id = f.readline().strip()
        client_secret = f.readline()

    url = 'https://openapi.naver.com/v1/papago/n2mt'
    headers = {
        'X-Naver-Client-Id': client_id,
        'X-Naver-Client-Secret': client_secret
    }
    data = {
        'source': 'ko',
        'target': 'en',
        'text': text
    }

    response = requests.post(url, headers=headers, data=data)
    result = response.json()
    translated_text = result['message']['result']['translatedText']

    return translated_text

def convert_to_korean_pronunciation(word):
    g2p = G2p()
    pronunciation = g2p(word)
    return pronunciation

def english_filter(nouns):
    # 한글 단어를 영어로 번역한 칼럼 : eng_word
    nouns['eng_word']= ''
    for idx in range(len(nouns)):
        nouns['eng_word'].iloc[idx]=translate_korean_to_english(nouns['noun'].iloc[idx])
        
    # 영어를 한글발음 칼럼 생성 : pronoun (시간 다소 오래걸림 450행에 10분정도)
    nouns['eumcha_word']= ''
    for idx in range(len(nouns)):
        if nouns['eumcha_word'].iloc[idx] == '':
            nouns['eumcha_word'].iloc[idx]= convert_to_korean_pronunciation(nouns['eng_word'].iloc[idx])
            
    eng_pro_idx = nouns[nouns['noun']== nouns['eumcha_word']].index
    #nouns.iloc[eng_pro_idx]
    #print('english_filter으로 탈락되는 단어들 확인')
    #print(list(nouns.iloc[eng_pro_idx]['noun']))  
    nouns.drop(eng_pro_idx, axis=0, inplace = True)       
    nouns = nouns.reset_index(drop=True)
    return nouns 

# ner 개체명 단어 삭제 
def ner_tag(nouns, df):
    ner_df = pd.DataFrame(columns= ['content'])
    for noun in list(nouns['noun']):
        ner_df = pd.concat([df[df['content'].str.contains(noun)], ner_df])
    if not len(ner_df):
        return [[],[]]
    pred_text, pred_tag = predict_ner((ner_df.drop_duplicates(subset=['content'])['content'].values))
    return [pred_text, pred_tag]


def ner_filter(ner_result, filter_tag, nouns):
    """
    ner_result[0] -> word
    ner_result[1] -> tag
    """
    per_set = []
    word_data = ner_result[0]
    tag_data = ner_result[1]
    
    for idx1, tags in enumerate(tag_data):
        for idx2, tag in enumerate(tags):
            if tag == filter_tag :
                per_set.append(word_data[idx1].split()[idx2])
                
    cutline = int(len(Counter(per_set)) * 0.05)
    word_tag_list_per = Counter(per_set).most_common()[:cutline] 
    word_list_per = [tup[0] for tup in word_tag_list_per]

    drop_idx = []
    for word in word_list_per:
        for idx, other in enumerate(nouns['noun']):
            if other in word:
                drop_idx.append(idx)
    drop_idx = list(set(drop_idx))
    #print(filter_tag , 'NER 작업으로 인해 탈락되는 단어들')
    #print(list(nouns.iloc[drop_idx]['noun']))
    nouns = nouns.drop(drop_idx,axis=0)
    nouns = nouns.reset_index(drop=True)
    return nouns

#띄어쓰기 오류 단어 필터링
def pykospacing_filter(nouns):
    spacing = Spacing()
    nouns['pykospacing']=''
    nouns['space_mecab']=''

    for idx in range(len(nouns)):
        # mecab 기반 띄어쓰기
        txt =''
        for n in range(len(nouns['mecab_pos'][idx])):
            txt = txt + nouns['mecab_pos'][idx][n][0]+' '
        nouns['space_mecab'][idx]= txt
        # pykospacing 기반 띄어쓰기
        word = nouns['noun'][idx]
        nouns['pykospacing'][idx]= spacing(word)
    nouns['space_mecab'] = nouns['space_mecab'].str.rstrip()

    # pykospacing으로 했을 때 띄어쓰기 변화 일어나고 & mecab 띄어쓰기와 pykospacing으로 띄어쓰기 결과 같음 
    space_index = []
    for idx in range(len(nouns)):
        if nouns['noun'][idx] != nouns['pykospacing'][idx]:
            if nouns['space_mecab'][idx] == nouns['pykospacing'][idx]:
                if nouns['mecab_pos'][idx][0][1]=='MM':
                    space_index.append(idx)   
    #print('pykospacing으로 탈락되는 단어들 확인')
    #print(list(nouns.iloc[space_index]['noun']))
    nouns.drop(space_index, axis = 0, inplace = True)
    nouns = nouns.reset_index(drop= True) 
    return nouns

#신조어 예비 후보 및 예문 가져오기 
def get_result(nouns, df):
    result = pd.DataFrame(columns=['date', 'noun', 'example']) 
    nouns = nouns['noun'].tolist()
    for noun in nouns: 
        today = date.today()
        example = df['content'].str.contains(noun)
        example_df = df[example]
        #30자 이하 문장만 가져오기 
        long_examples = example_df[example_df['content'].str.len()<=30]['content'].head(2).tolist()
        #만약 30자를 넘는 문장이 없을 경우, 30자 이상 문장 가져오기 
        if len(long_examples) == 0:
            all_examples = example_df['content'].head(2).tolist()
            result = result.append({
                'date': today, 'noun':noun, 'example': all_examples}, ignore_index = True)
        else: 
            result = result.append({
                'date': today, 'noun': noun, 'example': long_examples}, ignore_index = True)
    try: 
        file_path = '/home/sol4/workspace/DB/temp_noun.xlsx'
        temp_df = pd.read_excel(file_path, index_col=0)
        temp_new_df = temp_df.append(result, ignore_index = True)
        temp_new_df.to_excel(file_path) 
    except FileNotFoundError: 
        result.to_excel('DB/temp_noun.xlsx')
    return result


# DB에 있는 키워드라면 유사한 상위 3개 문장 가져오기
def predict_new_word_sentence(keywords, text):
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer('klue/bert-base')

    path = '/home/sol4/workspace/DB/temp_noun.csv' # 데이터 베이스 경로
    model_dict = pd.read_csv(path)
    
    sim_sentences = dict()

    for keyword in keywords:
        if len(model_dict[model_dict['noun'] == keyword]) == 0 : 
            result = []
        else:
            sentences2 = eval(model_dict[model_dict['noun'] == keyword]['example'].values[0])
            
            text_embedding = model.encode(text)
            dict_embedding = model.encode(sentences2)
            cos_similarity = util.cos_sim(text_embedding, dict_embedding)
            print_idx = cos_similarity[0].cpu().numpy().argsort()[::-1][:3] # 유사도가 높은 상위 3개 출력
            result = [sentences2[idx] for idx in print_idx]
        
        sim_sentences[keyword] = result

    return  sim_sentences# 리스트 형태로 반환
