import streamlit as st
import random
import time
import json
import os
import base64

# 1. 페이지 설정
st.set_page_config(page_title="동네 축구 카드 매니저", page_icon="⚽", layout="centered")

DATA_FILE = "game_save.json"

# [안전 데이터 시스템] 기존 따로 만드신 계정들 완벽하게 보존됩니다.
if "users_db" not in st.session_state:
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

# 뽑기 결과 및 쿨타임 기억장치
if "draw_result" not in st.session_state:
    st.session_state.draw_result = None
if "cooldown_time" not in st.session_state:
    st.session_state.cooldown_time = 0

def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.users_db, f, ensure_ascii=False, indent=4)
    except:
        pass

# 2. 💥 카드 데이터 등급 수정 (전설 ❌ -> UCL 및 KICK-OFF 등급으로 변경)
rare_players = [
    {"name": "마크롱", "image": "UEFA Champions League 24 STAR 마크롱.png", "sell_price": 50000, "grade": "🏆 UCL (10%)"}
]

normal_players = [
    {"name": "노무현", "image": "KICK-OFF 23-24 노무현.png", "sell_price": 1000, "grade": "🏃 KICK-OFF (90%)"},
    {"name": "안창혁", "image": "안창혁.png", "sell_price": 1000, "grade": "🏃 KICK-OFF (90%)"}
]

all_players = rare_players + normal_players


# 3. 안전한 스타일 지정 (세로 스크롤 완벽 보장)
st.markdown("""
    <style>
    .stTextInput input {
        color: #ece8e1 !important;
        background-color: #232936 !important;
        border: 1px solid #ff4655 !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #677080 !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #ff4655 !important;
    }
    </style>
""", unsafe_allow_html=True)


# 4. 메인 화면 타이틀
st.title("⚽ 동네 축구 카드 매니저")
st.write("---")

# 🔐 로그인 / 회원가입 폼
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
        st.session_state.draw_result = None
        st.session_state.cooldown_time = 0
        st.rerun()
        
    st.write("---")
    
    tab1, tab2 = st.tabs(["✨ 카드 팩 뽑기", "🎒 내 소장고 & 판매"])
    
    # --- [탭 1: 카드 뽑기] ---
    with tab1:
        st.subheader("🎯 동네 축구 일반 카드 팩")
        st.write("💰 **1회 뽑기 비용:** 1,000원")
        
        # 실시간 쿨타임 체크
        is_cooling = False
        current_ts = time.time()
        if st.session_state.cooldown_time > current_ts:
            is_cooling = True
            rem_time = int(st.session_state.cooldown_time - current_ts)
            btn_text = f"⏳ 쿨타임 대기 중... ({rem_time}초)"
        else:
            btn_text = "🔥 카드 팩 오픈! (1,000원 결제)"
            st.session_state.draw_result = None
            
        if st.button(btn_text, type="primary", use_container_width=True, disabled=is_cooling):
            if my_data["money"] < 1000:
                st.error("❌ 잔액이 부족합니다!")
            else:
                st.session_state.users_db[my_id]["money"] -= 1000
                save_data()
                
                # 영상 재생 연출존 미리 마련
                video_placeholder = st.empty()
                
                with st.spinner("⚡ 카드 팩을 뜯는 중..."):
                    time.sleep(1.0)
                    percentage = random.randint(1, 100)
                    if percentage <= 10:
                        lucky_player = random.choice(rare_players)
                        is_ucl = True
                    else:
                        lucky_player = random.choice(normal_players)
                        is_ucl = False
                
                # 💥 [수정 핵심] UCL 등급 카드가 나오면 비디오 전송 및 재생 처리
                if is_ucl:
                    if os.path.exists("uclcard.mp4"):
                        # autoplay=True로 유저가 누르지 않아도 비디오가 즉시 나옵니다.
                        video_placeholder.video("uclcard.mp4", format="video/mp4", autoplay=True)
                        # 영상이 끝날 때까지 (원하는 시간만큼 지정 가능, 기본 5초 대기) 화면을 붙잡아둡니다.
                        time.sleep(5.0) 
                        video_placeholder.empty() # 재생 완료 후 비디오 상자 청소
                    st.balloons()
                
                # 인벤토리에 보존 및 세이브
                st.session_state.users_db[my_id]["inventory"].append(lucky_player["name"])
                save_data()
                
                # 결과 임시 보관 및 5초 잠금설정
                st.session_state.draw_result = lucky_player
                st.session_state.cooldown_time = time.time() + 5
                st.rerun()
                
        # 5초 동안 사진 노출 및 카운트다운 가동
        if is_cooling and st.session_state.draw_result:
            p_res = st.session_state.draw_result
            st.success(f"🎉 **[{p_res['grade']}] {p_res['name']}** 선수를 뽑았습니다!")
            
            col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
            with col_c2:
                try:
                    st.image(p_res['image'], use_container_width=True)
                except:
                    st.error(f"❌ '{p_res['image']}' 이미지를 불러오지 못했습니다.")
            
            time.sleep(1)
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

# 5. 🔊 로그인 시 기본 오디오 인젝션 (기존 유지)
if os.path.exists("loading.mp3"):
    try:
        with open("loading.mp3", "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_base64}" style="display:none;"></audio>', unsafe_allow_html=True)
    except:
        pass
