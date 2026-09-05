import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title="주식 비교 앱",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 따뜻한 톤 커스텀 스타일
st.markdown("""
    <style>
    .main {
        background-color: #FFF8F0;
    }
    .metric-card {
        background: linear-gradient(135deg, #FFE5D9, #FFF0E6);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #FF8C42;
    }
    </style>
    """, unsafe_allow_html=True)

# 제목과 설명
st.title("📊 주식 비교 앱")
st.markdown("**2개의 종목을 나란히 비교할 수 있습니다.**")
st.markdown("예) `005930.KS` (삼성전자), `AAPL` (애플)")

# ===== 1. 종목 입력 (2개 입력창) =====
st.markdown("---")
st.markdown("### 📝 종목 선택")

ticker_col1, ticker_col2 = st.columns(2)

with ticker_col1:
    ticker1 = st.text_input(
        "첫 번째 종목 코드",
        placeholder="예: 005930.KS 또는 AAPL",
        label_visibility="collapsed"
    ).strip().upper()

with ticker_col2:
    ticker2 = st.text_input(
        "두 번째 종목 코드 (선택사항)",
        placeholder="예: 000660.KS 또는 MSFT",
        label_visibility="collapsed"
    ).strip().upper()

# ===== 2. 기간 선택 (버튼) =====
st.markdown("---")
st.markdown("### 📅 기간 선택")

# 버튼 레이아웃
period_col1, period_col2, period_col3, period_col4 = st.columns(4)

with period_col1:
    if st.button("📆 1개월", use_container_width=True):
        st.session_state.selected_period = "1month"

with period_col2:
    if st.button("📆 6개월", use_container_width=True):
        st.session_state.selected_period = "6months"

with period_col3:
    if st.button("📆 1년", use_container_width=True):
        st.session_state.selected_period = "1year"

with period_col4:
    if st.button("📆 5년", use_container_width=True):
        st.session_state.selected_period = "5years"

# 기본값 설정 (1년)
if "selected_period" not in st.session_state:
    st.session_state.selected_period = "1year"

# 선택된 기간 표시
period_display = {
    "1month": "1개월",
    "6months": "6개월",
    "1year": "1년",
    "5years": "5년"
}
st.markdown(f"**선택된 기간**: 🕐 {period_display[st.session_state.selected_period]}")

# ===== 3. 기간에 따른 날짜 계산 함수 =====
def get_date_range(period):
    """
    선택된 기간에 따라 시작날짜와 종료날짜를 계산
    """
    end_date = datetime.now()
    
    if period == "1month":
        start_date = end_date - timedelta(days=30)
    elif period == "6months":
        start_date = end_date - timedelta(days=180)
    elif period == "1year":
        start_date = end_date - timedelta(days=365)
    elif period == "5years":
        start_date = end_date - timedelta(days=365*5)
    
    return start_date, end_date

# ===== 4. 데이터 조회 함수 =====
@st.cache_data
def get_stock_data(ticker_code, start_date, end_date):
    """
    yfinance로 주가 데이터를 불러옴
    """
    try:
        # 주가 데이터 다운로드
        data = yf.download(
            ticker_code,
            start=start_date,
            end=end_date,
            progress=False
        )
        
        if data.empty:
            return None
        
        return data
    except Exception as e:
        return None

# ===== 5. 종목 정보 조회 함수 =====
def get_stock_info(ticker_code):
    """
    종목의 현재 정보를 불러옴
    """
    try:
        ticker_obj = yf.Ticker(ticker_code)
        info = ticker_obj.info
        return info
    except:
        return None

# ===== 6. 메인 로직 =====
st.markdown("---")

