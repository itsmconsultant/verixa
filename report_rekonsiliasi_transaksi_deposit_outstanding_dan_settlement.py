import streamlit as st
import pandas as pd
import datetime
import io

def show_report_deposit_settlement_outstanding(conn):
    st.title("📊 Rekonsiliasi Transaksi Deposit dan Settlement")
    st.divider()

    # --- 1. Input Parameter Tanggal ---
    col1, col2 = st.columns([1, 1])
    with col1:
        # Default ke tanggal hari ini jika belum ada di session state
        default_date = st.session_state.get('last_date', datetime.date.today())
        selected_date = st.date_input("Pilih Tanggal:", default_date)
        st.session_state['last_date'] = selected_date
        tanggal_str = selected_date.strftime("%Y-%m-%d")

    # --- 2. Ambil Distinct Client ID berdasarkan Tanggal ---
    try:
        client_response = conn.client.schema("verixa").table("summary_deposit") \
            .select("client_id") \
            .eq("tanggal_data", tanggal_str) \
            .execute()
        
        if client_response.data:
            # Mengambil nilai unik dan menghapus None
            raw_clients = sorted(list({row['client_id'] for row in client_response.data if row['client_id']}))
            # Tambahkan opsi "Pilih Semua" di awal list
            available_clients = ["Pilih Semua"] + raw_clients
        else:
            available_clients = []
            
    except Exception as e:
        st.error(f"Gagal memuat daftar Client: {e}")
        available_clients = []

    # --- 3. Filter Client ID (UI Dinamis) ---
    with col2:
        if not available_clients:
            # Tampilan jika data kosong (Disabled sesuai permintaan)
            st.selectbox(
                "Pilih Client ID:", 
                options=["Tidak ada client"], 
                disabled=True,
                help="Tidak ada data transaksi ditemukan untuk tanggal ini."
            )
            selected_client = None
        else:
            # Tampilan jika data tersedia
            selected_client = st.selectbox(
                "Pilih Client ID:", 
                options=available_clients,
                index=0
            )

    # --- 4. Tombol Cari ---
    if st.button("Tampilkan Data", use_container_width=True):
        if not selected_client:
            st.warning("Data tidak tersedia untuk ditampilkan pada tanggal ini.")
            return

        with st.spinner(f"Mengambil data untuk {selected_client}..."):
            try:
                # Membangun query dasar
                query = conn.client.schema("verixa").table("summary_deposit_outstanding") \
                    .select("client_id, merchant, tanggal_data, keterangan, jumlah_transaksi, jumlah_transaksi_sesuai_rate, penambahan_rupiah, pengurangan_rupiah, rekonsiliasi_jumlah_transaksi, rekonsiliasi_rupiah, rekonsiliasi_tambah_kurang, saldo_rekonsiliasi_rupiah") \
                    .eq("tanggal_data", tanggal_str)

                # Jika user TIDAK memilih "Pilih Semua", tambahkan filter spesifik client_id
                if selected_client != "Pilih Semua":
                    query = query.eq("client_id", selected_client)

                # Eksekusi query dengan urutan
                response = query.order("client_id").order("urutan", desc=False).execute()

                if response.data:
                    df = pd.DataFrame(response.data)
                    st.success(f"Berhasil menemukan {len(df)} baris data.")
                    
                    # --- PROSES KONVERSI KE EXCEL ---
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Data_Rekon')
                    
                    download_data = buffer.getvalue()

                    # Nama file dinamis berdasarkan pilihan
                    file_suffix = "ALL" if selected_client == "Pilih Semua" else selected_client
                    st.download_button(
                        label="📥 Download Excel (.xlsx)",
                        data=download_data,
                        file_name=f"Rekonsiliasi Transaksi Deposit Outstanding dan Settlement {tanggal_str}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info(f"Tidak ada detail data untuk {selected_client} pada tanggal tersebut.")
                    
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses data: {e}")
