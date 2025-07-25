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

        # ▶️ 선택 필터: 상위/하위/전체 선택
        filter_option = st.selectbox("🔍 표시할 데이터 범위 선택", ["전체 보기", "상위 5개만", "하위 5개만", "직접 선택"])

        if filter_option == "상위 5개만":
            df_vis = df.nlargest(5, "상위5개국 매장량 합계")
        elif filter_option == "하위 5개만":
            df_vis = df.nsmallest(5, "상위5개국 매장량 합계")
        elif filter_option == "직접 선택":
            selected_items = st.multiselect("광종 선택", df["광종"].unique())
            df_vis = df[df["광종"].isin(selected_items)]
        else:
            df_vis = df.copy()

        # ▶️ 정렬 옵션 추가
        sort_order = st.radio("정렬 순서 선택", ["매장량 높은 순", "매장량 낮은 순"])
        ascending = True if sort_order == "매장량 낮은 순" else False
        df_vis = df_vis.sort_values("상위5개국 매장량 합계", ascending=ascending)

        # ▶️ 그래프 그리기
        if orientation == "세로 막대":
            fig = px.bar(df_vis, x="광종", y="상위5개국 매장량 합계", color="단위",
                         title="광종별 상위 5개국 매장량 합계 (확대 보기)",
                         labels={"상위5개국 매장량 합계": "매장량", "광종": "광물 종류"})
            fig.update_layout(xaxis_tickangle=-45, margin=dict(b=120))
        else:
            fig = px.bar(df_vis, y="광종", x="상위5개국 매장량 합계", color="단위",
                         orientation="h",
                         title="광종별 상위 5개국 매장량 합계 (확대 보기)",
                         labels={"상위5개국 매장량 합계": "매장량", "광종": "광물 종류"})
            fig.update_layout(margin=dict(l=200))

        st.plotly_chart(fig, use_container_width=True)

        # ▶️ 선택한 광종 상세 정보 표시
        st.subheader("🔎 선택한 광물의 상세 매장량 보기")
        selected_mineral = st.selectbox("광종 선택", df_vis["광종"].unique())
        selected_row = df_vis[df_vis["광종"] == selected_mineral]

        if not selected_row.empty:
            st.markdown(f"""
            **📌 {selected_mineral} 매장량 상세 정보**

            - 매장량 합계: `{selected_row['상위5개국 매장량 합계'].values[0]:,}` {selected_row['단위'].values[0]}
            """)
        else:
            st.warning("선택한 광종의 데이터를 찾을 수 없습니다.")

    except Exception as e:
        st.error("❌ 오류 발생:")
        st.exception(e)
else:
    st.info("⬆️ 좌측에서 CSV 파일을 업로드하세요.")
