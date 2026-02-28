import streamlit as st
import pandas as pd
import numpy as np

def show_upload_dashboard(conn):

    st.title("📤 Upload Data")
    st.write("Pilih tabel tujuan untuk penyimpanan data dan excel sebagai sumber data.")
    st.divider()

    table_display_names = {
        "deposit": "Data Deposit",
        "disbursement": "Data Disbursement",
        "saldo_durian": "Data Saldo Durian",
        "settlement": "Data Settlement"
    }

    # Ambil daftar tabel
    try:
        mapping_data = conn.client.schema("verixa").table("v_table_list").select("*").in_("table_name", allowed_tables).execute()
        mapping_df = pd.DataFrame(mapping_data.data)
        list_tabel = mapping_df['table_name'].tolist()
    except Exception as e:
        st.error(f"Gagal memuat mapping tabel: {e}")
        list_tabel = []

    target_table = st.selectbox(
        "Pilih Tabel Tujuan:", 
        list_tabel,
        format_func=lambda x: table_display_names.get(x, x)
    )
    
    uploaded_file = st.file_uploader("Pilih file Excel (.xlsx)", type=["xlsx"])

    if uploaded_file and target_table:
        try:
            df = pd.read_excel(uploaded_file)
            # Normalisasi kolom: kecilkan huruf, ganti spasi & petik dengan _
            df.columns = [str(col).strip().lower().replace(' ', '_').replace("'", "_") for col in df.columns]
            
            st.subheader(f"Total: {len(df)} baris")
            st.dataframe(df.head(10), use_container_width=True)
            
            if st.button("Proses Upload"):
                def clean_json_data(obj):
                    if isinstance(obj, list): return [clean_json_data(item) for item in obj]
                    elif isinstance(obj, dict): return {k: clean_json_data(v) for k, v in obj.items()}
                    elif isinstance(obj, float):
                        if np.isnan(obj) or np.isinf(obj): return None
                    elif hasattr(obj, 'isoformat'): return obj.isoformat()
                    return obj

                cleaned_data = clean_json_data(df.to_dict(orient='records'))
                
                with st.spinner('Mengunggah...'):
                    try:
                        conn.client.schema("verixa").table(target_table).insert(cleaned_data).execute()
                        st.success("Berhasil diunggah!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error saat upload: {e}")
        except Exception as e:
            st.error(f"File rusak atau tidak terbaca: {e}")









