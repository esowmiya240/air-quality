# aqi_app_with_login.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random
import hashlib
import sqlite3
import time

# Page config
st.set_page_config(
    page_title="AQI Predictor - Login",
    page_icon="🔐",
    layout="wide"
)

# Initialize database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, 
                  password TEXT,
                  email TEXT,
                  phone TEXT,
                  created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Create new user
def create_user(username, password, email, phone):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                 (username, hash_password(password), email, phone, datetime.now()))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# Verify login
def verify_login(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
             (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user is not None

# Initialize DB
init_db()

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'page' not in st.session_state:
    st.session_state.page = "login"

# Login/Signup Page
def login_page():
    st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .login-container {
        background: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        max-width: 400px;
        margin: 50px auto;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Center the login box
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #667eea;">🌍 Air Quality Predictor</h1>
            <p style="color: #666;">Login to access the system</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login/Signup tabs
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("👤 Username", placeholder="Enter username")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter password")
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("🚀 Login", use_container_width=True)
                with col2:
                    if st.form_submit_button("🔄 Reset", use_container_width=True):
                        st.rerun()
                
                if submit:
                    if username and password:
                        if verify_login(username, password):
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.page = "main"
                            st.success("✅ Login successful!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    else:
                        st.warning("⚠️ Please enter both username and password")
        
        with tab2:
            with st.form("signup_form"):
                new_username = st.text_input("👤 Username", placeholder="Choose username")
                new_password = st.text_input("🔒 Password", type="password", placeholder="Choose password")
                confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter password")
                email = st.text_input("📧 Email", placeholder="Enter email")
                phone = st.text_input("📱 Phone", placeholder="Enter phone number")
                
                if st.form_submit_button("📝 Create Account", use_container_width=True):
                    if new_username and new_password and confirm_password and email and phone:
                        if new_password == confirm_password:
                            if create_user(new_username, new_password, email, phone):
                                st.success("✅ Account created! Please login.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Username already exists")
                        else:
                            st.error("❌ Passwords do not match")
                    else:
                        st.warning("⚠️ Please fill all fields")

# Main AQI App
def main_app():
    # Sidebar with user info
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px;">
            <h3>👋 Welcome, {st.session_state.username}!</h3>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "📌 Navigation",
            ["🏠 Dashboard", "📊 Predict AQI", "📈 History", "👤 Profile", "⚙️ Settings"]
        )
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.page = "login"
            st.rerun()
    
    # Main content based on navigation
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📊 Predict AQI":
        show_predictor()
    elif page == "📈 History":
        show_history()
    elif page == "👤 Profile":
        show_profile()
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard():
    st.title("🏠 Dashboard")
    st.markdown("---")
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Today's AQI", "142", "+12")
    with col2:
        st.metric("City", "Chennai", "📍")
    with col3:
        st.metric("Status", "Unhealthy", "⚠️")
    with col4:
        st.metric("Users Online", "1,234", "+56")
    
    st.markdown("---")
    
    # Recent predictions
    st.subheader("📊 Recent AQI Readings")
    
    # Sample data
    data = pd.DataFrame({
        'Time': ['6 AM', '9 AM', '12 PM', '3 PM', '6 PM'],
        'AQI': [85, 110, 145, 168, 152]
    })
    
    fig = go.Figure(data=[
        go.Scatter(x=data['Time'], y=data['AQI'], mode='lines+markers')
    ])
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def show_predictor():
    st.title("📊 AQI Predictor")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Enter Values")
        
        pm25 = st.number_input("PM2.5 (μg/m³)", 0.0, 500.0, 35.0)
        pm10 = st.number_input("PM10 (μg/m³)", 0.0, 600.0, 70.0)
        no2 = st.number_input("NO2 (ppb)", 0.0, 200.0, 40.0)
        so2 = st.number_input("SO2 (ppb)", 0.0, 100.0, 20.0)
        co = st.number_input("CO (ppm)", 0.0, 50.0, 2.0)
        o3 = st.number_input("O3 (ppb)", 0.0, 300.0, 60.0)
        
        if st.button("🔮 Predict AQI", type="primary", use_container_width=True):
            # Calculate AQI
            aqi = (pm25 * 2.5 + pm10 * 1.2 + no2 * 0.5 + so2 * 0.3 + co * 10 + o3 * 0.4) / 10
            
            # Store in session
            st.session_state.last_aqi = round(aqi, 1)
            
            # Save to history
            save_to_history(st.session_state.username, aqi, pm25, pm10, no2, so2, co, o3)
            
            st.success("✅ Prediction complete!")
    
    with col2:
        st.subheader("Results")
        
        if 'last_aqi' in st.session_state:
            aqi = st.session_state.last_aqi
            
            # Determine color and status
            if aqi <= 50:
                color = "#28a745"
                status = "Good"
            elif aqi <= 100:
                color = "#ffc107"
                status = "Moderate"
            elif aqi <= 150:
                color = "#ffc107"
                status = "Unhealthy for Sensitive Groups"
            elif aqi <= 200:
                color = "#dc3545"
                status = "Unhealthy"
            elif aqi <= 300:
                color = "#dc3545"
                status = "Very Unhealthy"
            else:
                color = "#dc3545"
                status = "Hazardous"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <h1 style="font-size: 60px; color: {color};">{aqi}</h1>
                <h3 style="color: {color};">{status}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Health tips
            if aqi <= 50:
                st.success("✅ Air quality is good. Safe for outdoor activities.")
            elif aqi <= 100:
                st.warning("⚠️ Moderate. Sensitive individuals be cautious.")
            elif aqi <= 150:
                st.warning("😷 Unhealthy for sensitive groups. Wear masks.")
            else:
                st.error("🚨 Unhealthy! Avoid outdoor activities.")

def show_history():
    st.title("📈 Prediction History")
    st.markdown("---")
    
    # Get user history from database
    history = get_user_history(st.session_state.username)
    
    if history:
        df = pd.DataFrame(history, columns=['Date', 'AQI', 'PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3'])
        st.dataframe(df, use_container_width=True)
        
        # Chart
        fig = go.Figure(data=[
            go.Scatter(x=df['Date'], y=df['AQI'], mode='lines+markers')
        ])
        fig.update_layout(title="AQI History", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📭 No history yet. Make some predictions!")

def show_profile():
    st.title("👤 User Profile")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Profile Information")
        
        # Get user details from database
        user = get_user_details(st.session_state.username)
        
        if user:
            st.write(f"**Username:** {user[0]}")
            st.write(f"**Email:** {user[2]}")
            st.write(f"**Phone:** {user[3]}")
            st.write(f"**Member Since:** {user[4]}")
    
    with col2:
        st.subheader("Statistics")
        stats = get_user_stats(st.session_state.username)
        st.write(f"**Total Predictions:** {stats['total']}")
        st.write(f"**Average AQI:** {stats['avg']}")
        st.write(f"**Highest AQI:** {stats['max']}")
        st.write(f"**Lowest AQI:** {stats['min']}")

def show_settings():
    st.title("⚙️ Settings")
    st.markdown("---")
    
    with st.form("settings_form"):
        st.subheader("Notification Settings")
        
        email_notify = st.checkbox("Email Notifications")
        sms_notify = st.checkbox("SMS Notifications")
        
        st.subheader("Alert Threshold")
        threshold = st.slider("Alert when AQI exceeds:", 50, 300, 150)
        
        st.subheader("Display Settings")
        theme = st.selectbox("Theme", ["Light", "Dark"])
        language = st.selectbox("Language", ["English", "Tamil", "Hindi"])
        
        if st.form_submit_button("Save Settings"):
            st.success("✅ Settings saved!")

# Database helper functions
def save_to_history(username, aqi, pm25, pm10, no2, so2, co, o3):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (username TEXT, date TIMESTAMP, aqi REAL,
                  pm25 REAL, pm10 REAL, no2 REAL, so2 REAL, co REAL, o3 REAL)''')
    c.execute("INSERT INTO history VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
             (username, datetime.now(), aqi, pm25, pm10, no2, so2, co, o3))
    conn.commit()
    conn.close()

def get_user_history(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (username TEXT, date TIMESTAMP, aqi REAL,
                  pm25 REAL, pm10 REAL, no2 REAL, so2 REAL, co REAL, o3 REAL)''')
    c.execute("SELECT date, aqi, pm25, pm10, no2, so2, co, o3 FROM history WHERE username=? ORDER BY date DESC LIMIT 10", (username,))
    history = c.fetchall()
    conn.close()
    return history

def get_user_details(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_stats(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (username TEXT, date TIMESTAMP, aqi REAL,
                  pm25 REAL, pm10 REAL, no2 REAL, so2 REAL, co REAL, o3 REAL)''')
    c.execute("SELECT COUNT(*), AVG(aqi), MAX(aqi), MIN(aqi) FROM history WHERE username=?", (username,))
    stats = c.fetchone()
    conn.close()
    
    return {
        'total': stats[0] if stats[0] else 0,
        'avg': round(stats[1], 1) if stats[1] else 0,
        'max': stats[2] if stats[2] else 0,
        'min': stats[3] if stats[3] else 0
    }

# Main app logic
if not st.session_state.logged_in:
    login_page()
else:
    main_app()