#단어 db에 등록 및 삭제하는 함수 
#type ('noun' or 'jamo') word('넣고 싶은 단어') db('욕' or '불용어' or '신조어')
#입력 예시: insert_word('noun', '바보', '욕') insert_word('jamo', 'ㅈㄱㄴ', '신조어')
#입력 예시: delete_word('noun', '바보', '욕') delete_word('jamo', 'ㅈㄱㄴ', '신조어') 

import pandas as pd 
 
def insert_word(type, word, db):
    if type == 'noun':
        if db == '욕':
            with open ('/home/sol4/workspace/DB/yoks.txt', 'a') as yok_db: 
                yok_db.write(word+'\n')
            print(word, '단어가', db, 'db에 추가 되었습니다')
        elif db == '불용어':
            with open('/home/sol4/workspace/DB/no_mean.txt', 'a') as stopword_db:
                stopword_db.write(word+'\n')
            print(word, '단어가', db, 'db에 추가 되었습니다')
        elif db == '신조어':
            try: 
                file_path = '/home/sol4/workspace/DB/final_noun.xlsx' 
                df = pd.read_excel(file_path, index_col = False, engine='openpyxl')
                df = df.append({'noun': word}, ignore_index=True)
                df.to_excel(file_path, index=False)
                print(word, '단어가', db, 'db에 추가 되었습니다')        
            except FileNotFoundError:
                df = pd.DataFrame({'noun': [word]})
                print(df)
                df.to_excel('DB/final_noun.xlsx', index=False)
                print(word, '단어가', db, 'db에 추가 되었습니다')     
        else: 
            print('유효하지 않은 db 유형입니다. 올바른 db명을 적어주세요.')
    elif type == 'jamo':
        if db == '욕':
            with open ('/home/sol4/workspace/DB/yoks.txt', 'a') as yok_db: 
                yok_db.write(word+'\n')
            print(word, '단어가', db, 'db에 추가 되었습니다')
        elif db == '불용어':
            with open('/home/sol4/workspace/DB/no_mean.txt', 'a') as stopword_db:
                stopword_db.write(word+'\n')
            print(word, '단어가', db, 'db에 추가 되었습니다')
        elif db == '신조어':
            try: 
                file_path = '/home/sol4/workspace/DB/final_jamo.xlsx' 
                df = pd.read_excel(file_path, index_col = False, engine='openpyxl')
                df = df.append({'jamo': word}, ignore_index=True)
                df.to_excel(file_path, index=False)
                print(word, '단어가', db, 'db에 추가 되었습니다')        
            except FileNotFoundError:
                df = pd.DataFrame({'jamo': [word]})
                df.to_excel('DB/final_jamo.xlsx', index=False)
                print(word, '단어가', db, 'db에 추가 되었습니다')
        else: 
            print('유효하지 않은 db 유형입니다. 올바른 db명을 적어주세요.')         
    else: 
        print('입력을 다시 확인해주세요.')
    return 
    
#단어 db에서 삭제하는 함수
def delete_word(type, word, db): 
    if type == 'noun':
        if db == '욕':
            with open ('/home/sol4/workspace/DB/yoks.txt', 'r')as yok_db: 
                lines = yok_db.readlines()
            with open('/home/sol4/workspace/DB/yoks.txt', 'w') as yok_db:
                for line in lines:
                    if line.strip() != word:
                        yok_db.write(line)
            print(word, '단어가', db, 'db에서 삭제 되었습니다')
        elif db == '불용어':
            with open ('/home/sol4/workspace/DB/no_mean.txt', 'r') as stopword_db: 
                lines = stopword_db.readlines()
            with open('/home/sol4/workspace/DB/no_mean.txt', 'w') as stopword_db: 
                for line in lines:
                    if line.strip() != word:
                        stopword_db.write(line)
            print(word, '단어가', db, 'db에서 삭제 되었습니다')
        elif db == '신조어': 
            file_path = '/home/sol4/workspace/DB/final_noun.xlsx'
            df = pd.read_excel(file_path, index_col=False)
            df = df[df['noun'] != word]
            df.to_excel(file_path, index=False)
            print(word, '단어가', db, 'db에서 삭제 되었습니다')        
        else: 
            print('유효하지 않은 db 유형입니다. 올바른 db명을 적어주세요.')
    elif type == 'jamo':
        if db == '욕':
            with open ('/home/sol4/workspace/DB/yoks.txt', 'r')as yok_db: 
                lines = yok_db.readlines()
            with open('/home/sol4/workspace/DB/yoks.txt', 'w') as yok_db:
                for line in lines:
                    if line.strip() != word:
                        yok_db.write(line)
            print(word, '단어가', db, 'db에서 삭제 되었습니다')
        elif db == '불용어':
            with open ('/home/sol4/workspace/DB/no_mean.txt', 'a') as stopword_db: 
                lines = stopword_db.readlines()
            with open('/home/sol4/workspace/DB/no_mean.txt', 'w') as stopword_db: 
                for line in lines:
                    if line.strip() != word:
                        stopword_db.write(line)
            print(word, '단어가', db, 'db에서 삭제 되었습니다')
        elif db == '신조어':
            file_path = '/home/sol4/workspace/DB/final_jamo.xlsx'
            df = pd.read_excel(file_path, index_col=False)
            df = df[df['jamo'] != word]
            df.to_excel(file_path, index=False)
            print(word, '단어가', db, 'db에서 삭제 되었습니다')
        else: 
            print('유효하지 않은 db 유형입니다. 올바른 db명을 적어주세요.')        
    else: 
        print('입력을 다시 확인해주세요.')
    return 
