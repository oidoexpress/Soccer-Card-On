import streamlit as st
import random
import time

st.set_page_config(page_title="축구 카드 뽑기", page_icon="⚽", layout="centered")

st.title("⚽ 레전드 축구 카드 가챠 앱")
st.write("직접 만든 한정판 축구 카드를 획득해 보세요!")

# 💥 [핵심 고정] 폴더 경로(images/)를 싹 다 지우고 파일 이름만 정확히 매칭했습니다!
players = [
    {"name": "노무현", "image": "KICK-OFF 23-24 노무현.png"},
    {"name": "마크롱", "image": "UEFA Champions League 24 STAR 마크롱.png"},
    {"name": "이현", "image": "UEFA Champions League 24 STAR 이현.png"},
    {"name": "권태희", "image": "권태희.png"},
    {"name": "안창혁", "image": "안창혁.png"},
    {"name": "이현(단독)", "image": "이현.png"}
]

if st.button("✨ 카드 팩 오픈! (Click)", type="primary", use_container_width=True):
    with st.spinner("⚡ 카드 팩을 뜯는 중..."):
        time.sleep(1.2)
        lucky_player = random.choice(players)
    
    st.balloons()
    st.success(f"🎉 대박! **[{lucky_player['name']}]** 선수를 뽑았습니다!")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            # 폴더 없이 파일명으로 바로 읽어옵니다.
            st.image(lucky_player['image'], use_container_width=True)
        except:
            st.error(f"❌ '{lucky_player['image']}' 파일을 찾을 수 없습니다. 메인 화면에 파일이 있는지 확인하세요.")
