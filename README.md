# project-Earth 프로젝트 (with wecode35) :tada:
## 프로젝트 개요 :speech_balloon:

### 프로젝트 목표
- 산업 현장에 설치된 CCTV 영상 및 영상분석 정보 수집 Pipeline
- 해당 정보를 토대로 현황 모니터링 및 공정률 분석이 가능한 플랫폼 개발

### 프로젝트 핵심 기능
- CCTV 영상정보수집
- 영상 분석 데이터 수집
- 수집 데이터 전처리 및 가공
- 분석 결과를 통한 현황 모니터링 및 공정률 분석
- 고객사 insight 제공

### 개발 기간 및 인원
- 개발 기간 : 2022-08-16 ~ 2022-09-06 (22일)
- 개발 인원 : 4 명
- Frontend : 노정은, 오창훈
- Backend  : 홍현진, 황유정

#### 적용 기술
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white"/>&nbsp;
<img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=Django&logoColor=white"/>&nbsp;
<img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=MySQL&logoColor=white"/>&nbsp;
<img src="https://img.shields.io/badge/miniconda3-44A833?style=for-the-badge&logo=anaconda&logoColor=white">&nbsp;
<img src="https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=Postman&logoColor=white"/>&nbsp;

## 프로젝트 구조
### DB 모델링
<img width="1020" alt="스크린샷 2022-09-07 오후 12 50 01" src="https://user-images.githubusercontent.com/94777292/188792983-0e94aa45-ddef-476e-9cab-7c44e102770c.png">

## 📄 구현 기능에 대한 소개

### 중장비 상태 모니터링 및 관리 (황유정)

1.실시간 데이터(mqtt)를 이용하여 실시간 중장비 상태 별 모니터링
 - 실시간, 장비 타입, 장비 상태를 10초 단위로 업데이트하여 모니터링 합니다. 
2.Q객체를 활용한 중장비 관리 페이지 리스트 기능 구현
 - 쿼리 파라미터로 받은 fliter 값으로 장비 타입별, 작업 구역을 flitering해 중장비 리스트 구현하였습니다. 초기 정렬은 중장비 시리얼 넘버로 정렬하였습니다. 
3.중장비 세부 페이지 및 해당 장비 별 일간 가동률 표시하고 수정, 삭제 기능을 제공합니다.
 - 장비별 월~토 가동률을 람다식으로 계산하여 제공하며, 장비 정보 수정과 삭제 기능을 구현하였습니다. 
4. Unit test 작성

#### 배운 점 & 아쉬운 점

* Mqtt protocol이 무엇인가 ?
 - 사물 인터넷에 대해 이런 프로토콜이 있는지 처음 알게 되었습니다. 실시간으로 DB에 저장하는 데이터를 10초 단위로 꺼내서 모니터링 API로 구현할 때 시간 계산이 얼마나 복잡하고 어려운지 알게 되었고, 스레드를 활용하여 서버 가동 시 mqtt 데이터도 자동으로 수집하면서 API도 구동하는 구조를 생각했으나.. 여러 시도 끝에 해내지 못해 아쉬웠습니다  :sob:

* *Q 객체를 사용한 flitering 구현
 - 장고에서 제공하는 Q 객체를 활용하여 여러 필터링 결괏값을 담아 전달하는 기능 구현을 해보면서 개념을 이해하는데 집중했습니다. </br> 생각보다 쉬워 보였는데 request로 받는 값을 먼저 지정하냐 안 사냐에 차이에 따른 필터 객체 값이 달라져 테스트를 많이 했고, 결과적으로는 원하는 결과를 담아내는데 성공했습니다.

* 날짜 및 시간 계산
 - 값을 계산하는 로직이 어렵다는 것을 알고있었지만 실제로 구현해보려고하니 작은 오차에도 결과 값이 달라지는 것을 보면서 간단하게 생각할게 아니구나 느꼈습니다. 요일에 따른 가동률을 계산할 때도 공휴일 또는 기상악화 같은 예외 상황이 발생하면 어떻게 해야할지 고민했으나 디테일한 부분까지 생각하여 로직을 작성하진 못했습니다.  

#### 🎬 시연

https://user-images.githubusercontent.com/94777292/188795939-b4c2e4aa-c232-4533-8fdf-a8fe04c7c666.mov

## API 명세서

<img alt="스크린샷 2022-09-07 오후 2 09 07" src="https://user-images.githubusercontent.com/94777292/188793402-c7207951-7871-4fca-94f3-3690fe80e341.png">

## 프로젝트 배포 주소

http://175.209.190.39:19999/ **(일정 기간 이후 접속이 불가할 수 있습니다.)**


#### Reference
이 프로젝트는 학습 목적 및 상업 목적으로 만들었기 때문에 코드를 활용하여 이득을 취하거나 무단 배포할 경우 법적으로 문제될 수 있습니다.
