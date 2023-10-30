# 신조어 추출 모델 및 정기적인 신조어 사전 구축 방법 개발
- 지속적인 데이터 수집을 통한 신조어 사전 구축  
- 단일 입력 문장에 대한 신조어와 해당 신조어가 포함된 유사 문장 출력  
## 모델 출력 예시
- 임시 신조어 사전 결과 

![임시 신조어 사전 결과](https://github.com/twigfarm/letr-sol-New-Words-Detector/assets/123911402/b40aef73-7f8a-44c8-89ae-c9505a07f7b9)
* * *
- 단일 문장 신조어 예측, 유사 문장 예시 결과  

![단일 문장 예측 결과](https://github.com/twigfarm/letr-sol-New-Words-Detector/assets/123911402/8a05b521-bf32-43fa-bdb0-6b0f608d072a)
## 모델 구조


![모델 기능 구조](https://github.com/twigfarm/letr-sol-New-Words-Detector/assets/123911402/4eea3695-3ddb-4be4-a04a-bb92e83ef730)
- 커뮤니티 데이터 수집 통해 입력 문장을 받아 신조어 추출 및 검증 과정 순차적으로 진행    

![모델 구조](https://github.com/twigfarm/letr-sol-New-Words-Detector/assets/123911402/827a77ba-cbb3-4ead-96bc-da0aa56a301b)
## 모델 사용 방법 
- 임시 신조어 사전 구축 시

![임시 신조어 사전 구축 프로세스](https://github.com/twigfarm/letr-sol-New-Words-Detector/assets/123911402/b97a0452-94aa-435e-8638-2564e0794371)  
  
    크롤링 데이터, main_noun.py, main_jamo.py 스케쥴링 설정 후 실행
* * *  
- 단일 문장 신조어 예측 시 

![단일 문장 프로세스](https://github.com/twigfarm/letr-sol-New-Words-Detector/assets/123911402/1241733d-51a8-48e0-9925-034c02154dcd)

    main_sentence('입력 문장')으로 실행
    
* * *
- 사용자 설정 가능 옵션   
  - 크롤링  
    - 사용자가 원하는 목적에 맞는 사이트 선정 및 크롤링 작업 진행
    - 모델 데이터는 csv-제목(title), 내용(content) / json-댓글(comment)
    - sub_noun.py에서 저장 형태 변환 가능
    * * *
  - 데이터 로드
    - 크롤링 결과의 파일 경로 수정을 통해 모델 입력 데이터로 변환
    - 결과 값은 DataFrame 형태로 ‘content’ 칼럼에 텍스트 데이터는 필수
    * * *
  - 스케쥴링 및 자동화
    - dc, main_noun, main_jamo 각각 crontab 명령어 적용하여 원하는 시간에 스케줄링 적용하여 신조어 축적 자동화 
## 참여자 
> 트위그팜 SOL 4기  
> > 문다은 https://github.com/daeun-moon   
이석호 https://github.com/LSH0414   
정경원 https://github.com/mabeljeong
## Reference