import streamlit as st
import random
import time

# 1. 페이지 기본 설정
st.set_page_config(page_title="축구 카드 뽑기", page_icon="⚽", layout="centered")

st.title("⚽ 레전드 축구 카드 가챠 앱")
st.write("직접 만든 한정판 축구 카드를 획득해 보세요!")

# 2. 내 이미지 파일들과 매칭
players = [
    {"name": "노무현", "image": "images/KICK-OFF 23-24 노무현.png"},
    {"name": "마크롱", "image": "images/UEFA Champions League 24 STAR 마크롱.png"},
    {"name": "이현", "image": "images/UEFA Champions League 24 STAR 이현.png"},
    {"name": "권태희", "image": "images/권태희.png"},
    {"name": "안창혁", "image": "images/안창혁.png"},
    {"name": "이현(단독)", "image": "images/이현.png"}
]

# 3. 뽑기 버튼 작동
if st.button("✨ 카드 팩 오픈! (Click)", type="primary", use_container_width=True):
    with st.spinner("⚡ 카드 팩을 뜯는 중..."):
        time.sleep(1.5)
        lucky_player = random.choice(players)
    
    st.balloons()
    st.success(f"🎉 대박! **[{lucky_player['name']}]** 선수를 뽑았습니다!")
    
    # 💥 에러 나던 들여쓰기 공간 완벽 수정 완료 💥
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image(lucky_player['image'], use_container_width=True)
        except:
            st.error(f"❌ '{lucky_player['image']}' 파일을 찾을 수 없습니다.")
