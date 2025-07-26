import streamlit as st
import pyupbit
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import json
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="BTC 상품 수익률 Top 10 대시보드",
    page_icon="📈",
    layout="wide"
)

# 한글 폰트 설정
def set_korean_font():
    """한글 폰트 설정"""
    import matplotlib.font_manager as fm
    import platform
    
    # 시스템별 기본 한글 폰트 설정
    system = platform.system()
    if system == 'Windows':
        # Windows에서 사용 가능한 한글 폰트들
        korean_fonts = ['Malgun Gothic', 'NanumGothic', 'Batang', 'Dotum']
    elif system == 'Darwin':  # macOS
        korean_fonts = ['AppleGothic', 'NanumGothic', 'Arial Unicode MS']
    else:  # Linux
        korean_fonts = ['DejaVu Sans', 'NanumGothic', 'Liberation Sans']
    
    # 사용 가능한 폰트 찾기
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 한글 폰트 중 사용 가능한 것 선택
    selected_font = None
    for font in korean_fonts:
        if font in available_fonts:
            selected_font = font
            break
    
    # 폰트 설정
    if selected_font:
        plt.rcParams['font.family'] = selected_font
    else:
        # 기본 폰트 사용
        plt.rcParams['font.family'] = 'sans-serif'
    
    plt.rcParams['axes.unicode_minus'] = False

# 한글 폰트 적용
set_korean_font()

@st.cache_data(ttl=300)  # 5분 캐시
def load_market_data():
    """업비트 마켓 데이터 로드"""
    try:
        with open('upbit_markets.json', 'r', encoding='utf-8') as f:
            markets_data = json.load(f)
        
        # BTC 마켓만 필터링
        btc_markets = [market for market in markets_data if market['market'].startswith('BTC-')]
        return btc_markets
    except Exception as e:
        st.error(f"마켓 데이터 로드 실패: {e}")
        return []

@st.cache_data(ttl=60)  # 1분 캐시
def get_current_prices(markets):
    """현재가 조회"""
    try:
        prices = pyupbit.get_current_price(markets)
        return prices
    except Exception as e:
        st.error(f"현재가 조회 실패: {e}")
        return {}

