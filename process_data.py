import streamlit as st
from sqlalchemy import text

def show_run_procedure(conn): # Tetap terima conn jika perlu, tapi kita buat koneksi baru di sini
    st.title("⚙️ Jalankan Proses Data")
    st.write("Pilih tanggal data yang mau di proses untuk menghasilkan report.")
    st.divider()
    
    selected_date = st.date_input("Pilih Tanggal Data:")
    
    if st.button("Proses Data"):
        # Streamlit akan otomatis mencari [connections.postgresql] di Secrets
        db_sql = st.connection("postgresql", type="sql")
        
        with st.spinner("Eksekusi Data..."):
            try:
                with db_sql.session as session:
                    # Menjalankan CALL secara eksplisit melalui SQLAlchemy
                    session.execute(
                        text("CALL verixa.run_all_procedure(:tgl)"),
                        {"tgl": selected_date.strftime("%Y-%m-%d")}
                    )
                    session.commit()
                st.success("Berhasil dijalankan!")
            except Exception as e:
                st.error(f"Error: {e}")
