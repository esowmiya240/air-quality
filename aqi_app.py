import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
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
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, 
                  password TEXT,
                  email TEXT,
                  phone TEXT,
                  created_at TIMESTAMP)''')
    # History table
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT, 
                  date TIMESTAMP, 
                  aqi REAL,
                  pm25 REAL, 
                  pm10 REAL, 
                  no2 REAL, 
                  so2 REAL, 
                  co REAL, 
                  o3 REAL,
                  status TEXT)''')
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
    except Exception as e:
        print(f"Error creating user: {e}")
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
if 'last_prediction' not in st.session_state:
    st.session_state.last_prediction = None
if 'notification_shown' not in st.session_state:
    st.session_state.notification_shown = False

# Function to get AQI status and color
def get_aqi_status(aqi):
    if aqi <= 50:
        return "Good", "#28a745", "✅ Safe for outdoor activities"
    elif aqi <= 100:
        return "Moderate", "#ffc107", "⚠️ Moderate. Sensitive individuals be cautious"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "#ff9800", "😷 Sensitive groups should wear masks"
    elif aqi <= 200:
        return "Unhealthy", "#dc3545", "🚨 Avoid outdoor activities"
    elif aqi <= 300:
        return "Very Unhealthy", "#9c27b0", "🚫 Stay indoors, wear masks if outside"
    else:
        return "Hazardous", "#6c757d", "☣️ Emergency conditions, stay inside"

# Calculate AQI
def calculate_aqi(pm25, pm10, no2, so2, co, o3):
    # Simple weighted calculation (you can replace with actual AQI formula)
    aqi = (pm25 * 2.5 + pm10 * 1.2 + no2 * 0.5 + so2 * 0.3 + co * 10 + o3 * 0.4) / 10
    return round(aqi, 1)