if ticker1:
    # 선택된 기간의 시작날짜와 종료날짜 구하기
    start_date, end_date = get_date_range(st.session_state.selected_period)
    
    # 데이터 로딩
    with st.spinner(f"📥 {ticker1} 데이터를 불러오는 중..."):
        stock_data1 = get_stock_data(ticker1, start_date, end_date)
        stock_info1 = get_stock_info(ticker1)
    
    # ticker2가 입력된 경우
    if ticker2:
        with st.spinner(f"📥 {ticker2} 데이터를 불러오는 중..."):
            stock_data2 = get_stock_data(ticker2, start_date, end_date)
            stock_info2 = get_stock_info(ticker2)
    else:
        stock_data2 = None
        stock_info2 = None
    
    # ===== 데이터 검증 =====
    if stock_data1 is not None and not stock_data1.empty:
        # 지표 카드 표시
        st.markdown("### 💰 지표")
        
        # 변화율 계산
        current_price1 = stock_data1['Close'].iloc[-1]
        period_ago_price1 = stock_data1['Close'].iloc[0]
        change_amount1 = current_price1 - period_ago_price1
        change_percent1 = (change_amount1 / period_ago_price1) * 100
        
        # 1열 또는 2열 레이아웃 결정
        if ticker2 and stock_data2 is not None and not stock_data2.empty:
            # 2개 종목 비교: 2열 레이아웃
            metric_col1, metric_col2 = st.columns(2)
            
            with metric_col1:
                st.markdown(f"#### 🔹 {ticker1}")
                sub_col1, sub_col2, sub_col3 = st.columns(3)
                
                with sub_col1:
                    st.metric(
                        label="현재가",
                        value=f"{current_price1:,.2f}"
                    )
                
                with sub_col2:
                    st.metric(
                        label="등락률",
                        value=f"{change_percent1:.2f}%",
                        delta=f"{change_amount1:,.2f}"
                    )
                
                with sub_col3:
                    st.metric(
                        label="최고가",
                        value=f"{stock_data1['High'].max():,.2f}"
                    )
            
            # 두 번째 종목 지표
            current_price2 = stock_data2['Close'].iloc[-1]
            period_ago_price2 = stock_data2['Close'].iloc[0]
            change_amount2 = current_price2 - period_ago_price2
            change_percent2 = (change_amount2 / period_ago_price2) * 100
            
            with metric_col2:
                st.markdown(f"#### 🔹 {ticker2}")
                sub_col1, sub_col2, sub_col3 = st.columns(3)
                
                with sub_col1:
                    st.metric(
                        label="현재가",
                        value=f"{current_price2:,.2f}"
                    )
                
                with sub_col2:
                    st.metric(
                        label="등락률",
                        value=f"{change_percent2:.2f}%",
                        delta=f"{change_amount2:,.2f}"
                    )
                
                with sub_col3:
                    st.metric(
                        label="최고가",
                        value=f"{stock_data2['High'].max():,.2f}"
                    )
        else:
            # 1개 종목: 3열 레이아웃
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.metric(
                    label="💰 현재가",
                    value=f"{current_price1:,.2f}"
                )
            
            with metric_col2:
                st.metric(
                    label="📈 등락률",
                    value=f"{change_percent1:.2f}%",
                    delta=f"{change_amount1:,.2f}"
                )
            
            with metric_col3:
                st.metric(
                    label="🎯 최고가",
                    value=f"{stock_data1['High'].max():,.2f}"
                )
        
        # ===== 7. 주가 그래프 =====
        st.markdown("---")
        st.markdown("### 📊 주가 추이")
        
        # Plotly 그래프 생성
        fig = go.Figure()
        
        # 첫 번째 종목 라인 (왼쪽 Y축)
        fig.add_trace(go.Scatter(
            x=stock_data1.index,
            y=stock_data1['Close'],
            mode='lines',
            name=f'{ticker1} 종가',
            line=dict(
                color='#FF8C42',  # 따뜻한 주황색
                width=3
            ),
            yaxis='y'
        ))
        
        # 두 번째 종목 추가 (있는 경우)
        if ticker2 and stock_data2 is not None and not stock_data2.empty:
            fig.add_trace(go.Scatter(
                x=stock_data2.index,
                y=stock_data2['Close'],
                mode='lines',
                name=f'{ticker2} 종가',
                line=dict(
                    color='#6C63FF',  # 보라색
                    width=3
                ),
                yaxis='y2'
            ))
            
            # 두 번째 Y축 추가 (두 종목의 가격대가 다를 수 있으므로)
            fig.update_layout(
                yaxis2=dict(
                    title=f"{ticker2} 주가",
                    overlaying='y',
                    side='right'
                )
            )
        
        # 그래프 레이아웃 설정
        fig.update_layout(
            title=f"{ticker1}" + (f" vs {ticker2}" if ticker2 else "") + " - 주가 비교",
            xaxis_title="날짜",
            yaxis_title=f"{ticker1} 주가",
            template="plotly_white",
            hovermode='x unified',
            height=500,
            font=dict(size=12),
            margin=dict(l=60, r=60, t=80, b=60),
            plot_bgcolor='rgba(255, 248, 240, 0.5)',
            paper_bgcolor='rgba(255, 255, 255, 0.8)'
        )
        
        # 그래프 표시
        st.plotly_chart(fig, use_container_width=True)
        
        # ===== 8. 통계 정보 (각 종목별) =====
        st.markdown("---")
        st.markdown("### 📋 통계 정보")
        
        if ticker2 and stock_data2 is not None and not stock_data2.empty:
            # 2개 종목 비교
            stat_col1, stat_col2 = st.columns(2)
            
            with stat_col1:
                st.markdown(f"#### {ticker1}")
                stats1_col1, stats1_col2, stats1_col3, stats1_col4 = st.columns(4)
                
                with stats1_col1:
                    st.metric(
                        label="최고가",
                        value=f"{stock_data1['High'].max():,.2f}"
                    )
                
                with stats1_col2:
                    st.metric(
                        label="최저가",
                        value=f"{stock_data1['Low'].min():,.2f}"
                    )
                
                with stats1_col3:
                    st.metric(
                        label="평균가",
                        value=f"{stock_data1['Close'].mean():,.2f}"
                    )
                
                with stats1_col4:
                    st.metric(
                        label="거래량",
                        value=f"{stock_data1['Volume'].mean():,.0f}"
                    )
            
            with stat_col2:
                st.markdown(f"#### {ticker2}")
                stats2_col1, stats2_col2, stats2_col3, stats2_col4 = st.columns(4)
                
                with stats2_col1:
                    st.metric(
                        label="최고가",
                        value=f"{stock_data2['High'].max():,.2f}"
                    )
                
                with stats2_col2:
                    st.metric(
                        label="최저가",
                        value=f"{stock_data2['Low'].min():,.2f}"
                    )
                
                with stats2_col3:
                    st.metric(
                        label="평균가",
                        value=f"{stock_data2['Close'].mean():,.2f}"
                    )
                
                with stats2_col4:
                    st.metric(
                        label="거래량",
                        value=f"{stock_data2['Volume'].mean():,.0f}"
                    )
        else:
            # 1개 종목
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            
            with stat_col1:
                st.metric(
                    label="최고가",
                    value=f"{stock_data1['High'].max():,.2f}"
                )
            
            with
