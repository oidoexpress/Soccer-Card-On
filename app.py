import streamlit as st
import random
import time

st.set_page_config(page_title="축구 카드 뽑기", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ 레전드 축구 카드 가챠 앱")
st.write("직접 만든 한정판 축구 카드를 획득해 보세요!")
