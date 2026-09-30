import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Rekap Jadwal & Tarif", page_icon="📅", layout="wide")

st.title("📅 Aplikasi Rekap Jadwal & Tarif Sesi")
st.write("Tempelkan data jadwal harian Anda di bawah ini untuk mendapatkan rincian dan total pendapatan secara instan.")

# Input Teks
user_input = st.text_area(
    "Masukkan Data Jadwal:",
    height=300,
    placeholder="Contoh:\nTgl 1 sept 26\nRachel, lusi, cing2, agatha (ding2)\nKen, kimmy\n\nTotal\n23 x 120rb = 2.760.000\nTotal = 4.260.000"
)

def parse_schedule(text):
    lines = text.strip().split('\n')
    data = {}
    current_date = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 1. Cek apakah baris merupakan tanggal
        if re.match(r'^(tgl|tanggal)\b', line, re.IGNORECASE):
            current_date = line
            if current_date not in data:
                data[current_date] = []
        
        # 2. Cek dan Abaikan teks ringkasan/total di akhir data
        elif re.match(r'^(total|\d+\s*x|rp\b)', line, re.IGNORECASE) or '=' in line:
            # Menghentikan pencatatan sesi untuk baris ringkasan total manual
            current_date = None
            continue
            
        # 3. Ambil data nama peserta jika sedang berada di bawah tanggal tertentu
        elif current_date:
            names = [name.strip() for name in line.split(',') if name.strip()]
            if names:
                data[current_date].append(names)
                
    return data

if st.button("Proses Review", type="primary"):
    if not user_input.strip():
        st.warning("Silakan masukkan data jadwal terlebih dahulu.")
    else:
        parsed_data = parse_schedule(user_input)
        
        table_rows = []
        total_priv_all = 0
        total_non_priv_all = 0
        
        for date, sessions in parsed_data.items():
            priv_count = sum(1 for s in sessions if len(s) <= 2)
            non_priv_count = sum(1 for s in sessions if len(s) > 2)
            
            daily_total = (priv_count * 100000) + (non_priv_count * 120000)
            
            total_priv_all += priv_count
            total_non_priv_all += non_priv_count
            
            table_rows.append({
                "Tanggal": date,
                "Sesi Private": f"{priv_count} sesi",
                "Sesi Non-Private": f"{non_priv_count} sesi",
                "Total Pendapatan Harian": f"Rp {daily_total:,.0f}".replace(",", ".")
            })

        st.markdown("---")
        
        # --- 1. Ringkasan Tabel ---
        st.subheader("📊 Ringkasan Rekapitulasi")
        
        if table_rows:
            df = pd.DataFrame(table_rows)
            
            grand_total_income = (total_priv_all * 100000) + (total_non_priv_all * 120000)
            
            total_row = pd.DataFrame([{
                "Tanggal": "TOTAL KESELURUHAN",
                "Sesi Private": f"{total_priv_all} sesi (Rp {total_priv_all * 100000:,.0f})".replace(",", "."),
                "Sesi Non-Private": f"{total_non_priv_all} sesi (Rp {total_non_priv_all * 120000:,.0f})".replace(",", "."),
                "Total Pendapatan Harian": f"Rp {grand_total_income:,.0f}".replace(",", ".")
            }])
            
            df_final = pd.concat([df, total_row], ignore_index=True)
            st.dataframe(df_final, use_container_width=True, hide_index=True)

            st.markdown("---")
            
            # --- 2. Rincian Per Tanggal ---
            st.subheader("📝 Detail Peserta Per Tanggal")
            
            for date, sessions in parsed_data.items():
                st.markdown(f"#### **{date}**")
                
                priv_sessions = [s for s in sessions if len(s) <= 2]
                non_priv_sessions = [s for s in sessions if len(s) > 2]
                
                if priv_sessions:
                    st.markdown(f"* **Private** ({len(priv_sessions)} sesi):")
                    for idx, s in enumerate(priv_sessions, 1):
                        st.markdown(f"  * Sesi {idx}: {', '.join(s)}")
                else:
                    st.markdown("* **Private**: Tidak ada")
                    
                if non_priv_sessions:
                    st.markdown(f"* **Non-Private** ({len(non_priv_sessions)} sesi):")
                    for idx, s in enumerate(non_priv_sessions, 1):
                        st.markdown(f"  * Sesi {idx}: {', '.join(s)}")
                else:
                    st.markdown("* **Non-Private**: Tidak ada")
                    
                st.write("")
        else:
            st.error("Format data tidak terdeteksi. Pastikan ada penulisan tanggal seperti 'Tgl ...'")
