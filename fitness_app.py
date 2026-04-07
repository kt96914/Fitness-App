import streamlit as st
import streamlit_authenticator as stauth
import plotly.express as px
import pandas as pd

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="FITMINDS Pro", page_icon="🧠", layout="wide")

# --- 2. AUTHENTICATION CONFIG ---
# In a real-world app, this would be loaded from a Database or YAML file.
if 'config' not in st.session_state:
    st.session_state.config = {
        "credentials": {
            "usernames": {
                "admin": {
                    "email": "admin@fitminds.com",
                    "name": "Admin User",
                    "password": "abc" # This will be hashed automatically
                }
            }
        },
        "cookie": {
            "expiry_days": 30,
            "key": "fitminds_signature",
            "name": "fitminds_cookie"
        }
    }

authenticator = stauth.Authenticate(
    st.session_state.config['credentials'],
    st.session_state.config['cookie']['name'],
    st.session_state.config['cookie']['key'],
    st.session_state.config['cookie']['expiry_days']
)

# --- 3. LOGIN INTERFACE ---
name, authentication_status, username = authenticator.login(location='main')

if authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.info('Please log in. Use "admin" / "abc" or Register below.')
    # Simple Registration Toggle
    with st.expander("New User? Register here"):
        new_email = st.text_input("Email")
        new_username = st.text_input("Choose Username")
        new_name = st.text_input("Full Name")
        new_password = st.text_input("Password", type="password")
        if st.button("Register"):
            st.session_state.config['credentials']['usernames'][new_username] = {
                "email": new_email, "name": new_name, "password": new_password
            }
            st.success("Registered! You can now log in.")

# --- 4. AUTHENTICATED APP CONTENT ---
if authentication_status:
    # Initialize User Data
    if 'user_weight' not in st.session_state: st.session_state.user_weight = 80.0
    if 'lifts' not in st.session_state:
        st.session_state.lifts = {"Squat": 0.0, "Bench": 0.0, "Deadlift": 0.0}

    # CSS for UI
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { min-width: 320px !important; }
        .hero-text { font-size: 2.2rem; font-weight: 700; border-left: 6px solid #007bff; padding-left: 15px; margin-bottom: 20px; }
        .m-card { border: 1px solid rgba(128,128,128,0.3); border-radius: 15px; padding: 25px; text-align: center; background: rgba(128,128,128,0.05); }
        .m-card h2 { color: #007bff; font-weight: 800; margin: 0; }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"### Welcome, {name}! 👋")
        st.write("---")
        st.session_state.user_weight = st.number_input("Bodyweight (kg) ⚖️", value=st.session_state.user_weight, step=0.1)
        menu = st.radio("NAVIGATION", ["🚀 Performance", "🥗 Nutrition", "🏋️ Training Lab"])
        st.write("---")
        authenticator.logout('Logout 🚪', 'sidebar')

    # STRENGTH LOGIC
    total_kg = sum(st.session_state.lifts.values())
    ratio = total_kg / st.session_state.user_weight if st.session_state.user_weight > 0 else 0
    if ratio < 2.5: rank, color = "Beginner 🐣", "#888888"
    elif ratio < 3.5: rank, color = "Intermediate ⚡", "#17a2b8"
    elif ratio < 4.5: rank, color = "Advanced 🔥", "#007bff"
    else: rank, color = "Elite 👑", "#d4af37"

    if menu == "🚀 Performance":
        st.markdown('<p class="hero-text">Performance Dashboard</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="m-card"><h4>⚖️ Weight</h4><h2>{st.session_state.user_weight}</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="m-card"><h4>🏗️ Total</h4><h2>{total_kg}</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="m-card"><h4>🏆 Rank</h4><h2 style="color:{color}; font-size:1.2rem !important;">{rank}</h2></div>', unsafe_allow_html=True)
        
        st.write("##")
        st.markdown("### 📊 LIFT BREAKDOWN")
        l1, l2, l3 = st.columns(3)
        l1.metric("🏋️ Squat", f"{st.session_state.lifts['Squat']} kg")
        l2.metric("🎯 Bench", f"{st.session_state.lifts['Bench']} kg")
        l3.metric("💀 Deadlift", f"{st.session_state.lifts['Deadlift']} kg")

    elif menu == "🥗 Nutrition":
        st.markdown('<p class="hero-text">Nutrition Engine</p>', unsafe_allow_html=True)
        bw = st.session_state.user_weight
        p, c, f = int(bw * 2.2), int(bw * 4.0), int(bw * 0.9)
        
        n1, n2, n3 = st.columns(3)
        with n1: st.markdown(f'<div class="m-card"><h4>🥩 Protein</h4><h2>{p}g</h2></div>', unsafe_allow_html=True)
        with n2: st.markdown(f'<div class="m-card"><h4>🍚 Carbs</h4><h2>{c}g</h2></div>', unsafe_allow_html=True)
        with n3: st.markdown(f'<div class="m-card"><h4>🥑 Fats</h4><h2>{f}g</h2></div>', unsafe_allow_html=True)
        
        st.write("---")
        fig = px.pie(names=['Protein', 'Carbs', 'Fats'], values=[p*4, c*4, f*9], hole=0.5, 
                     color_discrete_sequence=['#007bff', '#00d4ff', '#17a2b8'])
        fig.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=350, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "🏋️ Training Lab":
        st.markdown('<p class="hero-text">Training Lab</p>', unsafe_allow_html=True)
        with st.container(border=True):
            ex = st.selectbox("Exercise", ["Squat", "Bench", "Deadlift"])
            val = st.number_input("Max Weight (kg)", step=2.5)
            if st.button("UPDATE RECORD"):
                st.session_state.lifts[ex] = val
                st.balloons()
                st.rerun()
