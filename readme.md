# 신조어 추출 모델 및 정기적인 신조어 사전 구축 방법 개발

- 신조어 탐지 통한 신조어 사전(TB) 구축  
- 단일 입력 문장에 포함된 신조어와 해당 신조어가 포함된 유사 문장 출력 
## Requirements
requirements.txt 참고 

## 모델 구조
<div align="center"> 
  <img src="https://github.com/twigfarm/letr-sol-New-Words-Detector/assets/123911402/d4bced69-259a-4eb4-bba0-388aaab01220" width="550">
</div> 

## 모델 사용 방법 
- 신조어 사전 구축 시

![신조어사전 구축 프로세스(small)](https://github.com/twigfarm/letr-sol-New-Words-Detector/assets/123911402/2ab30a1a-5df4-4ce0-be9c-31d9475ab923)
  
    크롤링 데이터, main_noun.py, main_jamo.py 스케쥴링 설정 후 실행
* * *  
- 단일 문장에서 신조어 예측 시 

![단일 문장 프로세스(small)](https://github.com/twigfarm/letr-sol-New-Words-Detector/assets/123911402/b896258e-df60-471e-b590-40e31db3055c)

    main_sentence.predict('입력 문장')으로 실행
    
* * *
- 사용자 설정 가능 옵션   


| 옵션 | 설명 |
|------|------|
| 크롤링 | - 사용자가 원하는 목적에 맞는 사이트 선정 및 크롤링 작업 진행\n  - 모델 데이터는 csv-제목(title), 내용(content) / json-댓글(comment)\n  - sub_noun.py에서 저장 형태 변환 가능\n|
| 데이터 로드 | - 크롤링 결과의 파일 경로 수정을 통해 모델 입력 데이터로 변환\n  - 결과 값은 DataFrame 형태로 ‘content’ 칼럼에 텍스트 데이터는 필수\n |
| 스케쥴링 및 자동화 | - dc, main_noun, main_jamo 각각 crontab 명령어 적용하여 원하는 시간에 스케줄링 적용하여 신조어 축적 자동화 |

## 모델 출력 예시
- 임시 신조어 사전 결과 

![임시 신조어 사전 결과(SMALL)](https://github.com/twigfarm/letr-sol-New-Words-Detector/assets/123911402/e5c6b81b-e517-4e16-9bb6-6a5cbc6d9f67)
* * *
- 단일 문장 신조어 예측 결과  

![단일문장예측결과(SMALL)](https://github.com/twigfarm/letr-sol-New-Words-Detector/assets/123911402/e89bd045-6eda-425b-aab3-109fcd89adc0)

## 참여자 
> 트위그팜 SOL 4기  
> > 문다은 https://github.com/daeun-moon   
이석호 https://github.com/LSH0414   
정경원 https://github.com/mabeljeong
## Reference
- 추가예정