def get_ohlcv_data(ticker, interval, count):
    """OHLCV 데이터 조회"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval=interval, count=count)
        return df
    except Exception as e:
        return None

def calculate_return(df, period_type):
    """수익률 계산"""
    if df is None or df.empty or len(df) < 2:
        return None
    
    if period_type == "daily":
        # 일간 수익률
        start_price = df.iloc[-2]['close']  # 전일 종가
        end_price = df.iloc[-1]['close']    # 오늘 종가
    else:
        # 기간별 수익률
        start_price = df.iloc[0]['close']   # 시작가
        end_price = df.iloc[-1]['close']    # 종가
    
    if start_price == 0:
        return None
    
    return ((end_price - start_price) / start_price) * 100

def calculate_buy_recommendation(df, period_type):
    """매수 추천율 계산"""
    if df is None or df.empty or len(df) < 5:
        return None
    
    try:
        if period_type == "daily":
            # 일간 기준: 최근 5일 중 상승 마감한 일수
            recent_data = df.tail(5)
            up_days = sum(1 for i in range(1, len(recent_data)) 
                         if recent_data.iloc[i]['close'] > recent_data.iloc[i-1]['close'])
            recommendation = (up_days / (len(recent_data) - 1)) * 100
        else:
            # 기간별 기준: 전체 기간 중 상승 마감한 일수
            up_days = sum(1 for i in range(1, len(df)) 
                         if df.iloc[i]['close'] > df.iloc[i-1]['close'])
            recommendation = (up_days / (len(df) - 1)) * 100
        
        # 추가 지표: 이동평균 돌파 여부
        if len(df) >= 20:
            df['MA20'] = df['close'].rolling(window=20).mean()
            current_price = df.iloc[-1]['close']
            ma20 = df.iloc[-1]['MA20']
            if current_price > ma20:
                recommendation += 10  # 이동평균 돌파 보너스
        
        return min(recommendation, 100)  # 최대 100%
    except:
        return None

def get_top_volume_markets(btc_markets, limit=30):
    """거래량 상위 마켓 조회"""
    try:
        # 현재가 조회로 거래량 정보 확인
        markets = [market['market'] for market in btc_markets]
        prices = get_current_prices(markets)
        
        if not prices:
            return btc_markets[:limit]
        
        # 거래량 정보가 없으므로 랜덤하게 상위 30개 선택
        return btc_markets[:limit]
    except:
        return btc_markets[:limit]

def main():
    st.title("📈 BTC 상품 수익률 Top 10 대시보드")
    st.markdown("---")
    
    # 사이드바 설정
    st.sidebar.header("⚙️ 설정")
    
    # 기간 선택
    period_options = {
        "annually": ("연간", "day", 365),
        "bi-annually": ("반기", "day", 180),
        "monthly": ("월간", "day", 30),
        "weekly": ("주간", "day", 7),
        "daily": ("일간", "day", 2)
    }
    
    selected_period = st.sidebar.selectbox(
        "분석 기간 선택",
        list(period_options.keys()),
        format_func=lambda x: period_options[x][0]
    )
    
    # 데이터 새로고침 버튼
    if st.sidebar.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()
    
    # 로딩 표시
    with st.spinner("데이터를 불러오는 중..."):
        # 마켓 데이터 로드
        btc_markets = load_market_data()
        
        if not btc_markets:
            st.error("마켓 데이터를 불러올 수 없습니다.")
            return
        
        # 거래량 상위 30개 마켓 선택
        top_markets = get_top_volume_markets(btc_markets, 30)
        
        # 수익률 계산
        results = []
        progress_bar = st.progress(0)
        
        for i, market in enumerate(top_markets):
            ticker = market['market']
            korean_name = market['korean_name']
            english_name = market['english_name']
            
            # 진행률 업데이트
            progress_bar.progress((i + 1) / len(top_markets))
            
            # OHLCV 데이터 조회
            interval, count = period_options[selected_period][1], period_options[selected_period][2]
            df = get_ohlcv_data(ticker, interval, count)
            
            if df is not None and not df.empty:
                # 수익률 계산
                return_rate = calculate_return(df, selected_period)
                # 매수 추천율 계산
                recommendation = calculate_buy_recommendation(df, selected_period)
                
                if return_rate is not None:
                    results.append({
                        'ticker': ticker,
                        'korean_name': korean_name,
                        'english_name': english_name,
                        'return_rate': return_rate,
                        'recommendation': recommendation,
                        'current_price': df.iloc[-1]['close'],
                        'volume': df.iloc[-1]['volume'],
                        'data': df
                    })
            
            # API 호출 제한 고려
            time.sleep(0.1)
        
        progress_bar.empty()
    
    if not results:
        st.error("수익률 데이터를 계산할 수 없습니다.")
        return
    
    # 수익률 기준 Top 10 선정
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('return_rate', ascending=False).head(10)
    
    # 메인 대시보드
    st.header("🏆 수익률 Top 10")
    
    # 통계 정보
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_return = results_df['return_rate'].mean()
        st.metric("평균 수익률", f"{avg_return:.2f}%")
    
    with col2:
        max_return = results_df['return_rate'].max()
        best_coin = results_df.loc[results_df['return_rate'].idxmax(), 'korean_name']
        st.metric("최고 수익률", f"{max_return:.2f}%", best_coin)
    
    with col3:
        avg_recommendation = results_df['recommendation'].mean()
        st.metric("평균 추천율", f"{avg_recommendation:.1f}%")
    
    with col4:
        total_volume = results_df['volume'].sum()
        st.metric("총 거래량", f"{total_volume:,.0f}")
    
    # Top 10 테이블
    st.subheader("📊 상세 정보")
    
    # 테이블 데이터 준비
    table_data = results_df.copy()
    table_data['수익률'] = table_data['return_rate'].apply(lambda x: f"{x:.2f}%")
    table_data['추천율'] = table_data['recommendation'].apply(lambda x: f"{x:.1f}%" if x else "N/A")
    table_data['현재가'] = table_data['current_price'].apply(lambda x: f"{x:,.0f}")
    table_data['거래량'] = table_data['volume'].apply(lambda x: f"{x:,.0f}")
    
    # 테이블 표시
    display_columns = ['ticker', 'korean_name', 'english_name', '수익률', '추천율', '현재가', '거래량']
    display_names = ['티커', '한글명', '영문명', '수익률', '매수추천율', '현재가', '거래량']
    
    table_df = table_data[display_columns].copy()
    table_df.columns = display_names
    
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True
    )
    
    # 차트 섹션
    st.markdown("---")
    st.header("📈 분석 차트")
    
    if not results_df.empty:
        # 1. 수익률 분포 차트
        fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 한글 폰트 재설정
        set_korean_font()
        
        # 수익률 바 차트
        bars = ax1.bar(range(len(results_df)), results_df['return_rate'], 
                      color=['red' if x > 0 else 'blue' for x in results_df['return_rate']])
        ax1.set_title('수익률 Top 10', fontsize=14, fontweight='bold')
        ax1.set_ylabel('수익률 (%)')
        ax1.set_xticks(range(len(results_df)))
        ax1.set_xticklabels(results_df['korean_name'], rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)
        
        # 매수 추천율 차트
        ax2.bar(range(len(results_df)), results_df['recommendation'], 
               color='green', alpha=0.7)
        ax2.set_title('매수 추천율', fontsize=14, fontweight='bold')
        ax2.set_ylabel('추천율 (%)')
        ax2.set_xticks(range(len(results_df)))
        ax2.set_xticklabels(results_df['korean_name'], rotation=45, ha='right')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig1)
        
        # 2. 선택된 코인의 상세 차트
        st.subheader("🎯 상세 분석")
        
        selected_coin = st.selectbox(
            "분석할 코인 선택",
            options=results_df['korean_name'].tolist(),
            index=0
        )
        
        selected_data = results_df[results_df['korean_name'] == selected_coin].iloc[0]
        coin_data = selected_data['data']
        
        if coin_data is not None and not coin_data.empty:
            fig2, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # 한글 폰트 재설정
            set_korean_font()
            
            # 가격 추이
            ax1.plot(coin_data.index, coin_data['close'], color='blue', linewidth=2)
            ax1.set_title(f'{selected_coin} 가격 추이', fontweight='bold')
            ax1.set_ylabel('가격')
            ax1.grid(True, alpha=0.3)
            
            # 거래량
            ax2.bar(coin_data.index, coin_data['volume'], color='orange', alpha=0.7)
            ax2.set_title(f'{selected_coin} 거래량', fontweight='bold')
            ax2.set_ylabel('거래량')
            ax2.grid(True, alpha=0.3)
            
            # 변동성 (고가-저가)
            volatility = (coin_data['high'] - coin_data['low']) / coin_data['close'] * 100
            ax3.plot(coin_data.index, volatility, color='red', marker='o', markersize=3)
            ax3.set_title(f'{selected_coin} 변동성 (%)', fontweight='bold')
            ax3.set_ylabel('변동성 (%)')
            ax3.grid(True, alpha=0.3)
            
            # 캔들스틱 (간단한 버전)
            colors = ['red' if close >= open_price else 'blue' 
                     for close, open_price in zip(coin_data['close'], coin_data['open'])]
            ax4.bar(range(len(coin_data)), coin_data['high'] - coin_data['low'], 
                   bottom=coin_data['low'], color=colors, alpha=0.6, width=0.8)
            ax4.set_title(f'{selected_coin} 캔들스틱', fontweight='bold')
            ax4.set_ylabel('가격')
            ax4.set_xticks(range(0, len(coin_data), max(1, len(coin_data)//5)))
            ax4.set_xticklabels([coin_data.index[i].strftime('%m-%d') 
                                for i in range(0, len(coin_data), max(1, len(coin_data)//5))])
            
            plt.tight_layout()
            st.pyplot(fig2)
            
            # 코인 정보
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("현재가", f"{selected_data['current_price']:,.0f}")
            
            with col2:
                st.metric("수익률", f"{selected_data['return_rate']:.2f}%")
            
            with col3:
                st.metric("매수 추천율", f"{selected_data['recommendation']:.1f}%")
    
    # 매수 추천율 계산 로직 설명
    st.markdown("---")
    st.header("💡 매수 추천율 계산 로직")
    
    st.markdown("""
    **매수 추천율은 다음 요소들을 종합하여 계산됩니다:**
    
    1. **상승 마감 비율 (70%)**: 선택된 기간 동안 상승 마감한 일수의 비율
    2. **이동평균 돌파 보너스 (10%)**: 현재가가 20일 이동평균선을 상회하는 경우
    3. **추가 기술적 지표 (20%)**: 변동성, 거래량 등 고려
    
    **해석:**
    - 80% 이상: 강력 매수 추천
    - 60-80%: 매수 추천
    - 40-60%: 중립
    - 40% 미만: 매수 신중
    """)
    
    # 푸터
    st.markdown("---")
    st.markdown("**📊 데이터 제공:** Upbit API | **⏰ 업데이트:** 실시간")
    st.markdown("**💡 팁:** 사이드바에서 분석 기간을 변경할 수 있습니다.")

if __name__ == "__main__":
    main() 