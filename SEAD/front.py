# app.py (Updated Streamlit Frontend)
import streamlit as st
import requests
import re
import json
from datetime import datetime

# ---------- API FUNCTION ----------
def analyze_code(code):
    """Send code to backend for analysis"""
    url = "http://127.0.0.1:5000/analyze"
    
    try:
        response = requests.post(url, json={"code": code}, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Backend not running. Please start the Flask server."}
    except requests.exceptions.Timeout:
        return {"error": "Request timeout. Please try again."}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}


# ---------- VALIDATION FUNCTIONS ----------
def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

def is_valid_password(password):
    return len(password) >= 6

def is_valid_username(username):
    return len(username) >= 3 and username.isalnum()


# ---------- SESSION INITIALIZATION ----------
st.set_page_config(page_title="Ethical Software Checker", layout="wide", initial_sidebar_state="expanded")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "login"

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "username" not in st.session_state:
    st.session_state.username = None

if "users" not in st.session_state:
    st.session_state.users = {}

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

if "current_code" not in st.session_state:
    st.session_state.current_code = None


# ---------- NAVIGATION FUNCTIONS ----------
def go_to(page):
    st.session_state.page = page
    st.rerun()

def logout():
    st.session_state.user_email = None
    st.session_state.username = None
    st.session_state.analysis_results = None
    st.session_state.current_code = None
    go_to("login")


# ---------- HEADER COMPONENT ----------
def header():
    col1, col2 = st.columns([8, 2])
    with col1:
        st.markdown("## 🛡️ Ethical Software Checker")
    return col1, col2


# ---------- SIDEBAR COMPONENT ----------
def render_sidebar():
    if st.session_state.user_email:
        with st.sidebar:
            st.markdown("### 🧑‍💻 User Menu")
            st.markdown(f"**Welcome,**")
            st.markdown(f"**{st.session_state.username}**")
            st.markdown("---")
            
            # Navigation Menu
            selected = st.radio(
                "Navigation",
                ["📝 Submit Code", "🔒 Security Report", "🔐 Privacy Report", "⚖️ Ethical Report"],
                key="sidebar_navigation"
            )
            
            st.markdown("---")
            
            # Profile and Logout
            if st.button("👤 View Profile"):
                go_to("profile")
            
            if st.button("🚪 Logout"):
                logout()
            
            return selected
    return None


# ---------- LOGIN PAGE ----------
if st.session_state.page == "login":
    col1, col2 = header()
    
    with col2:
        if st.button("Sign Up", use_container_width=True):
            go_to("signup")
    
    st.markdown("### 🔐 Login to Your Account")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if not email or not password:
                st.error("❌ Please enter both Email and Password")
            elif not is_valid_email(email):
                st.error("❌ Please enter a valid email address")
            elif email not in st.session_state.users:
                st.error("❌ User not found. Please sign up first.")
            elif st.session_state.users[email]["password"] != password:
                st.error("❌ Incorrect password")
            else:
                st.session_state.user_email = email
                st.session_state.username = st.session_state.users[email]["username"]
                st.success("✅ Login successful! Redirecting...")
                go_to("dashboard")
    
    # Forgot password link
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Forgot Password?", use_container_width=True):
            go_to("forgot")


# ---------- SIGNUP PAGE ----------
elif st.session_state.page == "signup":
    col1, col2 = header()
    
    with col2:
        if st.button("Back to Login", use_container_width=True):
            go_to("login")
    
    st.markdown("### 📝 Create New Account")
    
    with st.form("signup_form"):
        username = st.text_input("Username", placeholder="Choose a username (min 3 characters)")
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Min 6 characters")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
        
        submitted = st.form_submit_button("Sign Up", use_container_width=True)
        
        if submitted:
            # Validation
            if not username or not email or not password or not confirm_password:
                st.error("❌ Please fill all fields")
            elif not is_valid_username(username):
                st.error("❌ Username must be at least 3 characters and contain only letters/numbers")
            elif not is_valid_email(email):
                st.error("❌ Please enter a valid email address")
            elif not is_valid_password(password):
                st.error("❌ Password must be at least 6 characters")
            elif email in st.session_state.users:
                st.error("❌ Email already registered. Please login instead.")
            elif password != confirm_password:
                st.error("❌ Passwords do not match!")
            else:
                # Create account
                st.session_state.users[email] = {
                    "username": username,
                    "password": password
                }
                st.success("✅ Account created successfully! Please login.")
                go_to("login")


