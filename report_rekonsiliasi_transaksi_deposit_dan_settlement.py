import streamlit as st
import pandas as pd
import datetime
import io

def show_report_deposit_settlement(conn):
    st.title("📊 Rekonsiliasi Transaksi Deposit dan Settlement")
    st.divider()

    # --- 1. Filter Tanggal ---
    col1, col2 = st.columns([1, 1])
    with col1:
        default_date = st.session_state.get('last_date', datetime.date.today())
        selected_date = st.date_input("Pilih Tanggal:", default_date)
        st.session_state['last_date'] = selected_date
        tanggal_str = selected_date.strftime("%Y-%m-%d")

    # --- 2. Ambil Distinct Client ID berdasarkan Tanggal ---
    # Kita ambil daftar client yang tersedia hanya pada tanggal yang dipilih
    try:
        client_response = conn.client.schema("verixa").table("summary_deposit") \
            .select("client_id") \
            .eq("tanggal_data", tanggal_str) \
            .execute()
        
        # Ambil nilai unik dan urutkan
        if client_response.data:
            available_clients = sorted(list({row['client_id'] for row in client_response.data if row['client_id']}))
        else:
            available_clients = []
            
    except Exception as e:
        st.error(f"Gagal memuat daftar Client: {e}")
        available_clients = []

    # --- 3. Filter Client ID (Dropdown muncul jika ada data) ---
    with col2:
        if available_clients:
            selected_client = st.selectbox("Pilih Client ID:", available_clients)
        else:
            st.warning("Tidak ada client pada tanggal ini.")
            selected_client = None

    # --- 4. Tombol Cari ---
    if st.button("Tampilkan Data", use_container_width=True):
        if not selected_client:
            st.error("Silakan pilih Client ID terlebih dahulu.")
            return

        with st.spinner(f"Mengambil data {selected_client} untuk tanggal {tanggal_str}..."):
            try:
                # Menambahkan filter .eq("client_id", selected_client)
                response = conn.client.schema("verixa").table("summary_deposit") \
                    .select("merchant, tanggal_data, keterangan, jumlah_transaksi, jumlah_transaksi_sesuai_rate, penambahan_rupiah, pengurangan_rupiah, rekonsiliasi_jumlah_transaksi, rekonsiliasi_rupiah, rekonsiliasi_tambah_kurang, saldo_rekonsiliasi_rupiah") \
                    .eq("tanggal_data", tanggal_str) \
                    .eq("client_id", selected_client) \
                    .order("urutan", desc=False) \
                    .execute()

                if response.data:
                    df = pd.DataFrame(response.data)
                    st.success(f"Berhasil menemukan {len(df)} data untuk {selected_client}.")
                    
                    # --- PROSES KONVERSI KE EXCEL ---
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Sheet1')
                    
                    download_data = buffer.getvalue()

                    st.download_button(
                        label="📥 Download Excel (.xlsx)",
                        data=download_data,
                        file_name=f"Rekon_{selected_client}_{tanggal_str}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.warning(f"Data tidak ditemukan untuk Client {selected_client} pada tanggal {tanggal_str}.")
                    
            except Exception as e:
                st.error(f"Terjadi kesalahan saat mengambil data: {e}")
