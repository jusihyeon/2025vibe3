import streamlit as st
import pandas as pd
import plotly.express as px
from pandas.errors import EmptyDataError

st.set_page_config(page_title="광종별 매장량 시각화", layout="wide")
st.title("⛏️ 광종별 및 국가별 매장량 분석 + 형법범죄 통계 대시보드")

# ---------------- 파일 업로드 ----------------
st.sidebar.header("📂 데이터 파일 업로드")
uploaded_mineral = st.sidebar.file_uploader("광종별 매장량 (상위 5개국 기준)", type=["csv"], key="mineral")
uploaded_country = st.sidebar.file_uploader("국가별 매장량 (전체 국가)", type=["csv"], key="country")
uploaded_crime = st.sidebar.file_uploader("형법범죄 통계 엑셀 파일", type=["xlsx"], key="crime")

# ---------------- TAB 설정 ----------------
tabs = st.tabs(["📈 광종별 매장량", "🌍 국가별 매장량", "📉 형법범죄 통계"])

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
                df2 = pd.read_csv(uploaded_country, encoding="utf-8", sep=None, engine="python")
            except UnicodeDecodeError:
                df2 = pd.read_csv(uploaded_country, encoding="cp949", sep=None, engine="python")

            df2 = df2.dropna(how='all')
            df2.columns = df2.columns.str.strip()

            # ✅ 열 이름 매핑 처리
            rename_map = {
                "자원명": "광종",
                "광종명": "광종",
                "국가명": "국가",
                "매장량(톤)": "매장량",
            }
            df2.rename(columns={k: v for k, v in rename_map.items() if k in df2.columns}, inplace=True)

            df2.columns = df2.columns.str.strip()
            required_cols = {"광종", "국가", "매장량"}
            if not required_cols.issubset(set(df2.columns)):
                st.warning(f"❗ 필요한 열 {required_cols}이(가) 누락된 파일입니다.")
                st.stop()

            df2["매장량"] = pd.to_numeric(df2["매장량"].astype(str).str.replace(",", ""), errors="coerce")
            df2 = df2.dropna(subset=["광종", "국가", "매장량"])

            if df2.empty:
                st.warning("⚠️ 업로드된 CSV 파일에 데이터가 없습니다. 행이 0개입니다.")
            else:
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

        except EmptyDataError:
            st.error("❌ CSV 파일이 비어 있어 읽을 수 없습니다.")
        except Exception as e:
            st.error("❌ 오류 발생:")
            st.exception(e)
    else:
        st.info("⬆️ 좌측에서 국가별 CSV 파일을 업로드하세요.")

# ---------------- TAB 3: 형법범죄 통계 ----------------
with tabs[2]:
    st.header("📉 형법범죄 통계 시각화")
    if uploaded_crime:
        try:
            df_crime_raw = pd.read_excel(uploaded_crime, sheet_name=0, header=None)

            # 헤더 추정 및 컬럼 설정
            df_crime_raw.columns.values[0:2] = ["범죄분류", "범죄유형"]
            df_crime_raw.columns = df_crime_raw.columns.astype(str).str.strip()
            df_crime_raw["범죄유형"] = df_crime_raw["범죄유형"].fillna(method="ffill")

            df_crime = df_crime_raw.melt(id_vars=["범죄분류", "범죄유형"], var_name="연도", value_name="범죄율")
            df_crime["연도"] = pd.to_numeric(df_crime["연도"], errors="coerce")
            df_crime = df_crime.dropna(subset=["연도", "범죄율"])

            df_crime["범죄율"] = pd.to_numeric(df_crime["범죄율"].astype(str).str.replace(",", "").replace("-", "0"), errors="coerce")

            # 주요 형법범죄만 필터링
            df_major = df_crime[df_crime["범죄분류"].str.contains("주요", na=False)]

            st.subheader("📈 주요 형법범죄 연도별 추이")
            fig = px.line(df_major, x="연도", y="범죄율", color="범죄유형", markers=True,
                         title="📊 주요 형법범죄 범죄율 추세")
            fig.update_layout(yaxis_title="범죄율 (인구 10만 명당)", xaxis_title="연도")
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error("❌ 오류 발생:")
            st.exception(e)
    else:
        st.info("⬆️ 좌측에서 형법범죄 엑셀 파일을 업로드하세요.")
