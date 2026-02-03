import streamlit as st

def show_login(conn):
    # 1. SET WIDE MODE DEFAULT
    st.set_page_config(
        page_title="Portal System",
        layout="centered",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔐 Login ke Sistem")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Masuk")
        
        if submit:
            try:
                # Auth menggunakan Supabase
                res = conn.client.auth.sign_in_with_password({"email": email, "password": password})
                if res.user:
                    st.session_state["authenticated"] = True
                    st.session_state["user_email"] = res.user.email
                    st.rerun()
            except Exception:
                st.error("Login Gagal: Pastikan email dan password benar.")
