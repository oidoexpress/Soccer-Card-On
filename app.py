import streamlit as st
import random
import time
import json
import os
import base64

# 1. 페이지 설정
st.set_page_config(page_title="동네 축구 카드 매니저", page_icon="⚽", layout="centered")

DATA_FILE = "game_save.json"

# 💥 [핵심 수리] 서버 권한 에러를 완벽하게 우회하는 안전 데이터 로드 시스템
if "users_db" not in st.session_state:
    # 1단계: 깃허브에 만들어둔 json 파일을 안전하게 읽어옵니다.
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                st.session_state.users_db = json.load(f)
        except:
            st.session_state.users_db = {"test": {"password": "1234", "money": 5000, "inventory": []}}
    else:
        st.session_state.users_db = {"test": {"password": "1234", "money": 5000, "inventory": []}}

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# 데이터 저장 함수 (서버 차단을 방지하기 위해 가상 저장 처리 후 세션 동시 유지)
def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.users_db, f, ensure_ascii=False, indent=4)
    except:
        # 서버가 파일 쓰기를 막아도 앱이 하얗게 튕기지 않고 브라우저 메모리로 안전하게 버티도록 방어합니다.
        pass

# 2. 카드 데이터 정의 (요청하신 3명 고정)
rare_players = [
    {"name": "마크롱", "image": "UEFA Champions League 24 STAR 마크롱.png", "sell_price": 50000, "grade": "🔥 전설 (10%)"}
]

normal_players = [
    {"name": "노무현", "image": "KICK-OFF 23-24 노무현.png", "sell_price": 1000, "grade": "일반 (90%)"},
    {"name": "안창혁", "image": "안창혁.png", "sell_price": 1000, "grade": "일반 (90%)"}
]

all_players = rare_players + normal_players

# 3. 메인 화면 타이틀 (동네 축구 카드 매니저)
st.title("⚽ 동네 축구 카드 매니저")
st.write("동네 축구 카드 뽑기 게임에 오신 것을 환영합니다.")
st.write("---")

# 🔐 로그인 / 회원가입 폼 (하얀 화면 버그 완벽 차단)
if st.session_state.current_user is None:
    st.subheader("🔑 로그인 및 회원가입")
    
    menu = ["로그인", "회원가입"]
    choice = st.radio("원하는 작업을 선택하세요", menu, horizontal=True)
    
    with st.form(key="auth_form"):
        user_id = st.text_input("아이디 (ID)")
        user_pw = st.text_input("비밀번호 (Password)", type="password")
        submit_button = st.form_submit_button(label="🚀 실행하기", use_container_width=True)
        
        if submit_button:
            if choice == "회원가입":
                if user_id in st.session_state.users_db:
                    st.error("❌ 이미 존재하는 아이디입니다.")
                elif user_id == "" or user_pw == "":
                    st.warning("⚠️ 아이디와 비밀번호를 입력해 주세요.")
                else:
                    st.session_state.users_db[user_id] = {"password": user_pw, "money": 5000, "inventory": []}
                    save_data()
                    st.success("🎉 회원가입 완료! 로그인을 선택하고 다시 눌러주세요.")
                    
            elif choice == "로그인":
                if user_id in st.session_state.users_db and st.session_state.users_db[user_id]["password"] == user_pw:
                    st.session_state.current_user = user_id
                    st.success(f"👋 {user_id}님 환영합니다!")
                    st.rerun()
                else:
                    st.error("❌ 아이디 또는 비밀번호가 틀렸습니다.")

# 🕹️ 게임 메인 화면 (로그인 후)
else:
    my_id = st.session_state.current_user
    my_data = st.session_state.users_db[my_id]
    
    col_u1, col_u2 = st.columns([2, 1])
    with col_u1:
        st.write(f"👤 **유저:** {my_id}님")
    with col_u2:
        st.write(f"💰 **보유 금액:** {my_data['money']}원")
        
    if st.button("🔒 로그아웃"):
        st.session_state.current_user = None
        st.rerun()
        
    st.write("---")
    
    tab1, tab2 = st.tabs(["✨ 카드 팩 뽑기", "🎒 내 소장고 & 판매"])
    
    # --- [탭 1: 카드 뽑기] ---
    with tab1:
        st.subheader("🎯 동네 축구 일반 카드 팩")
        st.write("💰 **1회 뽑기 비용:** 1,000원")
        
        if st.button("🔥 카드 팩 오픈! (1,000원 결제)", type="primary", use_container_width=True):
            if my_data["money"] < 1000:
                st.error("❌ 잔액이 부족합니다!")
            else:
                st.session_state.users_db[my_id]["money"] -= 1000
                
                with st.spinner("⚡ 카드 팩을 뜯는 중..."):
                    time.sleep(1.2)
                    percentage = random.randint(1, 100)
                    if percentage <= 10:
                        lucky_player = random.choice(rare_players)
                        st.balloons()
                    else:
                        lucky_player = random.choice(normal_players)
                
                st.success(f"🎉 **[{lucky_player['grade']}] {lucky_player['name']}** 선수를 뽑았습니다!")
                st.session_state.users_db[my_id]["inventory"].append(lucky_player["name"])
                save_data()
                
                col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
                with col_c2:
                    try:
                        st.image(lucky_player['image'], use_container_width=True)
                    except:
                        st.error(f"❌ '{lucky_player['image']}' 이미지를 불러오지 못했습니다.")
                st.rerun()
                
    # --- [탭 2: 내 소장고 & 판매] ---
    with tab2:
        st.subheader("🎒 내가 소장 중인 카드 목록")
        my_inv = my_data["inventory"]
        
        if not my_inv:
            st.info("아직 소장한 카드가 없습니다. 카드 팩을 뽑아보세요!")
        else:
            for item in set(my_inv):
                count = my_inv.count(item)
                p_info = next((p for p in all_players if p["name"] == item), None)
                
                if p_info:
                    col_i1, col_i2, col_i3 = st.columns([2, 1, 1])
                    with col_i1:
                        st.write(f"🏃‍♂️ **[{p_info['grade']}] {item}** (보유: {count}장)")
                    with col_i2:
                        st.write(f"💵 판매가: {p_info['sell_price']}원")
                    with col_i3:
                        if st.button("💰 판매하기", key=f"sell_{item}"):
                            st.session_state.users_db[my_id]["inventory"].remove(item)
                            st.session_state.users_db[my_id]["money"] += p_info["sell_price"]
                            save_data()
                            st.success(f"💵 {item} 카드를 판매 완료했습니다!")
                            st.rerun()
                    
                    with st.expander(f"🔍 {item} 카드 실물 확인"):
                        try:
                            st.image(p_info['image'], width=150)
                        except:
                            st.write("이미지가 존재하지 않습니다.")
                    st.write("---")

# 4. 🔊 안전한 자동 재생 오디오 인젝션
if os.path.exists("loading.mp3"):
    try:
        with open("loading.mp3", "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_base64}" style="display:none;"></audio>', unsafe_allow_html=True)
    except:
        pass