# ---------- FORGOT PASSWORD PAGE ----------
elif st.session_state.page == "forgot":
    col1, col2 = header()
    
    with col2:
        if st.button("Back to Login", use_container_width=True):
            go_to("login")
    
    st.markdown("### 🔑 Reset Password")
    
    with st.form("forgot_form"):
        email = st.text_input("Enter your registered email", placeholder="your@email.com")
        
        submitted = st.form_submit_button("Send Reset Link", use_container_width=True)
        
        if submitted:
            if not email:
                st.error("❌ Please enter your email")
            elif not is_valid_email(email):
                st.error("❌ Please enter a valid email address")
            elif email not in st.session_state.users:
                st.error("❌ Email not found in our system")
            else:
                # In real implementation, this would send an actual email
                st.success("✅ Password reset link has been sent to your email (demo)")

        st.info("📧 For demo purposes, this will show a success message. In production, it would send a real email.")


# ---------- DASHBOARD PAGE ----------
elif st.session_state.page == "dashboard":
    # Header
    col1, col2 = header()
    
    with col2:
        if st.button("👤 Profile", use_container_width=True):
            go_to("profile")
    
    st.markdown("Upload or paste your code to analyze security, privacy, and ethical compliance.")
    st.markdown("---")
    
    # Render sidebar and get selected option
    selected_option = render_sidebar()
    
    # Main content based on sidebar selection
    if selected_option == "📝 Submit Code":
        st.markdown("### 📤 Submit Code for Analysis")
        
        # Code input methods
        input_method = st.radio("Choose input method:", ["Paste Code", "Upload File"], horizontal=True)
        
        code = ""
        
        if input_method == "Upload File":
            uploaded_file = st.file_uploader("Upload a code file", type=['py', 'txt', 'js', 'java', 'cpp', 'c'])
            if uploaded_file is not None:
                try:
                    code = uploaded_file.read().decode("utf-8")
                    st.success(f"✅ File '{uploaded_file.name}' loaded successfully!")
                    with st.expander("Preview uploaded code"):
                        st.code(code[:1000], language='python')
                        if len(code) > 1000:
                            st.info("Showing first 1000 characters...")
                except Exception as e:
                    st.error(f"Error reading file: {e}")
        
        else:  # Paste Code
            code = st.text_area("Paste your code here:", height=300, placeholder="def example_function():\n    print('Hello World')")
        
        # Analyze button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            analyze_button = st.button("🔍 Analyze Code", use_container_width=True, type="primary")
        
        if analyze_button:
            if not code.strip():
                st.error("❌ Please provide code either by uploading a file or pasting it")
            else:
                # Store current code for reference
                st.session_state.current_code = code
                
                # Show loading spinner
                with st.spinner("🔄 Analyzing code... This may take a few seconds"):
                    result = analyze_code(code)
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.session_state.analysis_results = result
                    st.success("✅ Analysis Complete!")
                    
                    # Show summary cards
                    st.markdown("### 📊 Analysis Summary")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    # Get scores if available
                    security_score = result.get('security', {}).get('report', {}).get('score', 0)
                    privacy_score = result.get('privacy', {}).get('report', {}).get('score', 0)
                    ethical_decision = result.get('ethical', {}).get('report', {}).get('decision', 'N/A')
                    
                    with col1:
                        score_color = "green" if security_score >= 70 else "orange" if security_score >= 50 else "red"
                        st.metric("🔒 Security Score", f"{security_score}/100", delta=None)
                    
                    with col2:
                        score_color = "green" if privacy_score >= 70 else "orange" if privacy_score >= 50 else "red"
                        st.metric("🔐 Privacy Score", f"{privacy_score}/100", delta=None)
                    
                    with col3:
                        decision_emoji = "✅" if ethical_decision == "APPROVE" else "⚠️" if ethical_decision == "REVIEW" else "❌"
                        st.metric("⚖️ Ethical Decision", f"{decision_emoji} {ethical_decision}", delta=None)
    
    elif selected_option == "🔒 Security Report":
        st.markdown("### 🔒 Detailed Security Analysis Report")
        
        if st.session_state.analysis_results and 'security' in st.session_state.analysis_results:
            security_data = st.session_state.analysis_results['security']
            
            # Display report
            if security_data.get('formatted_output'):
                st.text(security_data['formatted_output'])
            else:
                st.info("No security analysis has been performed yet. Please submit code for analysis.")
        else:
            st.info("No security report available. Please submit code for analysis first.")
    
    elif selected_option == "🔐 Privacy Report":
        st.markdown("### 🔐 Detailed Privacy Analysis Report")
        
        if st.session_state.analysis_results and 'privacy' in st.session_state.analysis_results:
            privacy_data = st.session_state.analysis_results['privacy']
            
            # Display report
            if privacy_data.get('formatted_output'):
                st.text(privacy_data['formatted_output'])
            else:
                st.info("No privacy analysis has been performed yet. Please submit code for analysis.")
        else:
            st.info("No privacy report available. Please submit code for analysis first.")
    
    elif selected_option == "⚖️ Ethical Report":
        st.markdown("### ⚖️ Ethical Decision Report")
        
        if st.session_state.analysis_results and 'ethical' in st.session_state.analysis_results:
            ethical_data = st.session_state.analysis_results['ethical']
            
            # Display report
            if ethical_data.get('formatted_output'):
                st.text(ethical_data['formatted_output'])
            
            # Show additional recommendations if available
            st.markdown("---")
            st.markdown("### 📋 Summary of Findings")
            
            # Get summary from security and privacy
            security_summary = st.session_state.analysis_results.get('security', {}).get('report', {}).get('summary', '')
            privacy_summary = st.session_state.analysis_results.get('privacy', {}).get('report', {}).get('summary', '')
            
            if security_summary:
                st.info(f"🔒 {security_summary}")
            if privacy_summary:
                st.info(f"🔐 {privacy_summary}")
        else:
            st.info("No ethical analysis available. Please submit code for analysis first.")
    
    # Add footer
    st.markdown("---")
    st.markdown("💡 **Tip:** The analysis checks for security vulnerabilities, privacy concerns, and makes an ethical decision based on predefined rules.")


# ---------- PROFILE PAGE ----------
elif st.session_state.page == "profile":
    col1, col2 = header()
    
    with col2:
        if st.button("← Back to Dashboard", use_container_width=True):
            go_to("dashboard")
    
    st.markdown("### 👤 User Profile")
    
    # Display profile information in cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📧 Account Information")
        st.write(f"**Username:** {st.session_state.username}")
        st.write(f"**Email:** {st.session_state.user_email}")
        st.write(f"**Member since:** {datetime.now().strftime('%B %d, %Y')}")
    
    with col2:
        st.markdown("#### 📊 Activity Summary")
        if st.session_state.analysis_results:
            st.write("✅ Code analysis performed")
            ethical_decision = st.session_state.analysis_results.get('ethical', {}).get('report', {}).get('decision', 'N/A')
            st.write(f"**Latest decision:** {ethical_decision}")
        else:
            st.write("No code analysis performed yet")
    
    st.markdown("---")
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True):
        logout()
    
    st.info("💡 Note: This is a demo profile. In production, you would have more features like password change, etc.")