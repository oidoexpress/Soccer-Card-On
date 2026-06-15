import streamlit as st
import random
import time
import json
import base64
import os

# 1. 💥 [핵심] 하얀 화면 버그 방지 및 강제 스크롤 활성화 CSS 💥
# 기존에 화면 전체를 덮어버리던 방식을 버리고, 안전하게 메인 화면의 스타일만 다크 모드로 튜닝합니다.
st.set_page_config(page_title="동네축구 카드 뽑기 게임", page_icon="⚽", layout="centered")

# 음악 파일이 존재할 때만 안전하게 인젝션 (파일이 없어도 앱이 터지지 않게 방어 코드 적용)
def get_audio_html(audio_file):
    if os.path.exists(audio_file):
        try:
            with open(audio_file, "rb") as f:
                audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode()
            return f'<audio autoplay src="data:audio/mp3;base64,{audio_base64}">'
        except:
            return ""
    return ""

audio_html = get_audio_html("loading.mp3")

st.markdown(f"""
    <style>
    /* 1. 스트림릿 기본 하얀 배경을 발로란트 다크 톤으로 강제 전환 */
    .stApp, [data-testid="stAppViewContainer"] {{
        background-color: #11141a !important;
        color: #ece8e1 !important;
        overflow-y: auto !important;
        height: auto !important;
    }}
    html, body {{
        background-color: #11141a !important;
        overflow-y: auto !important;
    }}
    
    /* 2. 입력창 글씨 색상 가시성 확보 */
    .stTextInput input {{
        color: #ece8e1 !important;
        background-color: #232936 !important;
        border: 1px solid #ff4655 !important;
    }}
    
    /* 3. 탭 글씨 색상 조정 */
    .stTabs [data-baseweb="tab"] {{
        color: #677080 !important;
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        color: #ff4655 !important;
    }}
    
    /* 4. 발로란트 스타일 네온 애니메이션 타이틀 */
    .val-title {{
        font-size: 42px;
        font-weight: 900;
        color: #ff4655;
        letter-spacing: 3px;
        text-shadow: 0px 0px 10px rgba(255, 70, 85, 0.5);
        margin-bottom: 5px;
    }}
    </style>
    
    {audio_html}
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


# 3. 카드 데이터 정의 (요청하신 3명의 선수만 정확히 유지!)
rare_players = [
    {"name": "마크롱", "image": "UEFA Champions League 24 STAR 마크롱.png", "sell_price": 50000, "grade": "🔥 전설 (10%)"}
]

normal_players = [
    {"name": "노무현", "image": "KICK-OFF 23-24 노무현.png", "sell_price": 1000, "grade": "일반 (90%)"},
    {"name": "안창혁", "image": "안창혁.png", "sell_price": 1000, "grade": "일반 (90%)"}
]

all_players = rare_players + normal_players


# 4. 메인 화면 안전하게 빌드 (Manage app 안 눌러도 즉시 로딩되도록 강제 주입)
st.markdown('<div class="val-title">⚽ 동네 축구 카드 뽑기 </div>', unsafe_allow_html=True)
st.write("동네 축구 카드 뽑기 게임에 오신 것을 환영합니다.")
st.write("---")

# 🔐 로그인 / 회원가입 화면
if st.session_state.current_user is None:
    st.subheader("🔑 로그인 및 회원가입")
    menu = ["로그인", "회원가입"]
    choice = st.radio("원하는 작업을 선택하세요", menu, horizontal=True)
    
    user_id = st.text_input("아이디 (ID)", key="login_id")
    user_pw = st.text_input("비밀번호 (Password)", type="password", key="login_pw")
    
    if choice == "회원가입":
        if st.button("📝 계정 만들기", use_container_width=True):
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
        if st.button("🚀 로그인하기", use_container_width=True):
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
    
    if st.button("🔒 로그아웃", size="small"):
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
