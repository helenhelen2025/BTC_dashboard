# BTC 상품 수익률 Top 10 대시보드

## 📊 프로젝트 개요
Upbit Open API를 활용하여 BTC 마켓 상품들의 수익률을 분석하고 Top 10을 시각화하는 Streamlit 대시보드입니다.

## 🚀 주요 기능
- **상위 거래량 30개 우선 조회**: API 호출 제한을 고려한 효율적인 데이터 수집
- **수익률 Top 10 선정**: 선택한 기간 기준으로 수익률 상위 10개 코인 표시
- **다양한 기간 필터**: annually, bi-annually, monthly, weekly, daily 선택 가능
- **매수 추천율 계산**: 상승 마감 비율 + 이동평균 돌파 보너스로 계산
- **한글 폰트 지원**: NanumGothic 폰트로 차트의 한글이 깨지지 않음
- **데이터 새로고침**: 사이드바의 새로고침 버튼으로 최신 데이터 업데이트

## 📈 대시보드 구성
- **통계 정보**: 평균 수익률, 최고 수익률, 평균 추천율, 총 거래량
- **Top 10 테이블**: 티커, 한글명, 영문명, 수익률, 매수추천율, 현재가, 거래량
- **분석 차트**: 
  - 수익률 분포 차트 (상승/하락 색상 구분)
  - 매수 추천율 차트
  - 선택한 코인의 상세 분석 (가격 추이, 거래량, 변동성, 캔들스틱)

## 💡 매수 추천율 계산 로직
매수 추천율은 다음 요소들을 종합하여 계산됩니다:
1. **상승 마감 비율 (70%)**: 선택된 기간 동안 상승 마감한 일수의 비율
2. **이동평균 돌파 보너스 (10%)**: 현재가가 20일 이동평균선을 상회하는 경우
3. **추가 기술적 지표 (20%)**: 변동성, 거래량 등 고려

**해석:**
- 80% 이상: 강력 매수 추천
- 60-80%: 매수 추천
- 40-60%: 중립
- 40% 미만: 매수 신중

## 🛠️ 설치 및 실행

### 로컬 실행
```bash
pip install -r requirements.txt
streamlit run btc_dashboard.py
```

### Streamlit Cloud 배포
1. GitHub에 코드 업로드
2. [Streamlit Cloud](https://share.streamlit.io/)에서 새 앱 생성
3. GitHub 저장소 연결
4. 메인 파일 경로: `btc_dashboard.py`
5. 배포 완료!

## 📁 파일 구조
```
├── btc_dashboard.py          # 메인 대시보드 파일
├── requirements.txt          # Python 패키지 의존성
├── packages.txt             # 시스템 패키지 의존성 (Streamlit Cloud용)
├── .streamlit/config.toml   # Streamlit 설정
├── upbit_markets.json       # 업비트 마켓 데이터
└── README.md               # 프로젝트 설명서
```

## 🔧 한글 폰트 설정
- **로컬 환경**: 시스템 기본 한글 폰트 자동 감지
- **Streamlit Cloud**: NanumGothic 폰트 자동 다운로드 및 적용
- **폰트 우선순위**: Malgun Gothic → NanumGothic → 시스템 기본 폰트

## 📊 데이터 제공
- **API**: Upbit Open API
- **업데이트**: 실시간 (5분 캐시)
- **데이터 범위**: 최대 1년 전부터 최근까지

## 🎯 사용법
1. 사이드바에서 분석 기간 선택 (annually, bi-annually, monthly, weekly, daily)
2. 데이터 새로고침 버튼으로 최신 데이터 업데이트
3. Top 10 테이블에서 코인 정보 확인
4. 차트에서 시각적 분석
5. 상세 분석에서 특정 코인 선택하여 자세한 정보 확인

## 📝 라이선스
이 프로젝트는 교육 목적으로 제작되었습니다.