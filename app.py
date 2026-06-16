import streamlit as st
import random
import time
import os
import base64
import json
from datetime import datetime

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
    # 인벤토리 저장 구조 예시: [{"name": "노무현", "rank": 0, "awaken": 0, "training": 0}, ...]
    return {"test": {"password": "1234", "money": 600000, "inventory": [], "team": "선택 없음", "created_at": "2026-01-01"}}

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

# 2. 📋 카드 데이터 마스터 정의 (기본 포지션 및 판매가 정보 등)
# 모든 기본 카드들은 기본적으로 0진화, 0각성, 0특훈 스펙을 가집니다.
rare_players = [
    {"name": "마크롱", "image": "UEFA Champions League 24 STAR 마크롱.png", "sell_price": 50000, "grade": "🏆 UCL", "pos": "GK"},
    {"name": "세루 기라시", "image": "UEFA Champions League 25 STAR 세루 기라시.png", "sell_price": 50000, "grade": "🏆 UCL", "pos": "ST"},
    {"name": "주앙 네베스", "image": "UEFA Champions League 25 STAR 주앙 네베스.png", "sell_price": 51000, "grade": "🏆 UCL", "pos": "CDM"},
    {"name": "하피냐", "image": "UEFA Champions League 25 XI 하피냐.png", "sell_price": 52000, "grade": "🏆 UCL", "pos": "RWF"}
]

normal_players = [
    {"name": "노무현", "image": "KICK-OFF 23-24 노무현.png", "sell_price": 1000, "grade": "🏃 KICK-OFF", "pos": "CF"},
    {"name": "안창혁", "image": "안창혁.png", "sell_price": 1000, "grade": "🏃 KICK-OFF", "pos": "CB"},
    {"name": "크리스티아누 호날두", "image": "KICK OFF 21 크리스티아누 호날두.webp", "sell_price": 1000, "grade": "🏃 KICK-OFF", "pos": "ST"}
]

tots_son_players = [
    {"name": "22TOTS 손흥민", "image": "22TOTS 손흥민.webp", "sell_price": 80000, "grade": "🔥 TOTS", "pos": "LWF"},
    {"name": "23TOTS MOMENT 손흥민", "image": "23TOTS MOMENT 손흥민.webp", "sell_price": 95000, "grade": "🔥 TOTS", "pos": "LWF"},
    {"name": "UTOTS 손흥민", "image": "UTOTS 손흥민.webp", "sell_price": 120000, "grade": "🔥 TOTS", "pos": "LWF"}
]

# ✨ [선수 상점 전용 등록] 히샤를리송 마스터 데이터 (5진, 6각, 21특 고정)
richarlison_master = {
    "name": "HM24 히샤를리송", 
    "image": "HM24 히샤를리송 5진화 6각성 21특훈.png", 
    "buy_price": 500000, 
    "sell_price": 250000, 
    "grade": "🌟 HARD WORKER", 
    "pos": "ST",
    "rank": 5,
    "awaken": 6,
    "training": 21
}

all_players = rare_players + normal_players + tots_son_players + [richarlison_master]

