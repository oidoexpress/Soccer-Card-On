import streamlit as st
import random
import time
import os
import base64
import json

# 1. 페이지 설정
st.set_page_config(page_title="동네 축구 카드 매니저", page_icon="⚽", layout="wide")

# [영구 파일 DB 로드/세이브]
DB_FILE = "database.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"test": {"password": "1234", "money": 10000, "inventory": []}}

def save_db(db_data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=4)

users_db = load_db()

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "draw_result" not in st.session_state:
    st.session_state.draw_result = None
if "cooldown_time" not in st.session_state:
    st.session_state.cooldown_time = 0

# 2. 카드 데이터 정의
rare_players = [
    {"name": "마크롱", "image": "UEFA Champions League 24 STAR 마크롱.png", "sell_price": 50000, "grade": "🏆 UCL"},
    {"name": "세루 기라시", "image": "UEFA Champions League 25 STAR 세루 기라시.png", "sell_price": 50000, "grade": "🏆 UCL"},
    {"name": "주앙 네베스", "image": "UEFA Champions League 25 STAR 주앙 네베스.png", "sell_price": 51000, "grade": "🏆 UCL"},
    {"name": "하피냐", "image": "UEFA Champions League 25 XI 하피냐.png", "sell_price": 52000, "grade": "🏆 UCL"}
]

normal_players = [
    {"name": "노무현", "image": "KICK-OFF 23-24 노무현.png", "sell_price": 1000, "grade": "🏃 KICK-OFF"},
    {"name": "안창혁", "image": "안창혁.png", "sell_price": 1000, "grade": "🏃 KICK-OFF"},
    {"name": "크리스티아누 호날두", "image": "KICK OFF 21 크리스티아누 호날두.webp", "sell_price": 1000, "grade": "🏃 KICK-OFF"}
]

# 💥 [신규 등급] TOTS 손흥민 전용 카드 데이터
tots_son_players = [
    {"name": "22TOTS 손흥민", "image": "22TOTS 손흥민.webp", "sell_price": 80000, "grade": "🔥 TOTS"},
    {"name": "23TOTS MOMENT 손흥민", "image": "23TOTS MOMENT 손흥민.webp", "sell_price": 95000, "grade": "🔥 TOTS"},
    {"name": "UTOTS 손흥민", "image": "UTOTS 손흥민.webp", "sell_price": 120000, "grade": "🔥 TOTS"}
]

# 전체 선수 동기화 (소장고 노출용)
all_players = rare_players + normal_players + tots_son_players

