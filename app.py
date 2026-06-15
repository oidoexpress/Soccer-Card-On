import streamlit as st
import random
import time
import json
import base64

# 1. 페이지 설정 및 스크롤 버그 방지 CSS
st.set_page_config(page_title="동네축구 카드 뽑기 게임", page_icon="⚽", layout="centered")

# [음악 파일 읽어오기]
def get_audio_html(audio_file):
    try:
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        return f'<audio autoplay src="data:audio/mp3;base64,{audio_base64}">'
    except FileNotFoundError:
        return ""

audio_html = get_audio_html("loading.mp3")

# [발로란트 인트로 로딩 연출 CSS + 오디오 인젝션]
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #11141a;
        color: #ece8e1;
        overflow-y: auto !important;
        height: auto !important;
    }}
    html, body {{
        overflow-y: auto !important;
    }}
    
    #loading-overlay {{
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #11141a;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        animation: fadeOut 0.5s ease-in-out 3.5s forwards;
    }}
    
    .valorant-logo {{
        font-size: 70px;
        font-weight: 900;
        color: #ff4655;
        letter-spacing: 8px;
        margin-bottom: 20px;
        animation: glitch 1.5s infinite;
    }}
    
    .loading-bar-container {{
        width: 200px;
        height: 3px;
        background-color: #232936;
        overflow: hidden;
        position: relative;
    }}
    
    .loading-bar {{
        width: 100%;
        height: 100%;
        background-color: #ff4655;
        position: absolute;
        left: -100%;
        animation: scan 1.5s infinite ease-in-out;
    }}
    
    @keyframes scan {{
        0% {{ left: -100%; }}
        50% {{ left: 0%; }}
        100% {{ left: 100%; }}
    }}
    @keyframes glitch {{
        0% {{ transform: scale(1); opacity: 0.9; }}
        50% {{ transform: scale(1.03); opacity: 1; text-shadow: 2px 2px #00f3ff; }}
        100% {{ transform: scale(1); opacity: 0.9; }}
    }}
    @keyframes fadeOut {{
        to {{ opacity: 0; visibility: hidden; }}
    }}
    </style>
    
    {audio_html}
    
    <div id="loading-overlay">
        <div class="valorant-logo">⚽ V ⚽</div>
        <div class="loading-bar-container">
            <div class="loading-bar"></div>
        </div>
        <p style="color: #677080; margin-top: 15px; font-family: monospace; letter-spacing: 3px; font-size: 12px;">📢 터치하면 시스템 사운드가 활성화됩니다...</p>
    </div>
""", unsafe_allow_html=True)

# 2. 데이터 파일 저장/로드 함수 정의
DATA_FILE = "game_save.json"

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"test": {"password": "1234", "money": 5000, "inventory": []}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "users_db" not in st.session_state:
    st.session_state.users_db = load_data()

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# 3. 💥 카드 데이터 정정 (마크롱, 노무현, 안창혁만 유지) 💥
rare_players = [
    {"name": "마크롱", "image": "UEFA Champions League 24 STAR 마크롱.png", "sell_price": 50000, "grade": "🔥 전설 (10%)"}
]

normal_players = [
    {"name": "노무현", "image": "KICK-OFF 23-24 노무현.png", "sell_price": 1000, "grade": "일반 (90%)"},
    {"name": "안창혁", "image": "안창혁.png", "sell_price": 1000, "grade": "일반 (90%)"}
]

all_players = rare_players + normal_players

# 4. 메인 화면 출력
main_container = st.container()

with main_container:
    st.title("⚽동네축구 카드 뽑기 매니저 게임")

    # 🔐 로그인 / 회원가입 화면
    if st.session_state.current_user is None:
        st.subheader("🔑 로그인 및 회원가입")
        menu = ["로그인", "회원가입"]
        choice = st.radio("원하는 작업을 선택하세요", menu, horizontal=True)
        
        user_id = st.text_input("아이디 (ID)", key="login_id")
        user_pw = st.text_input("비밀번호 (Password)", type="password", key="login_pw")
        
        if choice == "회원가입":
            if st.button("📝 계정 만들기"):
                st.session_state.users_db = load_data()
                if user_id in st.session_state.users_db:
                    st.error("❌ 이미 존재하는 아이디입니다.")
                elif user_id == "" or user_pw == "":
                    st.warning("⚠️ 아이디와 비밀번호를 입력해 주세요.")
                else:
                    st.session_state.users_db[user_id] = {"password": user_pw, "money": 5000, "inventory": []}
                    save_data(st.session_state.users_db)
                    st.success("🎉 회원가입 완료! 로그인을 진행해 주세요.")
                    
        elif choice == "로그인":
            if st.button("🚀 로그인하기"):
                st.session_state.users_db = load_data()
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
                    st.error("❌ 잔액이 부족합니다! 소장 중인 카드를 팔아서 돈을 모으세요.")
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
                    save_data(st.session_state.users_db)
                    
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
                                save_data(st.session_state.users_db)
                                
                                st.success(f"💵 {item} 카드를 판매 완료했습니다!")
                                st.rerun()
                        
                        with st.expander(f"🔍 {item} 카드 실물 확인"):
                            try:
                                st.image(p_info['image'], width=150)
                            except:
                                st.write("이미지가 존재하지 않습니다.")
                        st.write("---")
