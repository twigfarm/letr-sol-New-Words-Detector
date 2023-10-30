import re
import json
import pandas as pd  
from collections import Counter
from datetime import date
from soynlp.normalizer import repeat_normalize
import warnings 
warnings.filterwarnings(action  = 'ignore')

#1. Data Load
def get_data():
    with open('/home/sol4/workspace/dc_inside/dc_crawl/dc/dc/spiders/gall_comments.json', 'r') as f: # 댓글데이터
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

#2. 전처리 
#1차 전처리
def basic_preprocessing(df): 
    #print(df.duplicated(['content'], keep='first').sum(),'개 행 탈락') # 중복값 확인
    df = df.drop_duplicates(['content'], keep='first') # 중복값 제거
    df.content=df['content'].fillna('') # df NaN 빈칸으로 바꾸기
    df= df.reset_index(drop=True)
    return df

# 유니코드 전처리
def preprocessing_unicode(tp):
    tp = re.sub('\n', ' ', tp) #\n (줄바꿈) 제거
    tp= re.sub('\xa0', ' ', tp) ## \xa0 공백으로 치환
    tp= re.sub('\u3000', ' ', tp) # \u3000 공백으로 치환
    tp= re.sub('- dc App', '', tp) 
    return tp.strip()

# 2차 전처리
def preprocessing(tp):
    tp = re.sub('  +', ' ', tp) # 공백 2번 이상 지우기
    # 특정 자음, 모음 을 반복하는 경우
    tp = re.sub('[ㅋ]{2,}', ' ', tp) # ㅋ 2번이상 지우기 
    tp = re.sub('[ㅎ]{2,}', ' ', tp) # ㅎ 2번이상 지우기 
    tp = re.sub('[ㅜ]{2,}', ' ', tp) # ㅜ 2번이상 지우기 
    tp = re.sub('[ㅠ]{2,}', ' ', tp) # ㅠ 2번이상 지우기
    tp = re.sub(r"[^ㄱ-ㅣ\s]", " ", tp) # 자음과 모음만 추출
    tp = re.sub('  +', ' ', tp) # 공백 2번 이상 지우기
    tp = repeat_normalize(tp, num_repeats =2)   
    return tp.strip()

#3. 자모 가져오기 
def get_jamo(df):
    jamo_list = []
    for idx in range(len(df)):
        ls = df['jaeum_moeum'][idx].split(" ") # 공백기준 나누기
        lls = [i for i in ls if i != ''] # 빈 값  없애기
        lls = [i for i in lls if i != ' '] # 공백은 없애기
        jamo_list = jamo_list + lls 
    return jamo_list 

#4. 빈도수로 정렬
def sortby_count(jamo_list):
    jamos = pd.DataFrame(columns = ['jamo','count'])
    jamos['jamo']= Counter(jamo_list).keys()
    jamos['count']= Counter(jamo_list).values()
    jamos = jamos.sort_values('count', ascending= False)
    jamos = jamos[jamos['jamo'] .str.len()> 1] # jamo 값이 최소 두글자 이상
    jamos = jamos[jamos['count'] > 4] # 빈도수가 적어도 5번 이상 나온 단어만 채택, 빈도수 변경 가능
    jamos = jamos.reset_index(drop= True) 
    return jamos

#5. 추가 필터링
def more_preprocessing(jamos):
    # 세글자가 동일한 글자인 경우
    same_index = []
    for idx, word in enumerate(jamos['jamo']):
        if len(word) == 3:
            if (word[0]== word[1]) and (word[1]==word[2]):
                same_index.append(idx)
    jamos.drop(same_index, axis = 0, inplace = True)
    jamos = jamos.reset_index(drop=True)
    return jamos

#6. 욕 DB로 제거
def profanity_filter(jamos):
    yok_db = []
    f = open("/home/sol4/workspace/DB/yoks.txt", 'r') 
    for line in f:
        yok_db.append(line.replace('\n',''))
    f.close()

    yok_idx = []
    for i in range(len(jamos)):
        for yok in yok_db:
            if yok in jamos['jamo'][i] :
                yok_idx.append(i)
    # print('욕 단어 탈락결과')
    # print(list(jamos.iloc[yok_idx]['jamo']))
    jamos.drop(yok_idx, axis=0, inplace = True)       
    jamos = jamos.reset_index(drop=True)
    return jamos

#7. 불용어 DB로 제거
def stopword_filter(jamos):
    nomean_db = []
    f = open("/home/sol4/workspace/DB/no_mean.txt", 'r')
    for line in f:
        nomean_db.append(line.replace('\n',''))
    f.close()

    nomean_idx = []
    for i in range(len(jamos)):
        for nomean in nomean_db:
            if nomean in jamos['jamo'][i] :
                nomean_idx.append(i)
    #print('불용어 단어 탈락결과')
    #print(list(jamos.iloc[nomean_idx]['jamo']))
    jamos.drop(nomean_idx, axis=0, inplace = True)       
    jamos = jamos.reset_index(drop=True)
    return jamos

#8. 이미 저장된 신조어 제거 
def ExistJamo_filter(jamos):
    try: 
        file_path = '/home/sol4/workspace/DB/final_jamo.xlsx'
        df = pd.read_excel(file_path)
        existjamo = df['jamo'].tolist()
        existjamo_idx = []
        for i in range(len(jamos)):
            for jamo in existjamo:
                if jamo == jamos['jamo'][i]: 
                    existjamo_idx.append(i)
        #print(jamos.iloc[existjamo_idx])
        jamos.drop(existjamo_idx, axis = 0, inplace = True)
        jamos = jamos.reset_index(drop=True)  
    except FileNotFoundError: 
        pass
    return jamos 

#9. 결과 가져오기
def get_result(jamos, df):
    result = pd.DataFrame(columns=['date', 'jamo', 'example'])
    jamos = jamos['jamo'].tolist()
    for jamo in jamos: 
        today = date.today()
        example = df['content'].str.contains(jamo)
        example_df = df[example]
        # 30자 이하 문장만 가져오기
        long_examples = example_df[example_df['content'].str.len() <= 30]['content'].head(2).tolist()
        # 만약 30자를 넘는 문장이 없을 경우, 30자 이상 문장 가져오기
        if len(long_examples) == 0:
            all_examples = example_df['content'].head(2).tolist()
            result = result.append({
                'date': today, 'jamo': jamo, 'example': all_examples
            }, ignore_index=True)
        else:
            result = result.append({
                'date': today, 'jamo': jamo, 'example': long_examples
            }, ignore_index=True)
    try: 
        file_path = '/home/sol4/workspace/DB/temp_jamo.xlsx' 
        temp_df = pd.read_excel(file_path, index_col=0)     
        temp_new_df = temp_df.append(result, ignore_index = True)
        temp_new_df.to_excel(file_path) 
    except FileNotFoundError: 
        result.to_excel('DB/temp_jamo.xlsx')
    return result 

