import streamlit as st
from st_supabase_connection import SupabaseConnection
from login import show_login
from upload_data import show_upload_dashboard
from process_data import show_run_procedure
from report_rekonsiliasi_transaksi_deposit_dan_settlement import show_report_deposit_settlement
from report_rekonsiliasi_transaksi_disbursement_dan_saldo_durian import show_report_disbursement_durian
from report_detail_reversal import show_report_detail_reversal
from report_balance_flow import show_report_balance_flow

# 1. SET WIDE MODE DEFAULT
st.set_page_config(
    page_title="Portal System", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 3. KONEKSI & INISIALISASI SESSION
conn = st.connection("supabase", type=SupabaseConnection)

if "authenticated" not in st.session_state:
    try:
        # Mencoba mengambil sesi yang tersimpan di browser
        session = conn.client.auth.get_session()
        if session:
            st.session_state["authenticated"] = True
            st.session_state["user_email"] = session.user.email
        else:
            st.session_state["authenticated"] = False
    except:
        st.session_state["authenticated"] = False

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "menu"

# --- LOGIKA NAVIGASI ---
if not st.session_state["authenticated"]:
    show_login(conn)
else:
    # SIDEBAR (Navigasi Samping)
    with st.sidebar:
        st.title("Informasi Akun")
        st.write(f"Logged in as:\n{st.session_state.get('user_email', 'User')}")
        st.divider()
        if st.button("🏠 Home Menu", key="side_home", use_container_width=True):
            st.session_state["current_page"] = "menu"
            st.rerun()
        if st.button("🚪 Logout", key="side_logout", use_container_width=True):
            conn.client.auth.sign_out()
            st.session_state["authenticated"] = False
            st.rerun()

    # KONTEN UTAMA
    if st.session_state["current_page"] == "menu":
        st.title("Data")
        st.write("Harap upload dan proses data terlebih dahulu sebelum menarik report!")
        st.divider()
        
        # Grid Menu menggunakan tombol standar Streamlit
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤\n\n\n\nUpload Data", key="btn_upload", use_container_width=True):
                st.session_state["current_page"] = "upload"
                st.rerun()
        
        with col2: # Misalnya kotak kedua
            if st.button("⚙️\n\n\n\nProcess Data", key="card_proc", use_container_width=True):
                st.session_state["current_page"] = "procedure"
                st.rerun()
        
        st.title("Report")
        st.write("Silakan pilih report yang ingin Anda akses:")
        st.divider()
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("📊\n\n\n\nReport Rekonsiliasi Transaksi Deposit dan Settlement", key="r1", use_container_width=True):
                st.session_state["current_page"] = "report_rekonsiliasi_transaksi_deposit_dan_settlement"
                st.rerun()
            
        with col4:
            if st.button("📊\n\n\n\nRekonsiliasi Transaksi Disbursement dan Saldo Durian", key="r2", use_container_width=True):
                st.session_state["current_page"] = "report_rekonsiliasi_transaksi_disbursement_dan_saldo_durian"
                st.rerun()

        with col3:
            if st.button("📊\n\n\n\nReport Detail Reversal", key="r3", use_container_width=True):
                st.session_state["current_page"] = "report_detail_reversal"
                st.rerun()
                
        with col4:
            if st.button("📊\n\n\n\nReport Balance Flow", key="r4", use_container_width=True):
                st.session_state["current_page"] = "report_balance_flow"
                st.rerun()

    elif st.session_state["current_page"] == "upload":
        # Menampilkan halaman upload dari file upload_data.py
        show_upload_dashboard(conn)
        
    elif st.session_state["current_page"] == "procedure":
        show_run_procedure(conn)

    elif st.session_state["current_page"] == "report_rekonsiliasi_transaksi_deposit_dan_settlement":
        show_report_deposit_settlement(conn)

    elif st.session_state["current_page"] == "report_rekonsiliasi_transaksi_disbursement_dan_saldo_durian":
        show_report_disbursement_durian(conn)

    elif st.session_state["current_page"] == "report_detail_reversal":
        show_report_detail_reversal(conn)

    elif st.session_state["current_page"] == "report_balance_flow":
        show_report_balance_flow(conn)