# Save prediction to history
def save_to_history(username, aqi, pm25, pm10, no2, so2, co, o3):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    status, _, _ = get_aqi_status(aqi)
    try:
        c.execute('''INSERT INTO history 
                     (username, date, aqi, pm25, pm10, no2, so2, co, o3, status)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (username, datetime.now(), aqi, pm25, pm10, no2, so2, co, o3, status))
        conn.commit()
    except Exception as e:
        print(f"Error saving to history: {e}")
    finally:
        conn.close()

# Get user history
def get_user_history(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('''SELECT date, aqi, pm25, pm10, no2, so2, co, o3, status 
                     FROM history 
                     WHERE username=? 
                     ORDER BY date DESC 
                     LIMIT 20''', (username,))
        history = c.fetchall()
    except Exception as e:
        print(f"Error getting history: {e}")
        history = []
    finally:
        conn.close()
    return history

# Get user details
def get_user_details(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

# Get user statistics
def get_user_stats(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('''SELECT COUNT(*), AVG(aqi), MAX(aqi), MIN(aqi) 
                     FROM history 
                     WHERE username=?''', (username,))
        stats = c.fetchone()
    except:
        stats = (0, 0, 0, 0)
    finally:
        conn.close()
    
    return {
        'total': stats[0] if stats[0] else 0,
        'avg': round(stats[1], 1) if stats[1] else 0,
        'max': stats[2] if stats[2] else 0,
        'min': stats[3] if stats[3] else 0
    }

# Login/Signup Page
def login_page():
    st.markdown("""
    <style>
    .stApp {
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
        <div style="text-align: center; margin-bottom: 30px; color: white;">
            <h1 style="color: white;">🌍 Air Quality Predictor</h1>
            <p style="color: white;">Login to access the system</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login/Signup tabs
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("👤 Username", placeholder="Enter username")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter password")
                
                if st.form_submit_button("🚀 Login", use_container_width=True):
                    if username and password:
                        if verify_login(username, password):
                            st.session_state.logged_in = True
                            st.session_state.username = username
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
                    if all([new_username, new_password, confirm_password, email, phone]):
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
        if 'nav_page' not in st.session_state:
            st.session_state.nav_page = "🏠 Dashboard"
            
        pages = ["🏠 Dashboard", "📊 Predict AQI", "📈 History", "👤 Profile", "⚙️ Settings"]
        selected_page = st.radio("📌 Navigation", pages, index=pages.index(st.session_state.nav_page))
        st.session_state.nav_page = selected_page
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
    
    # Main content based on navigation
    if st.session_state.nav_page == "🏠 Dashboard":
        show_dashboard()
    elif st.session_state.nav_page == "📊 Predict AQI":
        show_predictor()
    elif st.session_state.nav_page == "📈 History":
        show_history()
    elif st.session_state.nav_page == "👤 Profile":
        show_profile()
    elif st.session_state.nav_page == "⚙️ Settings":
        show_settings()

def show_dashboard():
    st.title("🏠 Dashboard")
    st.markdown("---")
    
    # Get user history for dashboard
    history = get_user_history(st.session_state.username)
    
    if history:
        df = pd.DataFrame(history, columns=['Date', 'AQI', 'PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3', 'Status'])
        latest_aqi = df['AQI'].iloc[0] if not df.empty else 0
        latest_status, color, _ = get_aqi_status(latest_aqi)
        
        # Stats cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current AQI", f"{latest_aqi}", f"{latest_status}")
        with col2:
            st.metric("Total Predictions", f"{len(df)}", "")
        with col3:
            st.metric("Avg AQI", f"{df['AQI'].mean():.1f}", "")
        with col4:
            st.metric("Max AQI", f"{df['AQI'].max():.1f}", "")
        
        st.markdown("---")
        
        # Recent predictions chart
        st.subheader("📊 AQI History Chart")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Date'].head(10),
            y=df['AQI'].head(10),
            mode='lines+markers',
            name='AQI',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))
        
        # Add threshold lines
        fig.add_hline(y=50, line_dash="dash", line_color="green", annotation_text="Good")
        fig.add_hline(y=100, line_dash="dash", line_color="yellow", annotation_text="Moderate")
        fig.add_hline(y=150, line_dash="dash", line_color="orange", annotation_text="Unhealthy")
        fig.add_hline(y=200, line_dash="dash", line_color="red", annotation_text="Very Unhealthy")
        
        fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="AQI Value",
            hovermode='x'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent predictions table
        st.subheader("📋 Recent Predictions")
        st.dataframe(df[['Date', 'AQI', 'Status']].head(5), use_container_width=True)
        
    else:
        st.info("📭 No predictions yet. Go to Predict AQI page to make your first prediction!")
        
        # Show sample chart
        st.subheader("📊 Sample Chart")
        sample_data = pd.DataFrame({
            'Date': ['6 AM', '9 AM', '12 PM', '3 PM', '6 PM'],
            'AQI': [85, 110, 145, 168, 152]
        })
        
        fig = go.Figure(data=[
            go.Scatter(x=sample_data['Date'], y=sample_data['AQI'], mode='lines+markers')
        ])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def show_predictor():
    st.title("📊 AQI Predictor")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Enter Values")
        
        with st.form("prediction_form"):
            pm25 = st.number_input("PM2.5 (μg/m³)", 0.0, 500.0, 35.0, step=1.0)
            pm10 = st.number_input("PM10 (μg/m³)", 0.0, 600.0, 70.0, step=1.0)
            no2 = st.number_input("NO2 (ppb)", 0.0, 200.0, 40.0, step=1.0)
            so2 = st.number_input("SO2 (ppb)", 0.0, 100.0, 20.0, step=1.0)
            co = st.number_input("CO (ppm)", 0.0, 50.0, 2.0, step=0.1)
            o3 = st.number_input("O3 (ppb)", 0.0, 300.0, 60.0, step=1.0)
            
            if st.form_submit_button("🔮 Predict AQI", type="primary", use_container_width=True):
                # Calculate AQI
                aqi = calculate_aqi(pm25, pm10, no2, so2, co, o3)
                
                # Store in session
                st.session_state.last_prediction = {
                    'aqi': aqi,
                    'pm25': pm25,
                    'pm10': pm10,
                    'no2': no2,
                    'so2': so2,
                    'co': co,
                    'o3': o3,
                    'timestamp': datetime.now()
                }
                
                # Save to history
                save_to_history(st.session_state.username, aqi, pm25, pm10, no2, so2, co, o3)
                
                # Reset notification flag for new prediction
                st.session_state.notification_shown = False
                
                st.success("✅ Prediction complete!")
                st.rerun()
    
    with col2:
        st.subheader("Results")
        
        if st.session_state.last_prediction:
            aqi = st.session_state.last_prediction['aqi']
            status, color, message = get_aqi_status(aqi)
            
            # Show AQI value
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                <h1 style="font-size: 72px; color: {color}; margin: 0;">{aqi}</h1>
                <h3 style="color: {color};">{status}</h3>
                <p style="color: #666;">{message}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show notification if not shown yet
            if not st.session_state.notification_shown:
                if aqi > 150:
                    st.error(f"🚨 **ALERT:** High AQI detected! {message}")
                    st.balloons()
                elif aqi > 100:
                    st.warning(f"⚠️ **CAUTION:** {message}")
                st.session_state.notification_shown = True
            
            # Show prediction details
            st.markdown("---")
            st.subheader("📊 Prediction Details")
            
            details_df = pd.DataFrame({
                'Parameter': ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3'],
                'Value': [
                    st.session_state.last_prediction['pm25'],
                    st.session_state.last_prediction['pm10'],
                    st.session_state.last_prediction['no2'],
                    st.session_state.last_prediction['so2'],
                    st.session_state.last_prediction['co'],
                    st.session_state.last_prediction['o3']
                ],
                'Unit': ['μg/m³', 'μg/m³', 'ppb', 'ppb', 'ppm', 'ppb']
            })
            
            st.dataframe(details_df, use_container_width=True)
            
            # Health recommendations
            st.markdown("---")
            st.subheader("💪 Health Recommendations")
            
            if aqi <= 50:
                st.success("• Great day for outdoor activities!\n• Keep windows open for ventilation")
            elif aqi <= 100:
                st.info("• Sensitive individuals should limit outdoor exertion\n• Keep windows closed if sensitive")
            elif aqi <= 150:
                st.warning("• Wear masks when going outside\n• Reduce prolonged outdoor activities\n• Keep windows closed")
            else:
                st.error("• Avoid all outdoor activities\n• Wear N95 masks if necessary\n• Use air purifiers indoors\n• Keep windows and doors closed")
        
        else:
            st.info("👆 Enter values and click Predict to see results")

def show_history():
    st.title("📈 Prediction History")
    st.markdown("---")
    
    # Get user history
    history = get_user_history(st.session_state.username)
    
    if history:
        # Convert to DataFrame
        df = pd.DataFrame(history, columns=['Date', 'AQI', 'PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3', 'Status'])
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.multiselect("Filter by Status", df['Status'].unique(), default=[])
        with col2:
            date_range = st.date_input("Date Range", [])
        with col3:
            sort_by = st.selectbox("Sort by", ["Date", "AQI", "Status"])
        
        # Apply filters
        filtered_df = df.copy()
        if status_filter:
            filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Predictions", len(filtered_df))
        with col2:
            st.metric("Average AQI", f"{filtered_df['AQI'].mean():.1f}")
        with col3:
            st.metric("Highest AQI", f"{filtered_df['AQI'].max():.1f}")
        with col4:
            st.metric("Lowest AQI", f"{filtered_df['AQI'].min():.1f}")
        
        st.markdown("---")
        
        # Chart
        st.subheader("📊 AQI Trend")
        
        fig = go.Figure()
        
        # Add AQI line
        fig.add_trace(go.Scatter(
            x=filtered_df['Date'],
            y=filtered_df['AQI'],
            mode='lines+markers',
            name='AQI',
            line=dict(color='#667eea', width=2),
            marker=dict(
                size=8,
                color=filtered_df['AQI'],
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="AQI")
            )
        ))
        
        # Add threshold zones
        fig.add_hrect(y0=0, y1=50, line_width=0, fillcolor="green", opacity=0.1, annotation_text="Good")
        fig.add_hrect(y0=50, y1=100, line_width=0, fillcolor="yellow", opacity=0.1, annotation_text="Moderate")
        fig.add_hrect(y0=100, y1=150, line_width=0, fillcolor="orange", opacity=0.1, annotation_text="Unhealthy")
        fig.add_hrect(y0=150, y1=200, line_width=0, fillcolor="red", opacity=0.1, annotation_text="Very Unhealthy")
        fig.add_hrect(y0=200, y1=300, line_width=0, fillcolor="purple", opacity=0.1, annotation_text="Hazardous")
        
        fig.update_layout(
            height=500,
            xaxis_title="Date",
            yaxis_title="AQI Value",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("📋 Detailed History")
        
        # Format date for display
        filtered_df['Date'] = pd.to_datetime(filtered_df['Date']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Add color coding for AQI
        def color_aqi(val):
            if val <= 50:
                return 'background-color: #28a74520'
            elif val <= 100:
                return 'background-color: #ffc10720'
            elif val <= 150:
                return 'background-color: #ff980020'
            elif val <= 200:
                return 'background-color: #dc354520'
            else:
                return 'background-color: #9c27b020'
        
        styled_df = filtered_df.style.applymap(color_aqi, subset=['AQI'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"aqi_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
    else:
        st.info("📭 No prediction history yet. Go to the Predict AQI page to make your first prediction!")
        
        # Show sample chart
        st.subheader("📊 Sample Chart (No Data)")
        sample_data = pd.DataFrame({
            'Date': ['6 AM', '9 AM', '12 PM', '3 PM', '6 PM'],
            'AQI': [85, 110, 145, 168, 152]
        })
        
        fig = go.Figure(data=[
            go.Scatter(x=sample_data['Date'], y=sample_data['AQI'], mode='lines+markers')
        ])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def show_profile():
    st.title("👤 User Profile")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Profile Information")
        
        # Get user details from database
        user = get_user_details(st.session_state.username)
        
        if user:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                <p><strong>👤 Username:</strong> {user[0]}</p>
                <p><strong>📧 Email:</strong> {user[2]}</p>
                <p><strong>📱 Phone:</strong> {user[3]}</p>
                <p><strong>📅 Member Since:</strong> {user[4]}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Edit profile button
        if st.button("✏️ Edit Profile"):
            st.info("Edit profile feature coming soon!")
    
    with col2:
        st.subheader("Statistics")
        
        # Get user statistics
        stats = get_user_stats(st.session_state.username)
        
        # Create metrics
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Total Predictions", stats['total'])
            st.metric("Average AQI", stats['avg'])
        with col_b:
            st.metric("Highest AQI", stats['max'])
            st.metric("Lowest AQI", stats['min'])
        
        # Activity chart
        if stats['total'] > 0:
            history = get_user_history(st.session_state.username)
            df = pd.DataFrame(history, columns=['Date', 'AQI', 'PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3', 'Status'])
            
            # Count by status
            status_counts = df['Status'].value_counts()
            
            fig = go.Figure(data=[
                go.Pie(labels=status_counts.index, values=status_counts.values)
            ])
            fig.update_layout(title="AQI Status Distribution", height=300)
            st.plotly_chart(fig, use_container_width=True)

def show_settings():
    st.title("⚙️ Settings")
    st.markdown("---")
    
    with st.form("settings_form"):
        st.subheader("🔔 Notification Settings")
        
        email_notify = st.checkbox("Email Notifications", value=True)
        sms_notify = st.checkbox("SMS Notifications", value=False)
        
        if email_notify:
            st.text_input("Notification Email", value=get_user_details(st.session_state.username)[2])
        
        if sms_notify:
            st.text_input("Notification Phone", value=get_user_details(st.session_state.username)[3])
        
        st.markdown("---")
        st.subheader("⚠️ Alert Threshold")
        
        threshold = st.slider("Alert when AQI exceeds:", 50, 300, 150)
        
        st.markdown("---")
        st.subheader("🎨 Display Settings")
        
        theme = st.selectbox("Theme", ["Light", "Dark", "System Default"])
        language = st.selectbox("Language", ["English", "Tamil", "Hindi"])
        
        st.markdown("---")
        st.subheader("📊 Chart Settings")
        
        chart_type = st.selectbox("Default Chart Type", ["Line", "Bar", "Area"])
        show_grid = st.checkbox("Show Grid", value=True)
        
        if st.form_submit_button("💾 Save Settings", use_container_width=True):
            st.success("✅ Settings saved successfully!")
            st.balloons()

# Main app logic
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
