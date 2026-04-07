import streamlit as st
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection
import plotly.express as px
import pandas as pd

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="CoreFit Analytics", page_icon="💪", layout="wide")

# Logo/Header stays at the top permanently
st.markdown('<h1 style="text-align:center; color:#2E7D32; font-weight:900; margin-bottom:0;">💪 COREFIT ANALYTICS</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#666; margin-top:0;">Secure Fitness Tracking Project</p>', unsafe_allow_html=True)

# --- 2. SECURE DATABASE CONNECTION ---
# This line automatically looks for [connections.gsheets] in your Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_users():
    try:
        # ttl=0 ensures we always get the latest registrations
        df = conn.read(ttl="0s") 
        user_dict = {"usernames": {}}
        for _, row in df.iterrows():
            user_dict["usernames"][str(row['username'])] = {
                "name": str(row['name']),
                "password": str(row['password']),
                "email": str(row['email'])
            }
        return user_dict, df
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return {"usernames": {}}, pd.DataFrame()

credentials, full_df = fetch_users()

# --- 3. AUTHENTICATION ENGINE ---
authenticator = stauth.Authenticate(
    credentials,
    "corefit_cookie",
    "auth_key_123",
    cookie_expiry_days=30
)

# Render Login
authenticator.login()

if st.session_state["authentication_status"] is False:
    st.error('Invalid Username or Password')
elif st.session_state["authentication_status"] is None:
    st.info("Please log in or register below.")
    
    # REGISTRATION (This uses the Service Account to WRITE)
    with st.expander("New Member? Register here"):
        with st.form("reg_form"):
            reg_name = st.text_input("Full Name")
            reg_user = st.text_input("Choose Username")
            reg_email = st.text_input("Email Address")
            reg_pass = st.text_input("Create Password", type="password")
            
            if st.form_submit_button("Create My Account"):
                if reg_user and reg_pass:
                    new_user = pd.DataFrame([{"name": reg_name, "username": reg_user, "password": reg_pass, "email": reg_email}])
                    updated_df = pd.concat([full_df, new_user], ignore_index=True)
                    
                    # This call requires the Service Account "Editor" permissions
                    conn.update(data=updated_df)
                    st.success("Account Created! You can now log in.")
                    st.rerun()
                else:
                    st.warning("Please provide both a username and password.")

# --- 4. DASHBOARD (Authenticated Only) ---
if st.session_state["authentication_status"]:
    if 'u_weight' not in st.session_state: st.session_state.u_weight = 70.0
    if 'prs' not in st.session_state:
        st.session_state.prs = {"Pushups": 0, "Squats": 0, "Plank (sec)": 0}

    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state['name']}")
        st.session_state.u_weight = st.number_input("Weight (kg)", value=st.session_state.u_weight)
        page = st.radio("MENU", ["Overview", "Nutrition", "Workout Log"])
        st.write("---")
        authenticator.logout('Sign Out', 'sidebar')

    if page == "Overview":
        st.header("Fitness Overview")
        c1, c2, c3 = st.columns(3)
        c1.metric("Weight", f"{st.session_state.u_weight} kg")
        c2.metric("Pushups PR", f"{st.session_state.prs['Pushups']} reps")
        c3.metric("Squats PR", f"{st.session_state.prs['Squats']} reps")

    elif page == "Nutrition":
        st.header("Daily Macros")
        w = st.session_state.u_weight
        p, c, f = int(w * 2.0), int(w * 3.0), int(w * 0.8)
        st.write(f"**Protein:** {p}g | **Carbs:** {c}g | **Fats:** {f}g")
        fig = px.pie(names=['Protein', 'Carbs', 'Fats'], values=[p*4, c*4, f*9], hole=0.4)
        st.plotly_chart(fig)

    elif page == "Workout Log":
        st.header("Log Activity")
        ex = st.selectbox("Exercise", list(st.session_state.prs.keys()))
        score = st.number_input("Score", min_value=0)
        if st.button("Save Record"):
            st.session_state.prs[ex] = score
            st.success("Record Saved!")
            st.rerun()
