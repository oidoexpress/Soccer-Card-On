import streamlit as st
import random
import time

# 1. 페이지 설정
st.set_page_config(page_title="축구 카드 뽑기 게임", page_icon="⚽", layout="centered")

# 2. 게임 데이터베이스 (세션 상태 초기화)
if "users_db" not in st.session_state:
    # 기본 가상 계정 (아이디: test, 비밀번호: 1234)
    st.session_state.users_db = {
        "test": {"password": "1234", "money": 5000, "inventory": []}
    }

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# 3. 카드 데이터 정의 (확률 계산을 위해 리스트 분리)
# 🌟 [10% 확률] 희귀 카드 목록
rare_players = [
    {"name": "마크롱", "image": "UEFA Champions League 24 STAR 마크롱.png", "sell_price": 800, "grade": "🔥 전설 (10%)"},
    {"name": "이현 UCL", "image": "UEFA Champions League 24 STAR 이현.png", "sell_price": 800, "grade": "🔥 전설 (10%)"}
]

# 🌟 [90% 확률] 일반 카드 목록
normal_players = [
    {"name": "노무현", "image": "KICK-OFF 23-24 노무현.png", "sell_price": 300, "grade": "일반 (90%)"},
    {"name": "권태희", "image": "권태희.png", "sell_price": 300, "grade": "일반 (90%)"},
    {"name": "안창혁", "image": "안창혁.png", "sell_price": 300, "grade": "일반 (90%)"},
    {"name": "이현", "image": "이현.png", "sell_price": 300, "grade": "일반 (90%)"}
]

# 전체 도감 조회를 위한 통합 리스트
all_players = rare_players + normal_players


# --- 화면 구현 ---

st.title("⚽ 풋볼 카드 뽑기 매니저 게임")

# 🔐 4. 로그인 / 회원가입 화면
if st.session_state.current_user is None:
    st.subheader("🔑 로그인 및 회원가입")
    menu = ["로그인", "회원가입"]
    choice = st.radio("원하는 작업을 선택하세요", menu, horizontal=True)
    
    user_id = st.text_input("아이디 (ID)", key="login_id")
    user_pw = st.text_input("비밀번호 (Password)", type="password", key="login_pw")
    
    if choice == "회원가입":
        if st.button("📝 계정 만들기"):
            if user_id in st.session_state.users_db:
                st.error("❌ 이미 존재하는 아이디입니다.")
            elif user_id == "" or user_pw == "":
                st.warning("⚠️ 아이디와 비밀번호를 입력해 주세요.")
            else:
                st.session_state.users_db[user_id] = {"password": user_pw, "money": 5000, "inventory": []}
                st.success("🎉 회원가입 완료! 로그인을 진행해 주세요.")
                
    elif choice == "로그인":
        if st.button("🚀 로그인하기"):
            if user_id in st.session_state.users_db and st.session_state.users_db[user_id]["password"] == user_pw:
                st.session_state.current_user = user_id
                st.success(f"👋 {user_id}님 환영합니다!")
                st.rerun()
            else:
                st.error("❌ 아이디 또는 비밀번호가 틀렸습니다.")

# 🕹️ 5. 게임 메인 화면 (로그인 후)
else:
    my_id = st.session_state.current_user
    my_data = st.session_state.users_db[my_id]
    
    # 상단바 유저 정보
    col_u1, col_u2 = st.columns([2, 1])
    with col_u1:
        st.write(f"👤 **유저:** {my_id}님")
    with col_u2:
        st.write(f"💰 **보유 금액:** {my_data['money']}원")
    
    if st.button("🔒 로그아웃"):
        st.session_state.current_user = None
        st.rerun()
        
    st.write("---")
    
    # 탭 메뉴 나누기
    tab1, tab2 = st.tabs(["✨ 카드 팩 뽑기", "🎒 내 소장고 & 판매"])
    
    # --- [탭 1: 카드 뽑기] ---
    with tab1:
        st.subheader("🎯 대박 축구 카드 팩")
        st.write("💰 **1회 뽑기 비용:** 1,000원")
        st.caption("※ 마크롱, 이현 UCL 카드는 10% 확률로 등장합니다!")
        
        if st.button("🔥 카드 팩 오픈! (1,000원 결제)", type="primary", use_container_width=True):
            if my_data["money"] < 1000:
                st.error("❌ 잔액이 부족합니다! 소장 중인 카드를 팔아서 돈을 모으세요.")
            else:
                # 돈 차감
                st.session_state.users_db[my_id]["money"] -= 1000
                
                with st.spinner("⚡ 카드 팩을 뜯는 중..."):
                    time.sleep(1.2)
                    
                    # 💥 10% vs 90% 확률 작동 주사위 던지기
                    percentage = random.randint(1, 100)
                    
                    if percentage <= 10:  # 1~10 나오면 10% 확률 당첨!
                        lucky_player = random.choice(rare_players)
                        st.balloons() # 전설은 특별히 풍선 이펙트!
                    else:  # 11~100 나오면 90% 일반 카드
                        lucky_player = random.choice(normal_players)
                
                st.success(f"🎉 **[{lucky_player['grade']}] {lucky_player['name']}** 선수를 뽑았습니다!")
                
                # 유저 인벤토리에 추가
                st.session_state.users_db[my_id]["inventory"].append(lucky_player["name"])
                
                # 카드 이미지 출력
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
                            st.success(f"💵 {item} 카드를 판매 완료했습니다!")
                            st.rerun()
                    
                    with st.expander(f"🔍 {item} 카드 실물 확인"):
                        try:
                            st.image(p_info['image'], width=150)
                        except:
                            st.write("이미지가 존재하지 않습니다.")
                    st.write("---")
