import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="광종별 매장량 시각화", layout="wide")
st.title("⛏️ 광종별 매장량 분석 대시보드")

# ---------------- 파일 업로드 ----------------
st.sidebar.header("📂 데이터 파일 업로드")
uploaded_file = st.sidebar.file_uploader("광종별 매장량 CSV 업로드", type=["csv"])

if uploaded_file:
    try:
        # 인코딩 자동 시도
        try:
            df = pd.read_csv(uploaded_file, encoding="cp949")
        except UnicodeDecodeError:
            df = pd.read_csv(uploaded_file, encoding="utf-8")

        # 전처리
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes(include='object'):
            df[col] = df[col].astype(str).str.strip()

        df["상위5개국 매장량 합계"] = pd.to_numeric(
            df["상위5개국 매장량 합계"].astype(str).str.replace(",", ""),
            errors="coerce"
        )
        df["단위"] = df["단위"].fillna("기타")

        st.subheader("🔍 데이터 미리보기")
        st.dataframe(df)

        # 📊 시각화 옵션
        st.subheader("📊 그래프 설정")
        orientation = st.radio("그래프 방향", ["세로 막대", "가로 막대"])
        filter_option = st.selectbox("데이터 범위", ["전체 보기", "상위 5개", "하위 5개", "직접 선택"])

        if filter_option == "상위 5개":
            df_vis = df.nlargest(5, "상위5개국 매장량 합계")
        elif filter_option == "하위 5개":
            df_vis = df.nsmallest(5, "상위5개국 매장량 합계")
        elif filter_option == "직접 선택":
            selected_items = st.multiselect("📌 광종 선택", df["광종"].unique())
            df_vis = df[df["광종"].isin(selected_items)]
        else:
            df_vis = df.copy()

        # 정렬
        sort_order = st.radio("정렬 방식", ["내림차순", "오름차순"])
        ascending = sort_order == "오름차순"
        df_vis = df_vis.sort_values("상위5개국 매장량 합계", ascending=ascending)

        # 📈 시각화
        st.subheader("📈 시각화 결과")
        if orientation == "세로 막대":
            fig = px.bar(df_vis, x="광종", y="상위5개국 매장량 합계", color="단위",
                         title="광종별 상위 5개국 매장량 합계",
                         labels={"상위5개국 매장량 합계": "매장량", "광종": "광물 종류"})
            fig.update_layout(xaxis_tickangle=-45)
        else:
            fig = px.bar(df_vis, y="광종", x="상위5개국 매장량 합계", color="단위",
                         orientation="h",
                         title="광종별 상위 5개국 매장량 합계",
                         labels={"상위5개국 매장량 합계": "매장량", "광종": "광물 종류"})
            fig.update_layout(margin=dict(l=200))

        st.plotly_chart(fig, use_container_width=True)

        # 📌 선택 상세 정보
        st.subheader("📌 선택한 광종 상세 정보")
        selected_mineral = st.selectbox("자세히 볼 광종 선택", df_vis["광종"].unique())
        row = df_vis[df_vis["광종"] == selected_mineral]
        if not row.empty:
            st.markdown(f"""
            **🔎 {selected_mineral} 상세 정보**
            - 매장량 합계: `{row['상위5개국 매장량 합계'].values[0]:,}` {row['단위'].values[0]}
            """)

    except Exception as e:
        st.error("❌ 오류 발생:")
        st.exception(e)
else:
    st.info("📁 좌측 사이드바에서 CSV 파일을 업로드해주세요.")
