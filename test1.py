import streamlit as st
import random

# 페이지 설정
st.set_page_config(page_title="가위바위보 게임", page_icon="✊", layout="centered")

st.title("✊ ✋ ✌ 가위바위보 게임")
st.write("당신의 선택은?")

# 선택지 정의
choices = ["가위", "바위", "보"]
user_choice = st.radio("선택하세요:", choices, horizontal=True)

# 세션 상태로 게임 기록 초기화
if "win" not in st.session_state:
    st.session_state.win = 0
if "draw" not in st.session_state:
    st.session_state.draw = 0
if "lose" not in st.session_state:
    st.session_state.lose = 0

# 결과 확인 버튼 클릭 시 게임 진행
if st.button("결과 확인"):
    computer_choice = random.choice(choices)

    st.write(f"🧑 당신의 선택: **{user_choice}**")
    st.write(f"💻 컴퓨터의 선택: **{computer_choice}**")

    if user_choice == computer_choice:
        st.session_state.draw += 1
        st.info("😐 비겼습니다!")
    elif (
        (user_choice == "가위" and computer_choice == "보") or
        (user_choice == "바위" and computer_choice == "가위") or
        (user_choice == "보" and computer_choice == "바위")
    ):
        st.session_state.win += 1
        st.balloons()
        st.success("🎉 당신이 이겼습니다!")
    else:
        st.session_state.lose += 1
        st.error("😢 당신이 졌습니다.")

    st.markdown("---")
    st.subheader("📊 게임 기록")
    st.write(f"✅ 승리: **{st.session_state.win}**")
    st.write(f"😐 무승부: **{st.session_state.draw}**")
    st.write(f"❌ 패배: **{st.session_state.lose}**")

# 기록 초기화 버튼
if st.button("기록 초기화"):
    st.session_state.win = 0
    st.session_state.draw = 0
    st.session_state.lose = 0
    st.success("기록이 초기화되었습니다.")
