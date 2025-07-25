import streamlit as st
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(page_title="북마크 지도", page_icon="🗺️", layout="centered")
st.title("📌 북마크 지도 만들기")

# 세션 상태에 북마크 리스트 저장
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []

# 입력 폼
with st.form("bookmark_form"):
    st.subheader("➕ 새로운 장소 추가")
    name = st.text_input("장소 이름")
    lat = st.number_input("위도", format="%.6f")
    lon = st.number_input("경도", format="%.6f")
    submitted = st.form_submit_button("추가")

    if submitted:
        if name and lat and lon:
            st.session_state.bookmarks.append({
                "name": name,
                "lat": lat,
                "lon": lon
            })
            st.success(f"📍 '{name}' 북마크에 추가됨!")
        else:
            st.warning("모든 정보를 입력하세요.")

# 지도 초기 중심 설정
if st.session_state.bookmarks:
    center_lat = st.session_state.bookmarks[-1]["lat"]
    center_lon = st.session_state.bookmarks[-1]["lon"]
else:
    center_lat, center_lon = 37.5665, 126.9780  # 서울 중심 (기본값)

# Folium 지도 생성
m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

# 마커 추가
for bm in st.session_state.bookmarks:
    folium.Marker(
        location=[bm["lat"], bm["lon"]],
        popup=bm["name"],
        icon=folium.Icon(color="blue", icon="bookmark")
    ).add_to(m)

# 지도 표시
st_data = st_folium(m, width=700, height=500)

# 북마크 목록 보기
if st.session_state.bookmarks:
    st.markdown("---")
    st.subheader("📋 북마크 목록")
    for idx, bm in enumerate(st.session_state.bookmarks):
        st.write(f"{idx + 1}. {bm['name']} ({bm['lat']}, {bm['lon']})")

# 초기화 버튼
if st.button("📛 모든 북마크 초기화"):
    st.session_state.bookmarks.clear()
    st.success("모든 북마크가 삭제되었습니다.")