# 3. 스타일 및 스크롤 패치
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }
    .stTextInput input {
        color: #ece8e1 !important;
        background-color: #232936 !important;
        border: 1px solid #ff4655 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 비디오 재생 로직 (UCL 및 TOTS 연출 통합 사용)
def play_ucl_video():
    video_placeholder = st.empty()
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

# 4. 로그인 화면 및 게임 분기
if st.session_state.current_user is None:
    st.title("⚽ 동네 축구 카드 매니저")
    st.write("---")
    st.subheader("🔑 로그인 및 회원가입")
    menu = ["로그인", "회원가입"]
    choice = st.radio("원하는 작업을 선택하세요", menu, horizontal=True)
    
    with st.form(key="auth_form"):
        user_id = st.text_input("아이디 (ID)")
        user_pw = st.text_input("비밀번호 (Password)", type="password")
        submit_button = st.form_submit_button(label="🚀 실행하기", use_container_width=True)
        
        if submit_button:
            if choice == "회원가입":
                if user_id in users_db:
                    st.error("❌ 이미 존재하는 아이디입니다.")
                elif user_id == "" or user_pw == "":
                    st.warning("⚠️ 아이디와 비밀번호를 입력해 주세요.")
                else:
                    users_db[user_id] = {"password": user_pw, "money": 10000, "inventory": []}
                    save_db(users_db)
                    st.success("🎉 회원가입 완료! 로그인을 선택하고 다시 눌러주세요.")
            elif choice == "로그인":
                if user_id in users_db and users_db[user_id]["password"] == user_pw:
                    st.session_state.current_user = user_id
                    st.success(f"👋 {user_id}님 환영합니다!")
                    st.rerun()
                else:
                    st.error("❌ 아이디 또는 비밀번호가 틀렸습니다.")

else:
    my_id = st.session_state.current_user
    my_data = users_db[my_id]
    
    # 사이드바 영역 (내 정보 및 소장고)
    with st.sidebar:
        st.header("⚽ 매니저 센터")
        st.write(f"👤 **유저:** {my_id}님")
        st.write(f"💰 **보유 금액:** {my_data['money']:,}원")
        
        if st.button("🔒 로그아웃", use_container_width=True):
            st.session_state.current_user = None
            st.session_state.draw_result = None
            st.session_state.cooldown_time = 0
            st.rerun()
            
        st.write("---")
        st.subheader("🎒 내 소장고 & 판매")
        my_inv = my_data["inventory"]
        
        if not my_inv:
            st.info("소장한 카드가 없습니다.")
        else:
            for item in set(my_inv):
                count = my_inv.count(item)
                p_info = next((p for p in all_players if p["name"] == item), None)
                
                if p_info:
                    st.write(f"🏃‍♂️ **[{p_info['grade']}] {item}** ({count}장)")
                    col_i1, col_i2 = st.columns([1, 1])
                    with col_i1:
                        st.write(f"💵 {p_info['sell_price']:,}원")
                    with col_i2:
                        if st.button("💰 판매", key=f"sell_{item}"):
                            users_db[my_id]["inventory"].remove(item)
                            users_db[my_id]["money"] += p_info["sell_price"]
                            save_db(users_db)
                            st.rerun()
                    
                    with st.expander("🔍 실물 보기"):
                        try:
                            st.image(p_info['image'], use_container_width=True)
                        except:
                            st.write("이미지 없음")
                    st.write("---")

    # 메인 화면 (상점)
    st.title("🛒 카드 팩 상점")
    st.write("---")
    
    is_cooling = False
    current_ts = time.time()
    if st.session_state.cooldown_time > current_ts:
        is_cooling = True
        rem_time = int(st.session_state.cooldown_time - current_ts)
    else:
        st.session_state.draw_result = None

    # --- 1번 팩: 일반 카드 팩 ---
    st.markdown("### 🎯 동네 축구 일반 카드 팩")
    st.write("💵 **비용:** 1,000원 | 📊 **확률:** KICK-OFF (90%), UCL (10%)")
    
    btn_text_normal = f"⏳ 쿨타임 대기 중... ({rem_time}초)" if is_cooling else "🔥 일반 카드 팩 오픈! (1,000원)"
    if st.button(btn_text_normal, key="btn_normal", type="secondary", use_container_width=True, disabled=is_cooling):
        if my_data["money"] < 1000:
            st.sidebar.error("❌ 잔액이 부족합니다!")
        else:
            users_db[my_id]["money"] -= 1000
            with st.spinner("⚡ 팩을 뜯는 중..."):
                time.sleep(0.6)
                percentage = random.randint(1, 100)
                if percentage <= 10:
                    lucky_player = random.choice(rare_players)
                    is_special = True
                else:
                    lucky_player = random.choice(normal_players)
                    is_special = False
            
            users_db[my_id]["inventory"].append(lucky_player["name"])
            save_db(users_db)
            st.session_state.draw_result = lucky_player
            
            if is_special:
                play_ucl_video()
                st.session_state.cooldown_time = time.time() + 20
            else:
                st.session_state.cooldown_time = time.time() + 3
            st.rerun()

    st.write("---")

    # --- 2번 팩: UCL 전용 프리미엄 팩 ---
    st.markdown("### 🏆 UCL 전용 프리미엄 팩")
    st.write("💵 **비용:** 50,000원 | 📊 **확률:** UCL 등급 카드 100% 확정 등장!")
    
    btn_text_ucl = f"⏳ UCL 당첨 연출 대기 중... ({rem_time}초)" if is_cooling else "✨ UCL 전용 팩 오픈! (50,000원)"
    if st.button(btn_text_ucl, key="btn_ucl_pack", type="primary", use_container_width=True, disabled=is_cooling):
        if my_data["money"] < 50000:
            st.sidebar.error("❌ 잔액이 부족합니다!")
        else:
            users_db[my_id]["money"] -= 50000
            with st.spinner("🌟 UEFA 챔피언스리그 팩 개봉 중..."):
                time.sleep(0.6)
                lucky_player = random.choice(rare_players)
            
            users_db[my_id]["inventory"].append(lucky_player["name"])
            save_db(users_db)
            st.session_state.draw_result = lucky_player
            
            play_ucl_video()
            st.session_state.cooldown_time = time.time() + 20
            st.rerun()
            
    st.write("---")

    # --- 💥 3번 팩: 손흥민 스페셜 팩 (신설!) ---
    st.markdown("### 🔥 손흥민 TOTS 스페셜 프리미엄 팩")
    st.write("💵 **비용:** 100,000원 | 📊 **확률:** **손흥민 TOTS 한정판 카드 100% 확정 등장!**")
    
    btn_text_son = f"⏳ 손흥민 소환 연출 대기 중... ({rem_time}초)" if is_cooling else "🇰🇷 손흥민 스페셜 팩 오픈! (100,000원)"
    if st.button(btn_text_son, key="btn_son_pack", type="primary", use_container_width=True, disabled=is_cooling):
        if my_data["money"] < 100000:
            st.sidebar.error("❌ 잔액이 부족합니다!")
        else:
            users_db[my_id]["money"] -= 100000
            with st.spinner("⚡ 대한민국 레전드 손흥민 카드 오픈 중..."):
                time.sleep(0.6)
                # 오직 TOTS 등급 리스트에서만 랜덤 추출
                lucky_player = random.choice(tots_son_players)
            
            users_db[my_id]["inventory"].append(lucky_player["name"])
            save_db(users_db)
            st.session_state.draw_result = lucky_player
            
            # 레전드 등급이므로 20초 연출 발동
            play_ucl_video()
            st.session_state.cooldown_time = time.time() + 20
            st.rerun()

    # 결과물 중앙 화면에 노출
    if is_cooling and st.session_state.draw_result:
        st.write("---")
        p_res = st.session_state.draw_result
        st.success(f"🎉 **[{p_res['grade']}] {p_res['name']}** 선수를 뽑았습니다!")
        
        col_c1, col_c2, col_c3 = st.columns([1, 1.5, 1])
        with col_c2:
            try:
                st.image(p_res['image'], use_container_width=True)
            except:
                st.error(f"❌ '{p_res['image']}' 이미지를 불러오지 못했습니다.")
        
        time.sleep(1)
        st.rerun()

if os.path.exists("loading.mp3"):
    try:
        with open("loading.mp3", "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_base64}" style="display:none;"></audio>', unsafe_allow_html=True)
    except:
        pass
