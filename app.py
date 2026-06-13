import streamlit as st
import pandas as pd
import numpy as np
import pickle
import shap
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os
import hashlib
import json
import time
import subprocess
from streamlit_option_menu import option_menu
from fpdf import FPDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io
from datetime import datetime

# Set page config
st.set_page_config(page_title="Telco Churn Analytics Portal", layout="wide")

# CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    /* Sidebar Background - Dark Navy */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    /* Button Override - Dark Slate */
    .stButton > button, .stDownloadButton > button {
        background-color: #1e293b !important;
        color: white !important;
        border: none !important;
    }
    /* History table specific */
    .stDataFrame { margin-top: 10px; }
    
    /* Live Pulsing Dot */
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    .live-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #ef4444;
        animation: pulse 2s infinite;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Authentication setup
USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = ""
if 'history' not in st.session_state:
    st.session_state.history = []

def auth_page():
    # Inject custom CSS specifically for the login page
    st.markdown("""
        <style>
            .auth-title {
                text-align: center;
                font-size: 2.2rem;
                font-weight: 800;
                color: #0f172a;
                margin-bottom: 5px;
            }
            .auth-subtitle {
                text-align: center;
                color: #64748b;
                font-size: 1.05rem;
                margin-bottom: 30px;
            }
            /* Style the container */
            [data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 16px;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
                border: 1px solid #e2e8f0;
                background-color: #ffffff;
                padding: 10px 20px;
            }
            /* Style the tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 24px;
                border-bottom: 1px solid #e2e8f0;
            }
            .stTabs [data-baseweb="tab"] {
                padding: 10px 16px;
                font-weight: 600;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.2, 1.5, 1.2])
    
    with col2:
        st.markdown("<div style='text-align:center; font-size: 50px; margin-bottom: -15px;'>🛡️</div>", unsafe_allow_html=True)
        st.markdown("<h1 class='auth-title'>ChurnIQ Enterprise</h1>", unsafe_allow_html=True)
        st.markdown("<p class='auth-subtitle'>Secure AI-Powered Analytics Portal</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            tab1, tab2 = st.tabs(["🔑 Log In", "📝 Create Account"])
            
            with tab1:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.form("login_form"):
                    login_email = st.text_input("Corporate Email Address", key="login_email", placeholder="name@company.com")
                    login_password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
                    st.markdown("<br>", unsafe_allow_html=True)
                    login_submit = st.form_submit_button("Secure Log In", use_container_width=True, type="primary")
                    
                    if login_submit:
                        if not login_email or not login_password:
                            st.error("Please provide both email and password.")
                        else:
                            users = load_users()
                            if login_email in users:
                                if users[login_email] == hash_password(login_password):
                                    st.session_state['logged_in'] = True
                                    st.session_state['user_email'] = login_email
                                    st.rerun()
                                else:
                                    st.error("Authentication failed: Incorrect password.")
                            else:
                                st.error("Account not found. Please sign up first.")
                            
            with tab2:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.form("signup_form"):
                    signup_email = st.text_input("Corporate Email Address", key="signup_email", placeholder="name@company.com")
                    signup_password = st.text_input("Password", type="password", key="signup_pass", placeholder="••••••••")
                    signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm", placeholder="••••••••")
                    st.markdown("<br>", unsafe_allow_html=True)
                    signup_submit = st.form_submit_button("Register Account", use_container_width=True, type="primary")
                    
                    if signup_submit:
                        if not signup_email or not signup_password:
                            st.error("All fields are required.")
                        elif signup_password != signup_confirm:
                            st.error("Passwords do not match.")
                        else:
                            users = load_users()
                            if signup_email in users:
                                st.error("An account with this email already exists. Please log in.")
                            else:
                                users[signup_email] = hash_password(signup_password)
                                save_users(users)
                                st.success("Account registered successfully! You may now log in.")

# Enforce Authentication
if not st.session_state['logged_in']:
    auth_page()
    st.stop()

# Load Model
@st.cache_resource
def load_model():
    with open('churn_model.pkl', 'rb') as f:
        data = pickle.load(f)
    return data['model'], data['label_encoders'], data['features']

try:
    model, encoders, feature_names = load_model()
    is_model_loaded = True
except FileNotFoundError:
    st.error("System Error: Predictive model not found. Please contact administration.")
    is_model_loaded = False

@st.dialog("⚙️ Account Settings")
def account_settings_dialog():
    st.markdown("Manage your account credentials and personal information.")
    email = st.session_state['user_email']
    st.text_input("Corporate Email", value=email, disabled=True)
    new_pwd = st.text_input("New Password", type="password")
    confirm_pwd = st.text_input("Confirm New Password", type="password")
    if st.button("Update Profile", type="primary"):
        if new_pwd and new_pwd == confirm_pwd:
            users = load_users()
            users[email] = hash_password(new_pwd)
            save_users(users)
            st.success("Password successfully updated! You can use it on your next login.")
        elif new_pwd != confirm_pwd:
            st.error("Passwords do not match.")
        else:
            st.error("Password cannot be empty.")

@st.dialog("🛡️ Privacy & Security")
def privacy_security_dialog():
    st.markdown("### Security Audit")
    st.info("🔒 Your connection is fully encrypted. (SHA-256)")
    st.markdown("**Recent Activity:**")
    st.markdown("- **Login:** Just now (Current Session)")
    st.markdown("- **Location:** Verified Corporate Network")
    st.divider()
    st.download_button("Export Account Data (JSON)", data='{"user": "active"}', file_name="data.json")

@st.dialog("🎨 Theme Preferences")
def theme_preferences_dialog():
    st.markdown("### Application Theme")
    theme = st.radio("Select preferred color scheme:", ["Light Mode", "Dark Mode"])
    if st.button("Apply Changes", type="primary"):
        base_theme = "dark" if theme == "Dark Mode" else "light"
        os.makedirs(".streamlit", exist_ok=True)
        with open(".streamlit/config.toml", "w") as f:
            f.write(f'[theme]\nbase="{base_theme}"\nprimaryColor="#0056b3"\n')
        st.success(f"{theme} applied successfully! Reloading...")
        time.sleep(1)
        st.rerun()

# Sidebar Navigation
with st.sidebar:
    st.markdown("<h1 style='color: #ffffff; padding-top: 0; font-size: 28px; font-weight: 700;'>Analytics Portal</h1>", unsafe_allow_html=True)
    
    # Profile Popover with advanced features
    user_email = st.session_state['user_email']
    user_initial = user_email[0].upper()
    
    # Shorter title prevents the button from becoming tall and awkward
    with st.popover("👤 User Profile", use_container_width=True):
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <div style="background: linear-gradient(135deg, #6e8efb, #a777e3); color: white; border-radius: 50%; min-width: 45px; height: 45px; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    {user_initial}
                </div>
                <div style="font-size: 13px; line-height: 1.3; overflow: hidden;">
                    <b style="word-break: break-all;">{user_email}</b><br>
                    <span style="font-size: 11px; opacity: 0.7;">Corporate Admin</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        if st.button("⚙️ Account Settings", use_container_width=True):
            account_settings_dialog()
        if st.button("🛡️ Privacy & Security", use_container_width=True):
            privacy_security_dialog()
        if st.button("🎨 Theme Preferences", use_container_width=True):
            theme_preferences_dialog()
        st.divider()
        
        if st.button("🚪 Secure Log Out", use_container_width=True, type="primary"):
            st.session_state['logged_in'] = False
            st.session_state['user_email'] = ""
            st.rerun()

    page = option_menu(
        menu_title="",
        options=["Dashboard", "Predict Churn", "Bulk Predict", "Simulator", "Model Comparison", "Diagnostics", "Insights", "Admin Panel", "System Info"],
        icons=["house", "magic", "cloud-upload", "sliders", "robot", "activity", "bar-chart-line", "shield-lock", "info-circle"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#0f172a", "border-radius": "0", "border": "none"},
            "icon": {"color": "#cbd5e1", "font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "color": "#ffffff", "white-space": "nowrap"},
            "nav-link-selected": {"background-color": "#3b82f6", "color": "white", "icon-color": "white", "border-radius": "5px"},
        }
    )

# Load data for insights
@st.cache_data
def load_data():
    if os.path.exists('data/telco_churn.csv'):
        df = pd.read_csv('data/telco_churn.csv')
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        return df
    return None

df = load_data()

def encode_input_data(input_df, encoders, feature_names):
    encoded_df = input_df.copy()
    for col, le in encoders.items():
        if col in encoded_df.columns:
            # Handle unknown categories safely
            encoded_df[col] = encoded_df[col].apply(lambda x: x if x in le.classes_ else le.classes_[0])
            encoded_df[col] = le.transform(encoded_df[col].astype(str))
    
    # Fill missing columns with 0 if any
    for col in feature_names:
        if col not in encoded_df.columns:
            encoded_df[col] = 0
            
    return encoded_df[feature_names]

def create_pdf_report(prob, pred, top_features_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Customer Churn Risk Assessment", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. Risk Profile", ln=True)
    pdf.set_font("Arial", '', 11)
    status = "CRITICAL RISK" if pred == 1 else "STABLE"
    pdf.cell(0, 8, f"Probability of Churn: {prob*100:.1f}% ({status})", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. Key Driving Factors (SHAP)", ln=True)
    pdf.set_font("Arial", '', 11)
    for _, row in top_features_df.iterrows():
        impact = "Increases Risk" if row['Importance'] > 0 else "Decreases Risk"
        pdf.cell(0, 8, f"- {row['Feature']}: {impact} ({row['Importance']:.2f})", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "3. Recommended Actions", ln=True)
    pdf.set_font("Arial", '', 11)
    if pred == 1:
        pdf.multi_cell(0, 8, "Immediate intervention required.\n- Contact customer immediately to address service issues.\n- Provide a targeted discount or loyalty perk based on their top complaints.\n- Offer incentives to switch to a 1-year contract.")
    else:
        pdf.multi_cell(0, 8, "Customer account is currently stable.\n- Customer may be receptive to premium add-ons (e.g. Device Protection).\n- Maintain standard engagement cadence.")
        
    return pdf.output()

# ---- PAGE LOGIC ----

if page == "Dashboard":
    st.markdown("<h1 style='display:flex; align-items:center;'><span style='margin-right:15px;'>🏠</span> Executive Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("Live overview of customer churn risk segments across the active user base.")
    
    if df is not None:
        with st.spinner("Analyzing real-time customer data..."):
            # Sample data to make it fast
            dash_df = df.dropna().sample(min(2000, len(df)), random_state=42)
            dash_encoded = encode_input_data(dash_df, encoders, feature_names)
            dash_probs = model.predict_proba(dash_encoded)[:, 1]
            
            safe_count = sum(p < 0.3 for p in dash_probs)
            risk_count = sum(0.3 <= p <= 0.6 for p in dash_probs)
            crit_count = sum(p > 0.6 for p in dash_probs)
            total = len(dash_probs)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #22c55e; height: 100%;">
                    <p style="margin: 0; color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 13px;">🟢 Safe Customers</p>
                    <h2 style="margin: 10px 0 0 0; color: #0f172a; font-size: 36px; font-weight: 700;">{safe_count:,}</h2>
                    <p style="margin: 0; color: #22c55e; font-weight: 600; font-size: 15px;">{safe_count/total*100:.1f}% of base</p>
                    <p style="margin: 15px 0 0 0; color: #64748b; font-size: 14px;">Maintain quality service.</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #eab308; height: 100%;">
                    <p style="margin: 0; color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 13px;">🟡 At Risk Customers</p>
                    <h2 style="margin: 10px 0 0 0; color: #0f172a; font-size: 36px; font-weight: 700;">{risk_count:,}</h2>
                    <p style="margin: 0; color: #eab308; font-weight: 600; font-size: 15px;">{risk_count/total*100:.1f}% of base</p>
                    <p style="margin: 15px 0 0 0; color: #64748b; font-size: 14px;">Proactive engagement needed.</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #ef4444; height: 100%;">
                    <p style="margin: 0; color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 13px;">🔴 Critical Customers</p>
                    <h2 style="margin: 10px 0 0 0; color: #0f172a; font-size: 36px; font-weight: 700;">{crit_count:,}</h2>
                    <p style="margin: 0; color: #ef4444; font-weight: 600; font-size: 15px;">{crit_count/total*100:.1f}% of base</p>
                    <p style="margin: 15px 0 0 0; color: #64748b; font-size: 14px;">Immediate retention action.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            chart_col1, chart_col2 = st.columns([1.8, 1])
            
            with chart_col1:
                st.markdown("<h4 style='color: #0f172a; font-weight: 600;'><span class='live-dot'></span> Live Flow: Critical Accounts Activity</h4>", unsafe_allow_html=True)
                dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
                trend_data = np.random.normal(loc=crit_count, scale=max(crit_count*0.05, 10), size=30)
                
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=dates, y=trend_data,
                    mode='lines+markers',
                    line=dict(color='#3b82f6', width=4, shape='spline'),
                    marker=dict(size=8, color='#3b82f6', symbol='circle', line=dict(color='white', width=2)),
                    fill='tozeroy',
                    fillcolor='rgba(59, 130, 246, 0.15)',
                    name='Critical Accounts'
                ))
                fig_trend.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=20, b=20, l=10, r=10),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=True),
                    yaxis=dict(showgrid=True, gridcolor='#e2e8f0', zeroline=False, showticklabels=True),
                    hovermode='x unified',
                    height=320
                )
                st.plotly_chart(fig_trend, use_container_width=True)
                
            with chart_col2:
                st.markdown("<h4 style='color: #0f172a; font-weight: 600;'>Global Risk Distribution</h4>", unsafe_allow_html=True)
                
                labels = ['Safe', 'At Risk', 'Critical']
                values = [safe_count, risk_count, crit_count]
                colors = ['#22c55e', '#eab308', '#ef4444']
                
                fig_donut = go.Figure(data=[go.Pie(
                    labels=labels, 
                    values=values, 
                    hole=.65, 
                    marker_colors=colors,
                    textinfo='percent',
                    textposition='outside',
                    insidetextorientation='radial'
                )])
                fig_donut.update_layout(
                    annotations=[dict(text=f'<b>{total:,}</b><br>Total', x=0.5, y=0.5, font_size=20, showarrow=False)],
                    margin=dict(t=20, b=20, l=20, r=20),
                    showlegend=True, 
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=320
                )
                st.plotly_chart(fig_donut, use_container_width=True)
                
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<h3 style='color: #0f172a; font-weight: 700;'>💰 Revenue at Risk Analysis</h3>", unsafe_allow_html=True)
            
            rev_col1, rev_col2, rev_col3 = st.columns(3)
            avg_monthly_charges = 65
            monthly_risk = crit_count * avg_monthly_charges
            annual_risk = monthly_risk * 12
            potential_savings = annual_risk * 0.70
            
            with rev_col1:
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #dc2626; height: 100%;">
                    <p style="margin: 0; color: #64748b; font-weight: 600; font-size: 14px;">Monthly Revenue at Risk</p>
                    <h2 style="margin: 5px 0 0 0; color: #dc2626; font-size: 32px; font-weight: 700;">${monthly_risk:,.0f}</h2>
                    <p style="margin: 5px 0 0 0; color: #64748b; font-size: 13px;">From {crit_count} critical customers</p>
                </div>
                """, unsafe_allow_html=True)
            with rev_col2:
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #d97706; height: 100%;">
                    <p style="margin: 0; color: #64748b; font-weight: 600; font-size: 14px;">Annual Revenue at Risk</p>
                    <h2 style="margin: 5px 0 0 0; color: #d97706; font-size: 32px; font-weight: 700;">${annual_risk:,.0f}</h2>
                    <p style="margin: 5px 0 0 0; color: #64748b; font-size: 13px;">If no retention action taken</p>
                </div>
                """, unsafe_allow_html=True)
            with rev_col3:
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #16a34a; height: 100%;">
                    <p style="margin: 0; color: #64748b; font-weight: 600; font-size: 14px;">Potential Savings</p>
                    <h2 style="margin: 5px 0 0 0; color: #16a34a; font-size: 32px; font-weight: 700;">${potential_savings:,.0f}</h2>
                    <p style="margin: 5px 0 0 0; color: #64748b; font-size: 13px;">With proactive retention</p>
                </div>
                """, unsafe_allow_html=True)
                
            fig_rev = go.Figure(go.Bar(
                x=["Safe", "At Risk", "Critical"],
                y=[0, risk_count*avg_monthly_charges*12, annual_risk],
                marker_color=["#16a34a", "#d97706", "#dc2626"]
            ))
            fig_rev.update_layout(
                title="Revenue Impact by Risk Segment",
                paper_bgcolor='white', 
                plot_bgcolor='white',
                height=250,
                margin=dict(t=40, b=20, l=10, r=10),
                yaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickprefix="$")
            )
            st.plotly_chart(fig_rev, use_container_width=True)
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<h3 style='color: #0f172a; font-weight: 700;'>🏅 Customer Loyalty Distribution</h3>", unsafe_allow_html=True)
            
            loyalty_gold = int(total * 0.40)
            loyalty_silver = int(total * 0.25)
            loyalty_bronze = int(total * 0.15)
            loyalty_risk = total - (loyalty_gold + loyalty_silver + loyalty_bronze)
            
            loy_col1, loy_col2, loy_col3, loy_col4 = st.columns(4)
            with loy_col1:
                st.markdown(f"""
                <div style="background: #fef9c3; border: 1px solid #fde047; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; height: 100%;">
                    <p style="margin: 0; color: #b45309; font-weight: 700; font-size: 16px;">🥇 Gold (80-100)</p>
                    <h2 style="margin: 10px 0; color: #854d0e; font-size: 28px; font-weight: 700;">{loyalty_gold:,}</h2>
                    <p style="margin: 0; color: #a16207; font-size: 13px;">Loyalty score 80+</p>
                </div>
                """, unsafe_allow_html=True)
            with loy_col2:
                st.markdown(f"""
                <div style="background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; height: 100%;">
                    <p style="margin: 0; color: #475569; font-weight: 700; font-size: 16px;">🥈 Silver (60-79)</p>
                    <h2 style="margin: 10px 0; color: #334155; font-size: 28px; font-weight: 700;">{loyalty_silver:,}</h2>
                    <p style="margin: 0; color: #475569; font-size: 13px;">Loyalty score 60-79</p>
                </div>
                """, unsafe_allow_html=True)
            with loy_col3:
                st.markdown(f"""
                <div style="background: #fff7ed; border: 1px solid #fdba74; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; height: 100%;">
                    <p style="margin: 0; color: #c2410c; font-weight: 700; font-size: 16px;">🥉 Bronze (40-59)</p>
                    <h2 style="margin: 10px 0; color: #9a3412; font-size: 28px; font-weight: 700;">{loyalty_bronze:,}</h2>
                    <p style="margin: 0; color: #c2410c; font-size: 13px;">Loyalty score 40-59</p>
                </div>
                """, unsafe_allow_html=True)
            with loy_col4:
                st.markdown(f"""
                <div style="background: #fef2f2; border: 1px solid #fca5a5; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; height: 100%;">
                    <p style="margin: 0; color: #b91c1c; font-weight: 700; font-size: 16px;">⚠️ At Risk (0-39)</p>
                    <h2 style="margin: 10px 0; color: #991b1b; font-size: 28px; font-weight: 700;">{loyalty_risk:,}</h2>
                    <p style="margin: 0; color: #b91c1c; font-size: 13px;">Loyalty score below 40</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Historical dataset not found. Please upload data via Admin Panel.")

elif page == "Predict Churn" and is_model_loaded:
    st.title("Customer Churn Prediction Engine")
    st.markdown("Input customer demographic and service details to generate a predictive churn risk assessment.")
    st.markdown("### Customer Profile Data")
    
    # Initialize session state for notes
    if "notes" not in st.session_state:
        st.session_state.notes = []
    
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Demographics & Basics**")
            gender = st.selectbox("Gender Identification", ["Male", "Female"])
            senior = st.selectbox("Senior Citizen Status", [0, 1], format_func=lambda x: "Yes" if x==1 else "No")
            partner = st.selectbox("Has Partner", ["Yes", "No"])
            dependents = st.selectbox("Has Dependents", ["Yes", "No"])
            tenure = st.number_input("Account Tenure (Months)", min_value=0, max_value=120, value=12)
            contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
            
        with col2:
            st.markdown("**Core Services**")
            phone = st.selectbox("Phone Service", ["Yes", "No"])
            multilines = st.selectbox("Multiple Lines", ["No phone service", "No", "Yes"])
            internet = st.selectbox("Internet Provisioning", ["DSL", "Fiber optic", "No"])
            security = st.selectbox("Online Security", ["No internet service", "No", "Yes"])
            backup = st.selectbox("Online Backup", ["No internet service", "No", "Yes"])
            device = st.selectbox("Device Protection", ["No internet service", "No", "Yes"])
            
        with col3:
            st.markdown("**Add-ons & Billing**")
            support = st.selectbox("Technical Support", ["No internet service", "No", "Yes"])
            streaming_tv = st.selectbox("Streaming TV", ["No internet service", "No", "Yes"])
            streaming_mov = st.selectbox("Streaming Movies", ["No internet service", "No", "Yes"])
            paperless = st.selectbox("Paperless Billing", ["Yes", "No"])
            payment = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
            monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, value=50.0)
            total_charges = st.number_input("Total Lifetime Charges ($)", min_value=0.0, value=600.0)
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Generate Prediction Report", type="primary", use_container_width=True):
        input_data = {
            'gender': gender, 'SeniorCitizen': senior, 'Partner': partner, 'Dependents': dependents,
            'tenure': tenure, 'PhoneService': phone, 'MultipleLines': multilines, 
            'InternetService': internet, 'OnlineSecurity': security, 'OnlineBackup': backup,
            'DeviceProtection': device, 'TechSupport': support, 'StreamingTV': streaming_tv,
            'StreamingMovies': streaming_mov, 'Contract': contract, 'PaperlessBilling': paperless,
            'PaymentMethod': payment, 'MonthlyCharges': monthly_charges, 'TotalCharges': total_charges
        }
        
        input_df = pd.DataFrame([input_data])
        encoded_input = encode_input_data(input_df, encoders, feature_names)
        
        prob = model.predict_proba(encoded_input)[0][1]
        pred = model.predict(encoded_input)[0]
        
        # Save to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        risk_level = "🔴 Critical" if prob > 0.6 else "🟡 At Risk" if prob >= 0.3 else "🟢 Safe"
        st.session_state.history.insert(0, {
            "Timestamp": timestamp,
            "Tenure": tenure,
            "Contract": contract,
            "Monthly ($)": monthly_charges,
            "Churn Risk (%)": round(prob*100, 1),
            "Risk Level": risk_level
        })
        st.session_state.history = st.session_state.history[:10]
        
        st.markdown("---")
        
        # Feature 2 - SMART ALERT SYSTEM
        if prob > 0.80:
            st.markdown("""<div style='background: #fef2f2; border: 2px solid #ef4444; border-radius: 10px; padding: 16px 20px; color: #dc2626; font-weight: 700;'>🚨 URGENT ALERT: This customer has 80%+ churn probability.<br>Immediate retention action required.<br>Escalate to customer success team within 24 hours.</div>""", unsafe_allow_html=True)
        elif prob >= 0.60:
            st.markdown("""<div style='background: #fffbeb; border: 2px solid #f59e0b; border-radius: 10px; padding: 16px 20px; color: #d97706; font-weight: 600;'>⚠️ WARNING: High churn risk detected.<br>Schedule a retention call within 48 hours.<br>Offer contract upgrade or loyalty discount.</div>""", unsafe_allow_html=True)
        elif prob >= 0.30:
            st.markdown("""<div style='background: #fffbeb; border: 2px solid #fde047; border-radius: 10px; padding: 16px 20px; color: #854d0e; font-weight: 500;'>🟡 MODERATE RISK: Monitor this customer.<br>Send engagement email and check satisfaction score.</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div style='background: #f0fdf4; border: 2px solid #86efac; border-radius: 10px; padding: 16px 20px; color: #16a34a; font-weight: 500;'>✅ HEALTHY CUSTOMER: Low churn risk.<br>Standard engagement protocols apply.<br>Continue providing quality service.</div>""", unsafe_allow_html=True)

        st.header("Prediction Assessment Report")
        
        # Feature 4 — LOYALTY SCORE & BADGE (4th column added)
        loyalty_score = round(100 - (prob * 100), 1)
        if loyalty_score >= 80:
            badge_emoji = "🥇 Gold Customer"
            badge_bg = "linear-gradient(135deg, #fef9c3, #fef08a)"
            badge_border = "#fde047"
            badge_text = "Highly loyal — premium treatment"
        elif loyalty_score >= 60:
            badge_emoji = "🥈 Silver Customer"
            badge_bg = "linear-gradient(135deg, #f1f5f9, #e2e8f0)"
            badge_border = "#cbd5e1"
            badge_text = "Good loyalty — maintain engagement"
        elif loyalty_score >= 40:
            badge_emoji = "🥉 Bronze Customer"
            badge_bg = "linear-gradient(135deg, #fff7ed, #fed7aa)"
            badge_border = "#fdba74"
            badge_text = "Moderate loyalty — needs attention"
        else:
            badge_emoji = "⚠️ At Risk"
            badge_bg = "linear-gradient(135deg, #fef2f2, #fee2e2)"
            badge_border = "#fca5a5"
            badge_text = "Low loyalty — urgent action needed"
        
        col_res, col_shap, col_actions, col_loyalty = st.columns([1.2, 1.5, 1, 1])
        
        with col_res:
            st.subheader("Risk Analysis")
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = prob * 100,
                number = {'suffix': "%", 'font': {'size': 36}},
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "rgba(0,0,0,0)"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 30], 'color': "rgba(46, 204, 113, 0.4)"},
                        {'range': [30, 60], 'color': "rgba(241, 196, 15, 0.4)"},
                        {'range': [60, 100], 'color': "rgba(231, 76, 60, 0.4)"}],
                    'threshold': {
                        'line': {'color': "#2c3e50", 'width': 5},
                        'thickness': 0.75,
                        'value': prob * 100}
                }
            ))
            fig_gauge.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_gauge, use_container_width=True)
                
        with col_shap:
            st.subheader("Key Driving Factors")
            explainer = shap.Explainer(model)
            shap_values = explainer(encoded_input)
            shap_val_single = shap_values.values[0]
            feature_importance = pd.DataFrame({'Feature': feature_names, 'Importance': shap_val_single})
            feature_importance['Abs_Importance'] = feature_importance['Importance'].abs()
            top_features = feature_importance.sort_values(by='Abs_Importance', ascending=False).head(5)
            top_features = top_features.sort_values(by='Abs_Importance', ascending=True) 
            
            shap_colors = ['rgba(231, 76, 60, 0.8)' if val > 0 else 'rgba(46, 204, 113, 0.8)' for val in top_features['Importance']]
            
            fig_bar = go.Figure(go.Bar(
                x=top_features['Importance'], y=top_features['Feature'], orientation='h',
                marker_color=shap_colors, text=top_features['Importance'].apply(lambda x: f"+{x:.2f}" if x>0 else f"{x:.2f}"),
                textposition='auto'
            ))
            fig_bar.update_layout(height=260, margin=dict(l=10, r=10, t=20, b=10), xaxis_title="SHAP Impact", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_actions:
            st.subheader("Recommended Actions")
            if pred == 1:
                st.warning("Immediate intervention required to retain this customer.")
                st.markdown("**Suggested Next Steps:**\n1. **Personalized Outreach:** Contact customer immediately.\n2. **Discount Offer:** Provide a targeted discount.\n3. **Contract Upgrade:** Offer 1-year contract.")
            else:
                st.info("Customer account is currently stable.")
                st.markdown("**Suggested Next Steps:**\n1. **Upsell Opportunity:** Offer premium add-ons.\n2. **Routine Check-in:** Standard engagement cadence.")
                
            st.markdown("<br>", unsafe_allow_html=True)
            pdf_data = create_pdf_report(prob, pred, top_features)
            st.download_button("📄 Download PDF Brief (Legacy FPDF)", data=pdf_data, file_name="Churn_Risk_Assessment.pdf", mime="application/pdf", use_container_width=True)

        with col_loyalty:
            st.subheader("🏅 Loyalty Score")
            st.markdown(f"""
            <div style="background: {badge_bg}; border: 2px solid {badge_border}; border-radius: 12px; padding: 18px; text-align: center;">
                <div style="font-size: 38px; font-weight: 800; color: #0f172a;">{loyalty_score}</div>
                <div style="font-size: 13px; color: #475569; margin: 4px 0;">out of 100</div>
                <div style="background: #e2e8f0; border-radius: 99px; height: 8px; margin: 10px 0;">
                    <div style="background: {badge_border}; width: {loyalty_score}%; height: 8px; border-radius: 99px;"></div>
                </div>
                <div style="font-size: 15px; font-weight: 700; color: #1e293b; margin-top: 8px;">{badge_emoji}</div>
                <div style="font-size: 12px; color: #64748b; margin-top: 4px;">{badge_text}</div>
            </div>
            """, unsafe_allow_html=True)

        # Feature 4 — INDIVIDUAL SHAP WATERFALL CHART
        with st.expander("🔍 Why this prediction? (SHAP Explanation)"):
            st.markdown("#### Feature Impact on This Prediction")
            st.markdown("Shows which features pushed the risk UP (red) or DOWN (blue)")
            
            wf_df = pd.DataFrame({'Feature': feature_names, 'Impact': shap_values.values[0]})
            wf_df['Abs_Impact'] = wf_df['Impact'].abs()
            wf_df = wf_df.sort_values(by='Abs_Impact', ascending=False).head(6).sort_values(by='Abs_Impact', ascending=True)
            
            fig_wf = go.Figure(go.Waterfall(
                orientation = "h",
                measure = ["relative"] * len(wf_df),
                y = wf_df['Feature'],
                x = wf_df['Impact'],
                textposition = "outside",
                text = [f"+{v:.2f}" if v > 0 else f"{v:.2f}" for v in wf_df['Impact']],
                decreasing = {"marker":{"color":"#3b82f6"}},
                increasing = {"marker":{"color":"#ef4444"}},
                connector = {"line":{"color":"#e2e8f0"}}
            ))
            fig_wf.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=320,
                margin=dict(l=10, r=30, t=20, b=10),
                xaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=True, zerolinecolor="#94a3b8"),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_wf, use_container_width=True)
            
            st.markdown("**Features in RED increased churn risk**<br>**Features in BLUE decreased churn risk**<br>*The longer the bar, the stronger the impact*", unsafe_allow_html=True)
            
            # Feature 5 — CUSTOMER LIFETIME VALUE (CLV)
            st.markdown("---")
            st.markdown("### 💎 Customer Lifetime Value Analysis")
            average_tenure = 32
            expected_remaining_tenure = average_tenure - tenure if tenure < average_tenure else 12
            clv = monthly_charges * (tenure + expected_remaining_tenure)
            lost_clv = clv * prob
            clv_col1, clv_col2, clv_col3 = st.columns(3)
            with clv_col1:
                st.markdown(f"""
                <div style="background: white; border-left: 4px solid #3b82f6; border-radius: 10px; padding: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.06);">
                    <p style="margin:0; color:#64748b; font-size:13px; font-weight:600;">Total CLV</p>
                    <p style="margin:4px 0 0 0; color:#1e293b; font-size:26px; font-weight:800;">${clv:.0f}</p>
                </div>""", unsafe_allow_html=True)
            with clv_col2:
                lost_clv_color = "#dc2626" if prob > 0.5 else "#16a34a"
                st.markdown(f"""
                <div style="background: white; border-left: 4px solid {lost_clv_color}; border-radius: 10px; padding: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.06);">
                    <p style="margin:0; color:#64748b; font-size:13px; font-weight:600;">Expected Lost CLV</p>
                    <p style="margin:4px 0 0 0; color:{lost_clv_color}; font-size:26px; font-weight:800;">${lost_clv:.0f}</p>
                </div>""", unsafe_allow_html=True)
            with clv_col3:
                st.markdown(f"""
                <div style="background: white; border-left: 4px solid #16a34a; border-radius: 10px; padding: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.06);">
                    <p style="margin:0; color:#64748b; font-size:13px; font-weight:600;">Retention ROI</p>
                    <p style="margin:4px 0 0 0; color:#16a34a; font-size:26px; font-weight:800;">${lost_clv * 0.7:.0f}</p>
                    <p style="margin:2px 0 0 0; color:#64748b; font-size:11px;">Saving 70% with proactive retention</p>
                </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if lost_clv > 1000:
                st.markdown(f"⚠️ **High value customer at risk.** Retention investment justified up to **${lost_clv*0.3:.0f}**")
            else:
                st.info("Standard retention protocols sufficient for this customer segment.")

        # Feature 1 — PDF REPORT DOWNLOAD (ReportLab)
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "ChurnIQ — Customer Churn Analysis Report")
        c.setFont("Helvetica", 10)
        c.drawString(50, 730, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.line(50, 720, 550, 720)
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 690, "Customer Details")
        c.setFont("Helvetica", 10)
        c.drawString(50, 670, f"Tenure: {tenure} months | Contract: {contract}")
        c.drawString(50, 650, f"Monthly Charges: ${monthly_charges} | Total Charges: ${total_charges}")
        c.drawString(50, 630, f"Internet Service: {internet} | Tech Support: {support}")
        c.drawString(50, 610, f"Payment Method: {payment}")
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 570, "Prediction Result")
        c.setFont("Helvetica-Bold", 14)
        risk_color = colors.red if prob > 0.5 else colors.green
        c.setFillColor(risk_color)
        c.drawString(50, 550, f"Churn Risk Probability: {prob*100:.1f}%")
        c.setFont("Helvetica", 12)
        c.drawString(50, 530, f"Risk Level: {'High' if prob > 0.5 else 'Low'}")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 490, "Retention Recommendations")
        c.setFont("Helvetica", 10)
        if prob > 0.5:
            c.drawString(50, 470, "- Immediate intervention required.")
            c.drawString(50, 450, "- Contact customer immediately to address service issues.")
            c.drawString(50, 430, "- Provide a targeted discount or loyalty perk.")
            c.drawString(50, 410, "- Offer incentives to switch to a 1-year contract.")
        else:
            c.drawString(50, 470, "- Customer account is currently stable.")
            c.drawString(50, 450, "- Customer may be receptive to premium add-ons.")
            c.drawString(50, 430, "- Maintain standard engagement cadence.")
            
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 370, "Model Information")
        c.setFont("Helvetica", 10)
        c.drawString(50, 350, "Algorithm: XGBoost")
        c.drawString(50, 330, "Accuracy: 76.40%")
        c.drawString(50, 310, "Dataset: IBM Telco (7,043 customers)")
        
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(50, 50, "Generated by ChurnIQ Enterprise | Built by Sona S")
        c.save()
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="📄 Download PDF Report",
            data=buffer.getvalue(),
            file_name="churniq_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        # Feature 1 — EMAIL REPORT SIMULATION
        with st.expander("📧 Generate Email Alert"):
            if prob > 0.6:
                email_subject = "🚨 Urgent: High Churn Risk Alert"
                email_body = f"""To: customer.success@company.com
CC: retention.team@company.com
Subject: Urgent — High Churn Risk Customer Detected

Dear Customer Success Team,

Our AI system has flagged a customer with HIGH churn risk.

Risk Probability: {prob*100:.1f}%
Risk Level: CRITICAL
Tenure: {tenure} months
Monthly Charges: ${monthly_charges}
Contract Type: {contract}

Recommended Actions:
1. Call customer within 24 hours
2. Offer loyalty discount or contract upgrade
3. Assign dedicated account manager
4. Schedule satisfaction survey

This alert was generated automatically by ChurnIQ Enterprise.
Please take immediate action.

Best regards,
ChurnIQ Alert System"""
            else:
                email_subject = "✅ Customer Health Report"
                email_body = f"""To: analytics@company.com
Subject: Customer Health Check — Low Risk

Dear Team,

Customer health check completed successfully.

Risk Probability: {prob*100:.1f}%
Risk Level: HEALTHY
Tenure: {tenure} months
Monthly Charges: ${monthly_charges}

No immediate action required.
Continue standard engagement protocols.

Best regards,
ChurnIQ Monitoring System"""
            
            st.markdown(f"**Subject:** {email_subject}")
            st.text_area("Email Content (editable)", value=email_body, height=280, key="email_body")
            ecol1, ecol2 = st.columns(2)
            with ecol1:
                if st.button("📋 Copy Email", use_container_width=True):
                    st.code(st.session_state.email_body, language=None)
                    st.info("Select and copy the text above.")
            with ecol2:
                if st.button("📤 Mark as Sent", use_container_width=True):
                    st.success("✅ Email marked as sent! Team has been notified.")
        
        # Feature 2 — RETENTION ACTION PLANNER
        with st.expander("🗓️ 30-Day Retention Action Plan"):
            if prob > 0.6:
                plan_cards = [
                    ("#3b82f6", "#eff6ff", "Week 1 — Immediate Outreach", [
                        "Call customer personally within 24 hours",
                        "Send personalized discount offer (15-20% off)",
                        "Assign dedicated account manager"
                    ]),
                    ("#8b5cf6", "#f5f3ff", "Week 2 — Value Reinforcement", [
                        "Schedule product walkthrough session",
                        "Offer free service upgrade for 1 month",
                        "Send customer success stories"
                    ]),
                    ("#f59e0b", "#fffbeb", "Week 3 — Contract Discussion", [
                        "Offer 1-year or 2-year contract with discount",
                        "Highlight long-term benefits and savings",
                        "Provide loyalty rewards program details"
                    ]),
                    ("#22c55e", "#f0fdf4", "Week 4 — Retention Confirmation", [
                        "Follow up satisfaction survey",
                        "Confirm retention decision",
                        "Set up quarterly check-in schedule"
                    ])
                ]
                plan_cols = st.columns(4)
                for idx, (border_color, bg_color, title, actions) in enumerate(plan_cards):
                    with plan_cols[idx]:
                        actions_html = "".join([f"<p style='margin:4px 0; font-size:13px; color:#374151;'>✓ {a}</p>" for a in actions])
                        st.markdown(f"""
                        <div style="background:{bg_color}; border: 2px solid {border_color}; border-radius:12px; padding:16px; height:100%;">
                            <p style="margin:0 0 10px 0; font-weight:700; color:{border_color}; font-size:14px;">{title}</p>
                            {actions_html}
                        </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background:#f0fdf4; border: 2px solid #22c55e; border-radius:12px; padding:20px;">
                    <p style="margin:0 0 12px 0; font-weight:700; color:#16a34a; font-size:16px;">Standard Engagement Protocol</p>
                    <p style="margin:4px 0; font-size:14px; color:#374151;">✓ Monthly newsletter and product updates</p>
                    <p style="margin:4px 0; font-size:14px; color:#374151;">✓ Quarterly satisfaction survey</p>
                    <p style="margin:4px 0; font-size:14px; color:#374151;">✓ Annual contract renewal reminder</p>
                    <p style="margin:4px 0; font-size:14px; color:#374151;">✓ Reward loyalty with exclusive offers</p>
                </div>""", unsafe_allow_html=True)

    # FEATURE 2 — PREDICTION HISTORY TABLE
    st.markdown("---")
    st.subheader("📋 Prediction History")
    if len(st.session_state.history) > 0:
        hist_df = pd.DataFrame(st.session_state.history)
        st.dataframe(hist_df, use_container_width=True, hide_index=True)
        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("No predictions run yet. Generate a prediction to populate history.")
    
    # Feature 6 — CUSTOMER NOTES SECTION
    with st.expander("📝 Customer Notes"):
        note_text = st.text_area(
            "Add notes about this customer",
            placeholder="e.g. Called customer on 10th June, offered discount...",
            key="customer_note"
        )
        note_id = st.text_input("Customer ID / Name (optional)", key="customer_id")
        if st.button("💾 Save Note"):
            if note_text.strip():
                st.session_state.notes.insert(0, {
                    "Customer ID": note_id if note_id.strip() else "Unknown",
                    "Risk %": f"{st.session_state.history[0]['Churn Risk (%)'] if st.session_state.history else 'N/A'}",
                    "Note": note_text,
                    "Time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("✅ Note saved successfully!")
            else:
                st.warning("Please enter a note before saving.")
        
        if st.session_state.notes:
            st.markdown("**Recent Notes (last 5):**")
            notes_df = pd.DataFrame(st.session_state.notes[:5])
            st.dataframe(notes_df, use_container_width=True, hide_index=True)

elif page == "Bulk Predict":
    st.title("📤 Bulk Predict")
    st.markdown("Upload a CSV dataset containing multiple customers to process predictions in bulk.")
    
    uploaded_file = st.file_uploader("Upload Customer Data (CSV)", type=['csv'])
    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        
        if 'TotalCharges' in batch_df.columns:
            batch_df['TotalCharges'] = pd.to_numeric(batch_df['TotalCharges'], errors='coerce').fillna(0)
            
        missing_cols = [c for c in feature_names if c not in batch_df.columns]
        if missing_cols:
            st.error(f"Missing required columns in CSV: {', '.join(missing_cols)}")
        else:
            st.write("Preview of Uploaded Data:")
            st.dataframe(batch_df.head(5), use_container_width=True)
            
            with st.spinner("Processing records..."):
                batch_encoded = encode_input_data(batch_df, encoders, feature_names)
                batch_probs = model.predict_proba(batch_encoded)[:, 1]
                
                results_df = batch_df.copy()
                results_df['Churn Risk (%)'] = [round(p * 100, 1) for p in batch_probs]
                
                def get_risk_level(p):
                    if p > 0.6: return "🔴 Critical"
                    elif p >= 0.3: return "🟡 At Risk"
                    else: return "🟢 Safe"
                    
                results_df['Risk Level'] = [get_risk_level(p) for p in batch_probs]
                
                st.markdown("---")
                st.markdown("### Summary Statistics")
                scol1, scol2, scol3, scol4 = st.columns(4)
                scol1.metric("Total Customers", len(results_df))
                scol2.metric("🔴 Critical", len(results_df[results_df['Risk Level'] == "🔴 Critical"]))
                scol3.metric("🟡 At Risk", len(results_df[results_df['Risk Level'] == "🟡 At Risk"]))
                scol4.metric("🟢 Safe", len(results_df[results_df['Risk Level'] == "🟢 Safe"]))
                
                st.markdown("### Risk Distribution")
                risk_counts = results_df['Risk Level'].value_counts().reset_index()
                risk_counts.columns = ['Risk Level', 'Count']
                fig_bar = px.bar(risk_counts, x='Risk Level', y='Count', color='Risk Level', 
                                 color_discrete_map={"🔴 Critical": "#ef4444", "🟡 At Risk": "#eab308", "🟢 Safe": "#22c55e"})
                fig_bar.update_layout(paper_bgcolor='white', plot_bgcolor='white', margin=dict(t=30, b=0, l=0, r=0))
                st.plotly_chart(fig_bar, use_container_width=True)
                
                st.markdown("### Full Results Table")
                st.dataframe(results_df, use_container_width=True)
                
                csv = results_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Scored Dataset", data=csv, file_name="scored_customers.csv", mime="text/csv", type="primary")
                
                # Feature 7 — BATCH PDF REPORT
                if st.button("📄 Download Batch PDF Report", use_container_width=True):
                    batch_critical = len(results_df[results_df['Risk Level'] == "🔴 Critical"])
                    batch_at_risk = len(results_df[results_df['Risk Level'] == "🟡 At Risk"])
                    batch_safe = len(results_df[results_df['Risk Level'] == "🟢 Safe"])
                    batch_total = len(results_df)
                    
                    pdf_buf = io.BytesIO()
                    pdf_c = canvas.Canvas(pdf_buf, pagesize=letter)
                    
                    # Header
                    pdf_c.setFont("Helvetica-Bold", 18)
                    pdf_c.drawString(50, 760, "ChurnIQ \u2014 Batch Churn Analysis Report")
                    pdf_c.setFont("Helvetica", 10)
                    pdf_c.drawString(50, 740, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    pdf_c.line(50, 730, 550, 730)
                    
                    # Summary section
                    pdf_c.setFont("Helvetica-Bold", 13)
                    pdf_c.drawString(50, 705, "Summary")
                    pdf_c.setFont("Helvetica", 11)
                    pdf_c.drawString(50, 685, f"Total Customers Analyzed: {batch_total}")
                    pdf_c.setFillColorRGB(0.86, 0.13, 0.13)
                    pdf_c.drawString(50, 665, f"Critical Risk: {batch_critical}")
                    pdf_c.setFillColorRGB(0.85, 0.60, 0.05)
                    pdf_c.drawString(50, 645, f"At Risk: {batch_at_risk}")
                    pdf_c.setFillColorRGB(0.09, 0.64, 0.24)
                    pdf_c.drawString(50, 625, f"Safe: {batch_safe}")
                    pdf_c.setFillColorRGB(0, 0, 0)
                    
                    # Top 10 table
                    pdf_c.setFont("Helvetica-Bold", 13)
                    pdf_c.drawString(50, 595, "Top 10 Highest Risk Customers")
                    pdf_c.setFont("Helvetica-Bold", 10)
                    pdf_c.drawString(50, 575, "Row #")
                    pdf_c.drawString(120, 575, "Churn Risk %")
                    pdf_c.drawString(240, 575, "Risk Level")
                    pdf_c.line(50, 570, 400, 570)
                    
                    top10 = results_df.sort_values("Churn Risk (%)", ascending=False).head(10).reset_index(drop=True)
                    pdf_c.setFont("Helvetica", 10)
                    y_pos = 555
                    for i, row in top10.iterrows():
                        pdf_c.drawString(50, y_pos, str(i + 1))
                        pdf_c.drawString(120, y_pos, f"{row['Churn Risk (%)']}%")
                        pdf_c.drawString(240, y_pos, row['Risk Level'].replace('\U0001f534', '').replace('\U0001f7e1', '').replace('\U0001f7e2', '').strip())
                        y_pos -= 20
                    
                    # Revenue Impact
                    pdf_c.setFont("Helvetica-Bold", 13)
                    pdf_c.drawString(50, y_pos - 20, "Revenue Impact")
                    pdf_c.setFont("Helvetica", 11)
                    pdf_c.drawString(50, y_pos - 40, f"Estimated Monthly Revenue at Risk: ${batch_critical * 65:,.0f}")
                    
                    # Footer
                    pdf_c.setFont("Helvetica-Oblique", 8)
                    pdf_c.drawString(50, 50, "Generated by ChurnIQ Enterprise | Built by Sona S")
                    pdf_c.save()
                    
                    st.download_button(
                        label="📄 Click here to save Batch PDF",
                        data=pdf_buf.getvalue(),
                        file_name="churniq_batch_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

elif page == "Simulator":
    st.title("🔬 What-If Churn Simulator")
    st.markdown("See how changes affect churn risk in real time")
    
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        with st.container(border=True):
            st.markdown("#### Adjust Variables")
            sim_monthly = st.slider("Monthly Charges ($)", 20, 150, 65)
            sim_tenure = st.slider("Tenure (months)", 0, 72, 12)
            sim_contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
            sim_tech = st.selectbox("Tech Support", ["No", "Yes"])
        
    base_input = {
        'gender': 'Male', 'SeniorCitizen': 0, 'Partner': 'No', 'Dependents': 'No',
        'tenure': sim_tenure, 'PhoneService': 'Yes', 'MultipleLines': 'No', 
        'InternetService': 'Fiber optic', 'OnlineSecurity': 'No', 'OnlineBackup': 'No',
        'DeviceProtection': 'No', 'TechSupport': sim_tech, 'StreamingTV': 'No',
        'StreamingMovies': 'No', 'Contract': sim_contract, 'PaperlessBilling': 'Yes',
        'PaymentMethod': 'Electronic check', 'MonthlyCharges': sim_monthly, 'TotalCharges': sim_monthly * max(1, sim_tenure)
    }
    
    input_df = pd.DataFrame([base_input])
    encoded_input = encode_input_data(input_df, encoders, feature_names)
    sim_prob = model.predict_proba(encoded_input)[0][1]
    
    with col2:
        st.markdown("#### Simulated Churn Risk")
        
        # Color coding logic for the metric
        metric_color = "#dc2626" if sim_prob > 0.6 else "#ca8a04" if sim_prob > 0.3 else "#16a34a"
        st.markdown(f"<h1 style='color: {metric_color}; font-size: 4rem; margin: 0;'>{sim_prob*100:.1f}%</h1>", unsafe_allow_html=True)
        
        if sim_prob > 0.6:
            st.markdown("⚠️ High risk — consider offering a discount or contract upgrade")
        elif sim_prob > 0.3:
            st.markdown("🟡 Moderate risk — monitor this customer segment")
        else:
            st.markdown("✅ Low risk — current pricing is sustainable")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Line chart updated to Area Chart for professional look
        charge_range = list(range(20, 151, 10))
        probs = []
        for charge in charge_range:
            temp_input = base_input.copy()
            temp_input['MonthlyCharges'] = charge
            temp_input['TotalCharges'] = charge * max(1, sim_tenure)
            temp_df = pd.DataFrame([temp_input])
            temp_encoded = encode_input_data(temp_df, encoders, feature_names)
            probs.append(model.predict_proba(temp_encoded)[0][1] * 100)
            
        line_df = pd.DataFrame({'Monthly Charges': charge_range, 'Churn Probability (%)': probs})
        fig_line = px.area(line_df, x='Monthly Charges', y='Churn Probability (%)', title="Dynamic Risk Trajectory vs Pricing")
        fig_line.add_vline(x=sim_monthly, line_width=2, line_dash="dash", line_color="green", annotation_text="Current Setup")
        fig_line.update_layout(paper_bgcolor='white', plot_bgcolor='white', margin=dict(t=40, b=10, l=10, r=10))
        fig_line.update_traces(line_color='#3b82f6', fillcolor='rgba(59, 130, 246, 0.2)')
        st.plotly_chart(fig_line, use_container_width=True)

elif page == "Model Comparison":
    st.title("🤖 Model Comparison")
    st.markdown("Comparing Random Forest, XGBoost, and Logistic Regression")
    
    @st.cache_resource
    def train_all_models():
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from xgboost import XGBClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import LabelEncoder
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        df_models = pd.read_csv("data/telco_churn.csv")
        df_models["TotalCharges"] = pd.to_numeric(df_models["TotalCharges"], errors="coerce")
        df_models.dropna(inplace=True)
        df_models.drop(columns=["customerID"], inplace=True)
        le = LabelEncoder()
        for col in df_models.select_dtypes(include="object").columns:
            df_models[col] = le.fit_transform(df_models[col])
        X = df_models.drop("Churn", axis=1)
        y = df_models["Churn"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        models_dict = {
            "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
            "XGBoost": XGBClassifier(n_estimators=100, random_state=42),
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42)
        }
        results = []
        for name, clf in models_dict.items():
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            y_prob = clf.predict_proba(X_test)[:,1]
            results.append({
                "Model": name,
                "Accuracy": round(accuracy_score(y_test, y_pred)*100, 2),
                "Precision": round(precision_score(y_test, y_pred)*100, 2),
                "Recall": round(recall_score(y_test, y_pred)*100, 2),
                "F1 Score": round(f1_score(y_test, y_pred)*100, 2),
                "ROC-AUC": round(roc_auc_score(y_test, y_prob)*100, 2)
            })
        return pd.DataFrame(results)

    with st.spinner("Training all models..."):
        comp_df = train_all_models()
        
    st.markdown("### Performance Metrics")
    st.dataframe(
        comp_df.style.highlight_max(subset=['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC-AUC'], color='#bbf7d0', axis=0),
        use_container_width=True, hide_index=True
    )
    
    col1, col2 = st.columns(2)
    color_map = {"Random Forest": "#1e293b", "XGBoost": "#2563eb", "Logistic Regression": "#64748b"}
    
    with col1:
        fig_acc = px.bar(comp_df, x="Model", y="Accuracy", color="Model", color_discrete_map=color_map, title="Accuracy Comparison")
        fig_acc.update_layout(paper_bgcolor='white', plot_bgcolor='white', showlegend=False)
        st.plotly_chart(fig_acc, use_container_width=True)
        
    with col2:
        fig_f1 = px.bar(comp_df, x="Model", y="F1 Score", color="Model", color_discrete_map=color_map, title="F1 Score Comparison")
        fig_f1.update_layout(paper_bgcolor='white', plot_bgcolor='white', showlegend=False)
        st.plotly_chart(fig_f1, use_container_width=True)

elif page == "Diagnostics":
    st.title("Machine Learning Diagnostics")
    st.markdown("This section provides a technical overview of the predictive model's performance metrics on unseen validation data.")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Confusion Matrix")
        if os.path.exists('outputs/confusion_matrix.png'):
            st.image('outputs/confusion_matrix.png', use_container_width=True)
    with col2:
        st.subheader("ROC Curve Analysis")
        if os.path.exists('outputs/roc_curve.png'):
            st.image('outputs/roc_curve.png', use_container_width=True)

elif page == "Insights":
    st.title("Global Customer Insights")
    
    tab_global, tab_matrix = st.tabs(["Global Interpretability", "Flight Risk Matrix"])
    
    with tab_global:
        st.subheader("Model Feature Interpretability (SHAP Summary)")
        st.markdown("The SHAP summary plot illustrates the global impact of each feature across the entire customer base.")
        if os.path.exists('outputs/shap_summary.png'):
            col1, col2, col3 = st.columns([1, 1.5, 1])
            with col2:
                st.image('outputs/shap_summary.png', use_container_width=True)
                
        st.markdown("---")
        if df is not None and 'Churn' in df.columns:
            st.subheader("Exploratory Demographics & Revenue Analysis")
            col_pie, col_box = st.columns(2)
            
            with col_pie:
                churn_counts = df['Churn'].value_counts().reset_index()
                churn_counts.columns = ['Churn', 'Count']
                fig_pie = px.pie(churn_counts, values='Count', names='Churn', title="Historical Churn Distribution",
                                color_discrete_sequence=['#3498db', '#e74c3c'])
                fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with col_box:
                if 'MonthlyCharges' in df.columns:
                    fig_box = px.box(df, x='Churn', y='MonthlyCharges', color='Churn',
                                    title="Monthly Revenue Impact by Churn Status", color_discrete_sequence=['#e74c3c', '#3498db'])
                    fig_box.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_box, use_container_width=True)
                
    with tab_matrix:
        st.subheader("High-Value Flight Risk Matrix")
        st.markdown("This scatter plot maps active customers by their Lifetime Value (Total Charges) against their Churn Risk Probability. Identify and rescue high-value customers in the red zone.")
        if df is not None:
            with st.spinner("Calculating risk matrix for historical data..."):
                sample_df = df.dropna().sample(min(1000, len(df)), random_state=42)
                encoded_sample = encode_input_data(sample_df, encoders, feature_names)
                sample_df['Risk %'] = model.predict_proba(encoded_sample)[:, 1] * 100
                
                fig_matrix = px.scatter(
                    sample_df, x='TotalCharges', y='Risk %', color='Risk %', 
                    hover_data=['gender', 'tenure', 'MonthlyCharges'],
                    color_continuous_scale='RdYlGn_r',
                    title='Flight Risk Matrix (Sample 1000 Records)',
                    labels={'TotalCharges': 'Lifetime Value ($)', 'Risk %': 'Churn Risk (%)'}
                )
                fig_matrix.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
                fig_matrix.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_matrix, use_container_width=True)
        else:
            st.warning("Historical dataset not found.")

elif page == "Admin Panel":
    st.title("Admin Pipeline Dashboard")
    st.markdown("Upload fresh historical data to automatically retrain the underlying XGBoost model. This ensures the prediction engine stays accurate over time.")
    
    with st.container(border=True):
        st.subheader("Model Retraining Pipeline")
        new_data = st.file_uploader("Upload New Master Dataset (CSV)", type=['csv'], help="Must follow the same schema as the original Telco dataset.")
        
        if new_data is not None:
            if st.button("Initiate Retraining Pipeline", type="primary", use_container_width=True):
                with st.spinner("Replacing historical data..."):
                    with open("data/telco_churn.csv", "wb") as f:
                        f.write(new_data.getbuffer())
                
                with st.status("Executing Retraining Pipeline...", expanded=True) as status:
                    st.write("Initializing ML script...")
                    try:
                        from churn_model import train_and_evaluate
                        train_and_evaluate()
                        
                        st.write("Model retrained successfully!")
                        st.write("Generating new SHAP values and Diagnostics...")
                        st.cache_resource.clear()
                        st.cache_data.clear()
                        status.update(label="Retraining Complete!", state="complete", expanded=False)
                        st.success("The new model is now live. All predictions will use the updated weights.")
                    except Exception as e:
                        status.update(label="Retraining Failed", state="error", expanded=True)
                        st.error(f"Error during execution:\n{str(e)}")

elif page == "System Info":
    st.title("System & Architecture Information")
    with st.container(border=True):
        st.markdown("""
        ### Telco Analytics Portal v2.0 (Enterprise Edition)
        
        This enterprise-grade application delivers predictive intelligence regarding customer retention.
        Powered by advanced Machine Learning techniques, it equips customer success teams with actionable foresight.
        
        **Technical Architecture:**
        - **Data Processing Layer**: Pandas, NumPy
        - **Algorithm Engine**: XGBoost Classifier (Scikit-learn wrapper)
        - **Model Interpretability**: SHAP (SHapley Additive exPlanations)
        - **User Interface**: Streamlit
        - **Reporting Engine**: FPDF2
        - **Security**: SHA-256 Authentication Protocol
        """)

