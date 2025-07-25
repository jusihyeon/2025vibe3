import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="광종별 매장량 시각화", layout="wide")
st.title("⛏️ 광종별 및 국가별 매장량 분석 대시보드")

# ---------------- 파일 업로드 ----------------
st.sidebar.header("📂 데이터 파일 업로드")
uploaded_mineral = st.sidebar.file_uploader("광종별 매장량 (상위 5개국 기준)", type=["csv"], key="mineral")
uploaded_country = st.sidebar.file_uploader("국가별 매장량 (전체 국가)", type=["csv"], key="country")

# ---------------- TAB 설정 ----------------
tabs = st.tabs(["📈 광종별 매장량", "🌍 국가별 매장량"])

# ---------------- TAB 1: 광종별 매장량 ----------------
with tabs[0]:
    st.header("📊 광종별 매장량 (상위 5개국 기준)")
    if uploaded_mineral:
        try:
            try:
                df = pd.read_csv(uploaded_mineral, encoding="cp949")
            except UnicodeDecodeError:
                df = pd.read_csv(uploaded_mineral, encoding="utf-8")

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

            st.subheader("📊 그래프 옵션")
            orientation = st.radio("그래프 방향", ["세로 막대", "가로 막대"])
            filter_option = st.selectbox("데이터 범위", ["전체 보기", "상위 5개만", "하위 5개만", "직접 선택"])

            if filter_option == "상위 5개만":
                df_vis = df.nlargest(5, "상위5개국 매장량 합계")
            elif filter_option == "하위 5개만":
                df_vis = df.nsmallest(5, "상위5개국 매장량 합계")
            elif filter_option == "직접 선택":
                selected_items = st.multiselect("광종 선택", df["광종"].unique())
                df_vis = df[df["광종"].isin(selected_items)]
            else:
                df_vis = df.copy()

            sort_order = st.radio("정렬 순서", ["매장량 높은 순", "매장량 낮은 순"])
            ascending = True if sort_order == "매장량 낮은 순" else False
            df_vis = df_vis.sort_values("상위5개국 매장량 합계", ascending=ascending)

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

            st.subheader("🔎 선택한 광물 상세 정보")
            selected_mineral = st.selectbox("광종 선택", df_vis["광종"].unique())
            selected_row = df_vis[df_vis["광종"] == selected_mineral]
            if not selected_row.empty:
                st.markdown(f"""
                **📌 {selected_mineral} 상세 정보**
                - 매장량 합계: `{selected_row['상위5개국 매장량 합계'].values[0]:,}` {selected_row['단위'].values[0]}
                """)

        except Exception as e:
            st.error("❌ 오류 발생:")
            st.exception(e)
    else:
        st.info("⬆️ 좌측에서 광종별 CSV 파일을 업로드하세요.")

# ---------------- TAB 2: 국가별 매장량 ----------------
with tabs[1]:
    st.header("🌍 국가별 광물 매장량 분석")
    if uploaded_country:
        try:
            try:
                df2 = pd.read_csv(uploaded_country, encoding="utf-8")
            except UnicodeDecodeError:
                df2 = pd.read_csv(uploaded_country, encoding="cp949")

            df2.columns = df2.columns.str.strip()
            df2["매장량"] = pd.to_numeric(df2["매장량"].astype(str).str.replace(",", ""), errors="coerce")
            st.subheader("📊 데이터 미리보기")
            st.dataframe(df2)

            selected_mineral = st.selectbox("🔍 광종 선택", df2["광종"].unique())
            df_mineral = df2[df2["광종"] == selected_mineral].copy()
            df_top10 = df_mineral.nlargest(10, "매장량")

            fig2 = px.bar(df_top10, x="국가", y="매장량", color="국가",
                          title=f"{selected_mineral} 자원 국가별 매장량 Top 10",
                          labels={"매장량": "매장량", "국가": "국가"})
            fig2.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)

        except Exception as e:
            st.error("❌ 오류 발생:")
            st.exception(e)
    else:
        st.info("⬆️ 좌측에서 국가별 CSV 파일을 업로드하세요.")
