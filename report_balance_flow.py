import streamlit as st
import pandas as pd
import datetime
import io

def show_report_balance_flow(conn):
    st.title("📊 Balance Flow")
    st.divider()

    # 1. Input Parameter Tanggal
    col1, col2 = st.columns([1, 2])
    with col1:
        # Default ke tanggal hari ini jika belum ada di session state
        default_date = st.session_state.get('last_date', datetime.date.today())
        selected_date = st.date_input("Pilih Tanggal:", default_date)
    
    st.session_state['last_date'] = selected_date

    # 2. Tombol Cari
    if st.button("Tampilkan Data", use_container_width=True):
        tanggal_str = selected_date.strftime("%Y-%m-%d")
        
        with st.spinner(f"Mengambil data untuk tanggal {tanggal_str}..."):
            try:
                # 3. Menggunakan API Select Supabase (Tanpa SQLAlchemy)
                # .table() merujuk ke nama tabel, .select("*") mengambil semua kolom
                response = conn.client.schema("verixa").table("summary_balance_flow") \
                    .select("keterangan,flag,tanggal_data,jumlah_transaksi,amount,rate_pt,saldo_di_pt,rate_vendor,saldo_di_vendor,profit_pt,balance,balance_settle") \
                    .eq("tanggal_data", tanggal_str) \
                    .order("urutan", desc=False) \
                    .execute()

                # 4. Menampilkan Hasil
                if response.data:
                    df = pd.DataFrame(response.data)
                    st.success(f"Berhasil menemukan {len(df)} data.")
                    
                    # --- PROSES KONVERSI KE EXCEL ---
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Sheet1')
                        # writer.save() # Tidak perlu di pandas versi terbaru
                    
                    download_data = buffer.getvalue()

                    # Tombol Download Excel
                    st.download_button(
                        label="📥 Download Excel (.xlsx)",
                        data=download_data,
                        file_name=f"Balance Flow {tanggal_str}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    # --------------------------------
                    
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.warning(f"Tidak ada data ditemukan untuk tanggal {tanggal_str}.")
                    
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
