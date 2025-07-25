import streamlit as st
import folium
from streamlit_folium import st_folium
import requests

# -------------------------------
# 주소 → 좌표 변환 함수 (Nominatim API)
def geocode_nominatim(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "streamlit-bookmark-app"
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200 and response.json():
        result = response.json()[0]
        return float(result["lat"]), float(result["lon"])
    else:
        return None, None

# -------------------------------
# Streamlit 설정
st.set_page_config(page_title="북마크 지도", page_icon="📍", layout="centered")
st.title("📍 주소 기반 북마크 지도 (선택 이동 기능 포함)")

# 세션 초기화
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []
if "selected" not in st.session_state:
    st.session_state.selected = None

# -------------------------------
# 장소 추가 폼
with st.form("bookmark_form"):
    st.subheader("➕ 북마크 추가")
    name = st.text_input("장소 이름")
    address = st.text_input("주소 입력")
    submitted = st.form_submit_button("추가하기")

    if submitted:
        if name and address:
            lat, lon = geocode_nominatim(address)
            if lat and lon:
                st.session_state.bookmarks.append({
                    "name": name,
                    "lat": lat,
                    "lon": lon,
                    "address": address
                })
                st.success(f"✅ '{name}' 북마크에 추가되었습니다.")
            else:
                st.error("❌ 주소를 찾을 수 없습니다.")
        else:
            st.warning("❗ 모든 항목을 입력하세요.")

# -------------------------------
# 북마크 목록 선택
if st.session_state.bookmarks:
    options = [f"{bm['name']} - {bm['address']}" for bm in st.session_state.bookmarks]
    selection = st.selectbox("📋 북마크에서 선택 시 지도 이동:", options)

    if selection:
        selected_idx = options.index(selection)
        st.session_state.selected = st.session_state.bookmarks[selected_idx]

# -------------------------------
# 지도 중심 위치 설정
if st.session_state.selected:
    center_lat = st.session_state.selected["lat"]
    center_lon = st.session_state.selected["lon"]
elif st.session_state.bookmarks:
    center_lat = st.session_state.bookmarks[-1]["lat"]
    center_lon = st.session_state.bookmarks[-1]["lon"]
else:
    center_lat, center_lon = 37.5665, 126.9780  # 서울 기본값

# -------------------------------
# 지도 생성 및 마커 표시
m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

for bm in st.session_state.bookmarks:
    folium.Marker(
        location=[bm["lat"], bm["lon"]],
        popup=f"{bm['name']}<br>{bm['address']}",
        icon=folium.Icon(color="blue", icon="bookmark")
    ).add_to(m)

# 지도 출력
st.subheader("🗺️ 북마크 지도")
st_folium(m, width=700, height=500)

# -------------------------------
# 초기화
if st.button("❌ 모든 북마크 초기화"):
    st.session_state.bookmarks.clear()
    st.session_state.selected = None
    st.success("모든 북마크가 삭제되었습니다.")
