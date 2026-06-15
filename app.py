import streamlit as st
import random
import time
import os
import base64

# 1. 페이지 설정
st.set_page_config(page_title="동네 축구 카드 매니저", page_icon="⚽", layout="centered")

# 계정 유실 방지 가상 메모리 데이터베이스
if "users_backup_db" not in st.session_state:
    st.session_state.users_backup_db = {
        "test": {"password": "1234", "money": 10000, "inventory": []}
    }

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# 뽑기 결과 및 쿨타임 기억장치
if "draw_result" not in st.session_state:
    st.session_state.draw_result = None
if "cooldown_time" not in st.session_state:
    st.session_state.cooldown_time = 0

# 2. 카드 데이터 정의
rare_players = [
    {"name": "마크롱", "image": "UEFA Champions League 24 STAR 마크롱.png", "sell_price": 50000, "grade": "🏆 UCL (10%)"},
    {"name": "세루 기라시", "image": "UEFA Champions League 25 STAR 세루 기라시.png", "sell_price": 45000, "grade": "🏆 UCL (10%)"},
    {"name": "주앙 네베스", "image": "UEFA Champions League 25 STAR 주앙 네베스.png", "sell_price": 45000, "grade": "🏆 UCL (10%)"}
]

normal_players = [
    {"name": "노무현", "image": "KICK-OFF 23-24 노무현.png", "sell_price": 1000, "grade": "🏃 KICK-OFF (90%)"},
    {"name": "안창혁", "image": "안창혁.png", "sell_price": 1000, "grade": "🏃 KICK-OFF (90%)"}
]

all_players = rare_players + normal_players

# 3. 부드러운 스크롤 스타일 지정
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

# 4. 메인 타이틀
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
                if user_id in st.session_state.users_backup_db:
                    st.error("❌ 이미 존재하는 아이디입니다.")
                elif user_id == "" or user_pw == "":
                    st.warning("⚠️ 아이디와 비밀번호를 입력해 주세요.")
                else:
                    st.session_state.users_backup_db[user_id] = {"password": user_pw, "money": 10000, "inventory": []}
                    st.success("🎉 회원가입 완료! 이제 바로 로그인을 선택하고 버튼을 눌러주세요.")
                    
            elif choice == "로그인":
                if user_id in st.session_state.users_backup_db and st.session_state.users_backup_db[user_id]["password"] == user_pw:
                    st.session_state.current_user = user_id
                    st.success(f"👋 {user_id}님 환영합니다!")
                    st.rerun()
                else:
                    st.error("❌ 아이디 또는 비밀번호가 틀렸습니다.")

# 🕹️ 게임 메인 화면
else:
    my_id = st.session_state.current_user
    my_data = st.session_state.users_backup_db[my_id]
    
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
        
        is_cooling = False
        current_ts = time.time()
        
        # 실시간 쿨타임 시스템 검사
        if st.session_state.cooldown_time > current_ts:
            is_cooling = True
            rem_time = int(st.session_state.cooldown_time - current_ts)
            
            # 💥 등급에 따라 버튼 메시지 분기 처리
            if st.session_state.draw_result and "UCL" in st.session_state.draw_result["grade"]:
                btn_text = f"⏳ UCL 카드 당첨! 쿨타임 대기 중... ({rem_time}초)"
            else:
                btn_text = f"⏳ 쿨타임 대기 중... ({rem_time}초)"
        else:
            btn_text = "🔥 카드 팩 오픈! (1,000원 결제)"
            st.session_state.draw_result = None
            
        if st.button(btn_text, type="primary", use_container_width=True, disabled=is_cooling):
            if my_data["money"] < 1000:
                st.error("❌ 잔액이 부족합니다!")
            else:
                st.session_state.users_backup_db[my_id]["money"] -= 1000
                
                video_placeholder = st.empty()
                
                with st.spinner("⚡ 카드 팩을 뜯는 중..."):
                    time.sleep(0.8)
                    percentage = random.randint(1, 100)
                    if percentage <= 10:
                        lucky_player = random.choice(rare_players)
                        is_ucl = True
                    else:
                        lucky_player = random.choice(normal_players)
                        is_ucl = False
                
                st.session_state.users_backup_db[my_id]["inventory"].append(lucky_player["name"])
                st.session_state.draw_result = lucky_player
                
                # UCL 등급 전용 비디오 및 20초 잠금
                if is_ucl:
                    if os.path.exists("uclcard.mp4"):
                        try:
                            with open("uclcard.mp4", "rb") as video_file:
                                video_bytes = video_file.read()
                            video_base64 = base64.b64encode(video_bytes).decode()
                            
                            video_html = f'''
                                <video autoplay playsinline style="width:100%; max-width:100%; border-radius:10px;">
                                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                                </video>
                            '''
                            video_placeholder.markdown(video_html, unsafe_allow_html=True)
                        except:
                            pass
                        
                        time.sleep(5.0) 
                        video_placeholder.empty()
                    st.balloons()
                    st.session_state.cooldown_time = time.time() + 20 # UCL 카드는 20초 잠금
                else:
                    # 💥 [수정 핵심] KICK-OFF 등급 카드는 쿨타임과 사진 노출 포함 총 3초 잠금!
                    st.session_state.cooldown_time = time.time() + 3
                
                st.rerun()
                
        # 쿨타임 동안 카드 사진 및 정보 고정 노출존
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
                            st.session_state.users_backup_db[my_id]["inventory"].remove(item)
                            st.session_state.users_backup_db[my_id]["money"] += p_info["sell_price"]
                            st.success(f"💵 {item} 카드를 판매 완료했습니다!")
                            st.rerun()
                    
                    with st.expander(f"🔍 {item} 카드 실물 확인"):
                        try:
                            st.image(p_info['image'], width=150)
                        except:
                            st.write("이미지가 존재하지 않습니다.")
                    st.write("---")

# 5. 🔊 안전한 자동 재생 오디오 인젝션
if os.path.exists("loading.mp3"):
    try:
        with open("loading.mp3", "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_base64}" style="display:none;"></audio>', unsafe_allow_html=True)
    except:
        pass 
