import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="광종별 매장량 시각화", layout="wide")
st.title("⛏️ 광종별 매장량 (상위 5개국 기준) - 2017")

# CSV 파일 업로드
uploaded_file = st.file_uploader("📂 CSV 파일 업로드", type=["csv"])

if uploaded_file:
    try:
        # CSV 불러오기 (cp949 또는 utf-8 시도)
        try:
            df = pd.read_csv(uploaded_file, encoding="cp949")
        except UnicodeDecodeError:
            df = pd.read_csv(uploaded_file, encoding="utf-8")

        # 열 이름과 문자열 컬럼의 공백 제거
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes(include='object'):
            df[col] = df[col].astype(str).str.strip()

        # 수치 컬럼 변환 (콤마 제거 후 숫자형으로 변환)
        df["상위5개국 매장량 합계"] = pd.to_numeric(
            df["상위5개국 매장량 합계"].astype(str).str.replace(",", ""),
            errors="coerce"
        )

        # 결측 단위 채우기
        df["단위"] = df["단위"].fillna("기타")

        # 데이터 테이블 미리보기
        st.subheader("📊 데이터 미리보기")
        st.dataframe(df)

        # 시각화
        st.subheader("📈 광종별 매장량 시각화 (막대그래프)")
        orientation = st.radio("그래프 방향 선택", ["세로 막대", "가로 막대"])

        if orientation == "세로 막대":
            fig = px.bar(df, x="광종", y="상위5개국 매장량 합계", color="단위",
                         title="광종별 상위 5개국 매장량 합계 (2017)",
                         labels={"상위5개국 매장량 합계": "매장량", "광종": "광물 종류"})
            fig.update_layout(xaxis_tickangle=-45, margin=dict(b=120))
        else:
            fig = px.bar(df, y="광종", x="상위5개국 매장량 합계", color="단위",
                         orientation="h",
                         title="광종별 상위 5개국 매장량 합계 (2017)",
                         labels={"상위5개국 매장량 합계": "매장량", "광종": "광물 종류"})
            fig.update_layout(margin=dict(l=200))

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error("❌ 오류 발생:")
        st.exception(e)
else:
    st.info("⬆️ 좌측에서 CSV 파일을 업로드하세요.")
