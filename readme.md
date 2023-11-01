# 신조어 추출 모델 및 정기적인 신조어 사전 구축 방법 개발
- **신조어 탐지 통한 신조어 사전(TB) 구축** - 커뮤니티 데이터 수집을 통해 신조어 추출하고, 자동화로 정기적으로 업데이트되는 신조어 사전 구축
- **단일 문장 내 신조어 및 유사 문장 출력** - 단일 문장 입력시 해당 문장 내 신조어를 식별하고, 해당 신조어가 포함된 유사 문장을 출력
- **추출 가능 신조어** - 2글자 이상 1어절 명사형 한글 단어, 자모 단위 단어
## Requirements
requirements.txt 참고   
[표준국어대사전](https://stdict.korean.go.kr/openapi/openApiInfo.do), [papago API](https://developers.naver.com/products/papago/nmt/nmt.md) 필요

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
| 크롤링 | - 사용자는 원하는 목적에 맞는 사이트 선정 및 크롤링 작업 진행<br>  - 모델 데이터는 csv-제목(title), 내용(content) 및 json-댓글(comment)로 default 구성<br>  - sub_noun에서 데이터 형식 변경 가능 |
| 데이터 로드 | - 크롤링 작업 결과 파일의 경로 수정하여 모델 입력 데이터로 변환<br>  - 결과 값은 DataFrame 형태로 제공, ‘content’ 칼럼에 텍스트 데이터는 필수로 포함 |
| 스케쥴링 및 자동화 | - dc, main_noun, main_jamo를 사용하여 원하는 시간에 스케줄링 설정하여 신조어 탐지 과정 자동화 |

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
- [모두의 말뭉치](https://corpus.korean.go.kr/)
- [Soynlp Noun Extractor](https://pypi.org/project/soynlp/)
- [Konlpy Mecab, Okt](https://konlpy.org/ko/latest/index.html)
- [g2pK](https://github.com/Kyubyong/g2pK)
- [PyKoSpacing](https://github.com/haven-jeon/PyKoSpacing)
- [KcELECTRA-base-v2022](https://huggingface.co/beomi/KcELECTRA-base-v2022)
