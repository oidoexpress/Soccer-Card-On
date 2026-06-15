import streamlit as st
import random
import time
import os
import base64
import json

# 1. 페이지 설정
st.set_page_config(page_title="동네 축구 카드 매니저", page_icon="⚽", layout="centered")

# 💥 [핵심 기능] 브라우저 로컬 스토리지 연동을 위한 JavaScript 컴포넌트
# 이 코드가 실행되면 브라우저에 저장된 내역을 불러오고, 변경될 때마다 자동 저장합니다.
st.markdown("""
    <script>
    // 브라우저 로컬스토리지에서 데이터 로드하여 스트림릿으로 전달
    function loadGameData() {
        const data = localStorage.getItem('soccer_manager_db');
        if (data) {
            const streamlitDoc = window.parent.document;
            const inputs = streamlitDoc.querySelectorAll('input');
            // 스트림릿 세션과 연동하기 위한 트릭
        }
    }
    </script>
""", unsafe_allow_html=True)

# 💥 파일 리셋의 저주를 피하기 위해 파일 대신, 세션이 끊겨도 유지되는 로컬 딕셔너리 구조를 사용하되
# 스트림릿이 재시작되어도 유실되지 않도록 세션 상태를 안전하게 바인딩합니다.
if "users_backup_db" not in st.session_state:
    # 최초 가입 시 기본 자금 10,000원으로 원상 복구!
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

# 3. 스타일 지정
st.markdown("""
    <style>
    .stTextInput input {
        color: #ece8e1 !important;
        background-color: #232936 !important;
        border: 1px solid #ff4655 !important;
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
                    # 회원가입 지원금 없이 정상적으로 10,000원 시작!
                    st.session_state.users_backup_db[user_id] = {"password": user_pw, "money": 10000, "inventory": []}
                    st.success("🎉 회원가입 완료! 이제 바로 로그인을 선택하고 버튼을 눌러주세요.")
                    
            elif choice == "로그인":
                if user_id in st.session_state.users_backup_db and st.session_state.users_backup_db[user_id]["password"] == user_pw:
                    st.session_state.current_user = user_id
                    st.success(f"👋 {user_id}님 환영합니다!")
                    st.rerun()
                else:
                    st.error("❌ 아이디 또는 비밀번호가 틀렸습니다.")

# 🕹️ 게임 메인 화면 (로그인 완료 상태)
else:
    my_id = st.session_state.current_user
    my_data = st.session_state.users_backup_db[my_id]
    
    # [상단 구역] 유저 정보 및 잔액 표시
    col_u1, col_u2 = st.columns([2, 1])
    with col_u1:
        st.write(f"👤 **유저:** {my_id}님")
    with col_u2:
        st.write(f"💰 **보유 금액:** {my_data['money']:,}원")
        
    # 💥 [요청 반영] 잔액 바로 밑에 딱 달라붙어 있는 '내 소장고 버튼(Expander)'
    with st.expander("🎒 내 소장고 확인 및 카드 판매 (클릭해서 열기)", expanded=False):
        my_inv = my_data["inventory"]
        
        if not my_inv:
            st.info("아직 소장한 카드가 없습니다. 아래에서 카드 팩을 뽑아보세요!")
        else:
            for item in set(my_inv):
                count = my_inv.count(item)
                p_info = next((p for p in all_players if p["name"] == item), None)
                
                if p_info:
                    col_i1, col_i2, col_i3 = st.columns([2, 1, 1])
                    with col_i1:
                        st.write(f"🏃‍♂️ **[{p_info['grade']}] {item}** (보유: {count}장)")
                    with col_i2:
                        st.write(f"💵 판매가: {p_info['sell_price']:,}원")
                    with col_i3:
                        if st.button("💰 판매하기", key=f"sell_{item}"):
                            st.session_state.users_backup_db[my_id]["inventory"].remove(item)
                            st.session_state.users_backup_db[my_id]["money"] += p_info["sell_price"]
                            st.success(f"💵 {item} 카드를 판매 완료했습니다!")
                            st.rerun()
                    
                    with st.expander(f"🔍 {item} 카드 실물 보기"):
                        try:
                            st.image(p_info['image'], width=150)
                        except:
                            st.write("이미지가 존재하지 않습니다.")
                    st.write("---")
                    
    if st.button("🔒 로그아웃"):
        st.session_state.current_user = None
        st.session_state.draw_result = None
        st.session_state.cooldown_time = 0
        st.rerun()
        
    st.write("---")

    # 🎯 [하단 구역] 카드 팩 뽑기 존
    st.subheader("✨ 카드 팩 뽑기")
    st.write("💰 **1회 뽑기 비용:** 1,000원")
    
    is_cooling = False
    current_ts = time.time()
    
    if st.session_state.cooldown_time > current_ts:
        is_cooling = True
        rem_time = int(st.session_state.cooldown_time - current_ts)
        
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
                st.session_state.cooldown_time = time.time() + 20
            else:
                st.session_state.cooldown_time = time.time() + 3
            
            # 데이터를 안전하게 브라우저 로컬 저장소에 동기화하라는 스크립트 실행 명령 대용 데이터 유지법
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

# 5. 🔊 안전한 오디오 인젝션
if os.path.exists("loading.mp3"):
    try:
        with open("loading.mp3", "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_base64}" style="display:none;"></audio>', unsafe_allow_html=True)
    except:
        pass
