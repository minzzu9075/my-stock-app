import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="주식 비교 앱",
    page_icon="📈",
    layout="wide"
)

st.title("📊 주식 비교 앱")
st.markdown("**2개의 종목을 나란히 비교할 수 있습니다.**")

st.markdown("---")
st.markdown("### 📝 종목 선택")

col1, col2 = st.columns(2)
with col1:
    ticker1 = st.text_input("첫 번째 종목", placeholder="AAPL").strip().upper()
with col2:
    ticker2 = st.text_input("두 번째 종목 (선택)", placeholder="MSFT").strip().upper()

st.markdown("---")
st.markdown("### 📅 기간 선택")

period_col1, period_col2, period_col3, period_col4 = st.columns(4)
with period_col1:
    if st.button("1개월"):
        st.session_state.period = "1mo"
with period_col2:
    if st.button("6개월"):
        st.session_state.period = "6mo"
with period_col3:
    if st.button("1년"):
        st.session_state.period = "1y"
with period_col4:
    if st.button("5년"):
        st.session_state.period = "5y"

if "period" not in st.session_state:
    st.session_state.period = "1y"

period_text = {"1mo": "1개월", "6mo": "6개월", "1y": "1년", "5y": "5년"}
st.markdown(f"**선택: {period_text[st.session_state.period]}**")

@st.cache_data
def get_stock_data(ticker, period):
    """주식 데이터 가져오기"""
    if not ticker or len(ticker) == 0:
        return None
    
    try:
        data = yf.download(ticker, period=period, progress=False)
        
        # 데이터가 비어있으면 None 반환
        if data is None or data.empty:
            return None
        
        return data
    except Exception as e:
        st.warning(f"⚠️ {ticker} 데이터 로드 실패: {str(e)}")
        return None

st.markdown("---")

# ticker1이 입력되었을 때만 실행
if ticker1:
    st.info(f"📥 {ticker1} 데이터를 불러오는 중...")
    data1 = get_stock_data(ticker1, st.session_state.period)
    
    # data1이 정상적으로 로드되었을 때
    if data1 is not None and not data1.empty:
        # ticker2 로드
        if ticker2:
            data2 = get_stock_data(ticker2, st.session_state.period)
        else:
            data2 = None
        
        st.markdown("### 💰 지표")
        
        # ticker1 데이터 처리
        try:
            current1 = float(data1['Close'].iloc[-1])
            prev1 = float(data1['Close'].iloc[0])
            change1 = current1 - prev1
            change_pct1 = (change1 / prev1) * 100
            max1 = float(data1['High'].max())
        except Exception as e:
            st.error(f"❌ {ticker1} 데이터 처리 오류: {e}")
            st.stop()
        
        # 2개 종목 비교
        if ticker2 and data2 is not None and not data2.empty:
            col_m1, col_m2 = st.columns(2)
            
            with col_m1:
                st.markdown(f"#### 🔹 {ticker1}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("현재가", f"${current1:,.2f}")
                with c2:
                    st.metric("등락률", f"{change_pct1:.2f}%", delta=f"${change1:,.2f}")
                with c3:
                    st.metric("최고가", f"${max1:,.2f}")
            
            # ticker2 데이터 처리
            try:
                current2 = float(data2['Close'].iloc[-1])
                prev2 = float(data2['Close'].iloc[0])
                change2 = current2 - prev2
                change_pct2 = (change2 / prev2) * 100
                max2 = float(data2['High'].max())
            except Exception as e:
                st.error(f"❌ {ticker2} 데이터 처리 오류: {e}")
                st.stop()
            
            with col_m2:
                st.markdown(f"#### 🔹 {ticker2}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("현재가", f"${current2:,.2f}")
                with c2:
                    st.metric("등락률", f"{change_pct2:.2f}%", delta=f"${change2:,.2f}")
                with c3:
                    st.metric("최고가", f"${max2:,.2f}")
        else:
            # 1개 종목만
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("💰 현재가", f"${current1:,.2f}")
            with c2:
                st.metric("📈 등락률", f"{change_pct1:.2f}%", delta=f"${change1:,.2f}")
            with c3:
                st.metric("🎯 최고가", f"${max1:,.2f}")
        
        st.markdown("---")
        st.markdown("### 📊 주가 추이")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data1.index,
            y=data1['Close'],
            mode='lines',
            name=f'{ticker1}',
            line=dict(color='#FF8C42', width=3)
        ))
        
        if ticker2 and data2 is not None and not data2.empty:
            fig.add_trace(go.Scatter(
                x=data2.index,
                y=data2['Close'],
                mode='lines',
                name=f'{ticker2}',
                line=dict(color='#6C63FF', width=3),
                yaxis='y2'
            ))
            
            fig.update_layout(
                yaxis2=dict(
                    title=f"{ticker2} ($)",
                    overlaying='y',
                    side='right'
                )
            )
        
        fig.update_layout(
            title=f"{ticker1}" + (f" vs {ticker2}" if ticker2 else ""),
            xaxis_title="날짜",
            yaxis_title=f"{ticker1} ($)",
            template="plotly_white",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📋 통계 정보")
        
        if ticker2 and data2 is not None and not data2.empty:
            col_s1, col_s2 = st.columns(2)
            
            with col_s1:
                st.markdown(f"#### {ticker1}")
                s1, s2, s3, s4 = st.columns(4)
                with s1:
                    st.metric("최고가", f"${float(data1['High'].max()):,.2f}")
                with s2:
                    st.metric("최저가", f"${float(data1['Low'].min()):,.2f}")
                with s3:
                    st.metric("평균가", f"${float(data1['Close'].mean()):,.2f}")
                with s4:
                    vol = data1['Volume'].mean()
                    vol_str = f"{vol/1000000:.1f}M" if vol > 1000000 else f"{vol/1000:.0f}K"
                    st.metric("평균거래량", vol_str)
            
            with col_s2:
                st.markdown(f"#### {ticker2}")
                s1, s2, s3, s4 = st.columns(4)
                with s1:
                    st.metric("최고가", f"${float(data2['High'].max()):,.2f}")
                with s2:
                    st.metric("최저가", f"${float(data2['Low'].min()):,.2f}")
                with s3:
                    st.metric("평균가", f"${float(data2['Close'].mean()):,.2f}")
                with s4:
                    vol = data2['Volume'].mean()
                    vol_str = f"{vol/1000000:.1f}M" if vol > 1000000 else f"{vol/1000:.0f}K"
                    st.metric("평균거래량", vol_str)
        else:
            s1, s2, s3, s4 = st.columns(4)
            with s1:
                st.metric("최고가", f"${float(data1['High'].max()):,.2f}")
            with s2:
                st.metric("최저가", f"${float(data1['Low'].min()):,.2f}")
            with s3:
                st.metric("평균가", f"${float(data1['Close'].mean()):,.2f}")
            with s4:
                vol = data1['Volume'].mean()
                vol_str = f"{vol/1000000:.1f}M" if vol > 1000000 else f"{vol/1000:.0f}K"
                st.metric("평균거래량", vol_str)
        
        # 성공 메시지
        st.success("✅ 데이터 로드 완료!")
    
    else:
        # data1이 None이거나 비어있음
        st.error(f"❌ '{ticker1}' 데이터를 불러올 수 없습니다.")
        st.info("💡 유효한 주식 코드를 입력하세요. (예: AAPL, MSFT, GOOGL)")

else:
    st.info("📌 첫 번째 종목 코드를 입력하세요 (예: AAPL)")