# 3. 스타일 패치
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        width: 100% !important;
        font-size: 16px !important;
    }
    h1, h2, h3, p, span, label {
        font-family: sans-serif !important;
        letter-spacing: normal !important;
    }
    .stTextInput input {
        color: #ece8e1 !important;
        background-color: #232936 !important;
        border: 1px solid #ff4655 !important;
    }
    .profile-card {
        background-color: #1e2430;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #3a4454;
        margin-bottom: 20px;
    }
    .pos-badge {
        background-color: #ff4655;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 12px;
        margin-right: 5px;
    }
    /* 진화, 각성, 특훈용 스펙 스타일 뱃지 */
    .stat-badge {
        font-size: 11px;
        padding: 2px 5px;
        border-radius: 3px;
        font-weight: bold;
        margin-right: 3px;
        color: #ffffff;
    }
    .badge-rank { background-color: #9c27b0; }     /* 진화: 보라 */
    .badge-awaken { background-color: #ff9800; }   /* 각성: 주황 */
    .badge-train { background-color: #00bcd4; }    /* 특훈: 하늘 */
    
    @media (max-width: 1024px) {
        [data-testid="stSidebar"] {
            width: 100% !important;
        }
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

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
                    today_str = datetime.today().strftime('%Y-%m-%d')
                    users_db[user_id] = {
                        "password": user_pw, 
                        "money": 10000, 
                        "inventory": [],
                        "team": "선택 없음",
                        "created_at": today_str
                    }
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
    
    if "team" not in my_data:
        my_data["team"] = "선택 없음"
    if "created_at" not in my_data:
        my_data["created_at"] = "알 수 없음"

    # 과거 단일 스트링 배열 구조 유저 보호 조치용 변환 로직
    updated_inv = []
    for item in my_data["inventory"]:
        if isinstance(item, str):
            if item == "HM24 히샤를리송":
                updated_inv.append({"name": "HM24 히샤를리송", "rank": 5, "awaken": 6, "training": 21})
            else:
                updated_inv.append({"name": item, "rank": 0, "awaken": 0, "training": 0})
        else:
            updated_inv.append(item)
    my_data["inventory"] = updated_inv

    # ==================== 사이드바 영역 (매니저 센터) ====================
    with st.sidebar:
        st.header("⚽ 매니저 센터")
        st.write(f"👤 **유저:** {my_id}님")
        team_emoji = "👑" if my_data["team"] == "레알 마드리드" else "🔵" if my_data["team"] == "바르셀로나" else "⚪" if my_data["team"] == "토트넘" else "🏴"
        st.write(f"🛡️ **소속 팀:** {team_emoji} {my_data['team']}")
        
        if my_data["team"] == "토트넘":
            if os.path.exists("토트넘로고.jpeg"):
                st.image("토트넘로고.jpeg", width=120)
                st.write("")
        elif my_data["team"] == "바르셀로나":
            if os.path.exists("바로셀로나.svg"):
                st.image("바로셀로나.svg", width=120)
                st.write("")
        elif my_data["team"] == "레알 마드리드":
            if os.path.exists("레알마드리드.svg"):
                st.image("레알마드리드.svg", width=120)
                st.write("")

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
            # 중복 노출 최소화를 위한 키 생성 및 유니크 체크
            seen_items = []
            for idx, card in enumerate(my_inv):
                card_key = f"{card['name']}_{card['rank']}_{card['awaken']}_{card['training']}"
                if card_key in seen_items:
                    continue
                seen_items.append(card_key)
                
                p_info = next((p for p in all_players if p["name"] == card["name"]), None)
                if p_info:
                    # 동일 스펙 수량 계산
                    count = sum(1 for c in my_inv if c['name'] == card['name'] and c['rank'] == card['rank'] and c['awaken'] == card['awaken'] and c['training'] == card['training'])
                    
                    st.write(f"🏃‍♂️ **[{p_info['grade']}] <span class='pos-badge'>{p_info['pos']}</span> {card['name']}** ({count}장)", unsafe_allow_html=True)
                    st.markdown(f"""
                        <span class='stat-badge badge-rank'>{card['rank']}진</span>
                        <span class='stat-badge badge-awaken'>{card['awaken']}각</span>
                        <span class='stat-badge badge-train'>{card['training']}특</span>
                    """, unsafe_allow_html=True)
                    
                    col_i1, col_i2 = st.columns([1, 1])
                    with col_i1:
                        # 히샤를리송은 고유 판매가, 나머지는 오리지널 판매가 적용
                        curr_sell_price = richarlison_master["sell_price"] if card["name"] == "HM24 히샤를리송" else p_info["sell_price"]
                        st.write(f"💵 {curr_sell_price Keep:,.0f}원")
                    with col_i2:
                        if st.button("💰 판매", key=f"sell_{card_key}_{idx}"):
                            my_inv.remove(card)
                            users_db[my_id]["money"] += curr_sell_price
                            save_db(users_db)
                            st.rerun()
                    
                    with st.expander("🔍 실물 보기"):
                        try:
                            # 히샤를리송 이미지 예외 처리
                            img_path = "HM24 히샤를리송 5진화 6각성 21특훈.png" if card["name"] == "HM24 히샤를리송" else p_info['image']
                            st.image(img_path, use_container_width=True)
                        except:
                            st.write("이미지 없음")
                    st.write("---")

    # 카드팩 상점, 선수 상점, 프로필 설정 분기
    tab_shop, tab_player_market, tab_profile = st.tabs(["🛒 카드 팩 상점", "🏃‍♂️ 선수 상점", "👤 내 프로필 설정"])

    # ==================== 탭 1: 카드 팩 상점 화면 ====================
    with tab_shop:
        st.title("🛒 카드 팩 상점")
        st.write("---")
        
        is_cooling = False
        current_ts = time.time()
        if st.session_state.cooldown_time > current_ts:
            is_cooling = True
            rem_time = int(st.session_state.cooldown_time - current_ts)
        else:
            st.session_state.draw_result = None

        # 일반 카드 팩
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
                    else:
                        lucky_player = random.choice(normal_players)
                
                # 상점 오픈은 기본 카드이므로 무조건 0진, 0각, 0특으로 인벤토리에 세팅
                new_card = {"name": lucky_player["name"], "rank": 0, "awaken": 0, "training": 0}
                users_db[my_id]["inventory"].append(new_card)
                save_db(users_db)
                
                # 결과 다이얼로그용 전송 데이터 조립
                display_res = lucky_player.copy()
                display_res.update(new_card)
                st.session_state.draw_result = display_res
                
                if lucky_player["grade"] == "🏆 UCL":
                    play_ucl_video()
                    st.session_state.cooldown_time = time.time() + 20
                else:
                    st.session_state.cooldown_time = time.time() + 3
                st.rerun()

        st.write("---")

        # UCL 전용 프리미엄 팩
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
                
                new_card = {"name": lucky_player["name"], "rank": 0, "awaken": 0, "training": 0}
                users_db[my_id]["inventory"].append(new_card)
                save_db(users_db)
                
                display_res = lucky_player.copy()
                display_res.update(new_card)
                st.session_state.draw_result = display_res
                
                play_ucl_video()
                st.session_state.cooldown_time = time.time() + 20
                st.rerun()
                
        st.write("---")

        # 손흥민 스페셜 팩
        st.markdown("### 🔥 손흥민 TOTS 스페셜 프리미엄 팩")
        st.write("💵 **비용:** 100,000원 | 📊 **확률:** 손흥민 TOTS 한정판 카드 100% 확정 등장!")
        
        btn_text_son = f"⏳ 손흥민 소환 연출 대기 중... ({rem_time}초)" if is_cooling else "🇰🇷 손흥민 스페셜 팩 오픈! (100,000원)"
        if st.button(btn_text_son, key="btn_son_pack", type="primary", use_container_width=True, disabled=is_cooling):
            if my_data["money"] < 100000:
                st.sidebar.error("❌ 잔액이 부족합니다!")
            else:
                users_db[my_id]["money"] -= 100000
                with st.spinner("⚡ 대한민국 레전드 손흥민 카드 오픈 중..."):
                    time.sleep(0.6)
                    lucky_player = random.choice(tots_son_players)
                
                new_card = {"name": lucky_player["name"], "rank": 0, "awaken": 0, "training": 0}
                users_db[my_id]["inventory"].append(new_card)
                save_db(users_db)
                
                display_res = lucky_player.copy()
                display_res.update(new_card)
                st.session_state.draw_result = display_res
                
                play_ucl_video()
                st.session_state.cooldown_time = time.time() + 20
                st.rerun()

        if is_cooling and st.session_state.draw_result:
            st.write("---")
            p_res = st.session_state.draw_result
            st.success(f"🎉 **[{p_res['grade']}] {p_res['pos']} {p_res['name']}** 선수를 뽑았습니다!")
            st.markdown(f"📊 **획득 스펙:** {p_res['rank']}진화 | {p_res['awaken']}각성 | {p_res['training']}특훈")
            
            col_c1, col_c2, col_c3 = st.columns([1, 1.5, 1])
            with col_c2:
                try:
                    img_path = "HM24 히샤를리송 5진화 6각성 21특훈.png" if p_res["name"] == "HM24 히샤를리송" else p_res['image']
                    st.image(img_path, use_container_width=True)
                except:
                    st.error(f"❌ 이미지를 불러오지 못했습니다.")
            time.sleep(1)
            st.rerun()

    # ==================== 🏃‍♂️ 탭 2: 선수 상점 화면 (신규 개장) ====================
    with tab_player_market:
        st.title("🏃‍♂️ 선수 다이렉트 영입 상점")
        st.write("---")
        st.subheader("🔥 이주의 한정판 스페셜 매물")
        
        col_m1, col_m2 = st.columns([1, 2])
        
        with col_m1:
            try:
                # 업로드된 이미지를 불러옵니다.
                st.image("HM24 히샤를리송 5진화 6각성 21특훈.png", use_container_width=True)
            except:
                # 파일이 준비되지 않았거나 탐색 안 될 경우 원본 스크린샷으로 대체 구동 지원
                if os.path.exists("Screenshot_20260616-123143~2.png"):
                    st.image("Screenshot_20260616-123143~2.png", caption="HM24 히샤를리송 카드", use_container_width=True)
                else:
                    st.info("🖼️ 선수 이미지 배치 대기 중")
                    
        with col_m2:
            st.markdown(f"### **[{richarlison_master['grade']}] {richarlison_master['name']}**")
            st.markdown(f"**포지션:** <span class='pos-badge'>{richarlison_master['pos']}</span>", unsafe_allow_html=True)
            st.write("---")
            st.markdown(f"""
            🧬 **고정 인카운터 강화 등급 스펙:**
            - **진화 단계:** <span class='stat-badge badge-rank'>{richarlison_master['rank']} 진화</span>
            - **각성 레벨:** <span class='stat-badge badge-awaken'>{richarlison_master['awaken']} 각성</span>
            - **특훈 스탯:** <span class='stat-badge badge-train'>{richarlison_master['training']} 특훈</span>
            """, unsafe_allow_html=True)
            st.write("---")
            st.subheader(f"💵 영입 비용: **{richarlison_master['buy_price']:,} 원**")
            
            # 구매 처리 버튼
            if st.button("🤝 이적료 지불 및 즉시 영입", type="primary", use_container_width=True):
                if my_data["money"] < richarlison_master["buy_price"]:
                    st.error("❌ 잔고가 부족합니다! 카드팩 상점에서 소장 카드를 판매하거나 재정을 확보하세요.")
                else:
                    # 차감 및 인벤토리 삽입 (히샤를리송만 5, 6, 21 보존 상태로 들어감)
                    users_db[my_id]["money"] -= richarlison_master["buy_price"]
                    users_db[my_id]["inventory"].append({
                        "name": richarlison_master["name"],
                        "rank": richarlison_master["rank"],
                        "awaken": richarlison_master["awaken"],
                        "training": richarlison_master["training"]
                    })
                    save_db(users_db)
                    st.balloons()
                    st.success(f"🎉 성공적으로 {richarlison_master['name']} (5진 6각 21특) 선수를 구단으로 영입했습니다!")
                    time.sleep(1.5)
                    st.rerun()

    # ==================== 탭 3: 내 프로필 설정 화면 ====================
    with tab_profile:
        st.title("👤 유저 프로필 센터")
        st.write("---")
        
        col_prof_text, col_prof_logo = st.columns([2, 1])
        
        with col_prof_text:
            st.markdown(f"""
            <div class="profile-card">
                <h3>🆔 구단주 정보</h3>
                <p>• <b>구단주 ID:</b> {my_id}</p>
                <p>• <b>창단일 (가입일):</b> {my_data['created_at']}</p>
                <p>• <b>현재 보유 잔고:</b> {my_data['money']:,} 원</p>
                <p>• <b>총 보유 카드 장수:</b> {len(my_data['inventory'])} 장</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_prof_logo:
            if my_data["team"] == "토트넘":
                if os.path.exists("토트넘로고.jpeg"):
                    st.markdown("<p style='text-align:center; font-weight:bold;'>🛡️ 선택 구단 엠블럼</p>", unsafe_allow_html=True)
                    st.image("토트넘로고.jpeg", width=180)
            elif my_data["team"] == "바르셀로나":
                if os.path.exists("바로셀로나.svg"):
                    st.markdown("<p style='text-align:center; font-weight:bold;'>🛡️ 선택 구단 엠블럼</p>", unsafe_allow_html=True)
                    st.image("바로셀로나.svg", width=180)
            elif my_data["team"] == "레알 마드리드":
                if os.path.exists("레알마드리드.svg"):
                    st.markdown("<p style='text-align:center; font-weight:bold;'>🛡️ 선택 구단 엠블럼</p>", unsafe_allow_html=True)
                    st.image("레알마드리드.svg", width=180)

        st.subheader("🛡️ 선호 팀 고르기")
        st.write("팀을 변경하면 실시간으로 클럽 데이터베이스에 저장됩니다.")
        
        teams_list = ["선택 없음", "레알 마드리드", "바르셀로나", "토트넘"]
        try:
            current_team_index = teams_list.index(my_data["team"])
        except ValueError:
            current_team_index = 0
            
        selected_team = st.selectbox("나의 최애 클럽팀을 선택하세요", teams_list, index=current_team_index)
        
        if selected_team != my_data["team"]:
            users_db[my_id]["team"] = selected_team
            save_db(users_db)
            st.success(f"✅ 구단주님의 선호 클럽이 **{selected_team}**으로 변경되었습니다!")
            time.sleep(1)
            st.rerun()

# 5. 오디오 인젝션
if os.path.exists("loading.mp3"):
    try:
        with open("loading.mp3", "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_base64}" style="display:none;"></audio>', unsafe_allow_html=True)
    except:
        pass
