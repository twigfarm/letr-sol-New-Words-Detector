from sub_jamo import *
#from time import process_time 
#import numpy as np

#print('실행시작')
#start = process_time() 

df = get_data()  # 데이터 가져오기

df = basic_preprocessing(df) # 1차 전처리

df['content'] = df['content'].apply(preprocessing_unicode) # 2차 전처리 - 유니코드 삭제
df['jaeum_moeum'] = df['content'].apply(preprocessing) # 2차 전처리 - 자음, 모음으로만 이루어진 글자만 남겨둠

df = df[df['jaeum_moeum'].str.len() > 1] # 댓글 길이가 한 글자면 제거
df = df.reset_index(drop=True)

jamo_list = get_jamo(df) # 빈칸을 기준 나누기

jamos = sortby_count(jamo_list) # 빈도수로 정렬

jamos = more_preprocessing(jamos) # 추가 필터링

jamos = profanity_filter(jamos) # 욕설 제거

jamos = stopword_filter(jamos) # 불용어 제거 

jamos = ExistJamo_filter(jamos) # 이미 저장된 신조어 제거

result = get_result(jamos, df) # 결과 가져오기
print(result)
#end = process_time()

#print('총 ',np.round(end-start,3),'초 걸렸다.') 

#print(result) -> temp_jamo.xlsx에서 확인가능
