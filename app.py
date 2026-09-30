import re
import streamlit as st

st.set_page_config(page_title="Rekap Jadwal & Tarif", page_icon="📅", layout="wide")

st.title("📅 Aplikasi Rekap Jadwal & Tarif Sesi")
st.write("Tempelkan data jadwal harian Anda di bawah ini untuk mendapatkan rincian dan total pendapatan secara instan.")

# Input Teks
user_input = st.text_area(
    "Masukkan Data Jadwal:",
    height=300,
    placeholder="Contoh:\nTgl 1 sept 26\[nama], [nama], [nama], [nama]\n[nama], [nama]\n\nTgl 2 Sept 26\n[nama]"
)

def parse_schedule(text):
    lines = text.strip().split('\n')
    data = {}
    current_date = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Cek apakah baris merupakan tanggal
        if re.match(r'^(tgl|tanggal)\b', line, re.IGNORECASE):
            current_date = line
            if current_date not in data:
                data[current_date] = []
        elif current_date:
            # Hitung jumlah peserta berdasarkan koma
            names = [name.strip() for name in line.split(',') if name.strip()]
            if names:
                data[current_date].append(names)
                
    return data

if st.button("Proses Review", type="primary"):
    if not user_input.strip():
        st.warning("Silakan masukkan data jadwal terlebih dahulu.")
    else:
        parsed_data = parse_schedule(user_input)
        
        private_dates = {}
        non_private_dates = {}
        
        total_private_sessions = 0
        total_non_private_sessions = 0
        
        for date, sessions in parsed_data.items():
            for names in sessions:
                count = len(names)
                names_str = ", ".join(names)
                
                if count <= 2:
                    total_private_sessions += 1
                    if date not in private_dates:
                        private_dates[date] = []
                    private_dates[date].append(names_str)
                else:
                    total_non_private_sessions += 1
                    if date not in non_private_dates:
                        non_private_dates[date] = []
                    non_private_dates[date].append(names_str)

        st.markdown("---")
        
        # --- 1. Daftar Tanggal Sesi Private ---
        st.subheader("Daftar Tanggal Sesi Private")
        if private_dates:
            for date, groups in private_dates.items():
                st.markdown(f"- **{date}**: {' | '.join(groups)}")
        else:
            st.write("Tidak ada sesi Private.")

        # --- 2. Daftar Tanggal Sesi Non-Private ---
        st.subheader("Daftar Tanggal Sesi Non-Private")
        if non_private_dates:
            for date, groups in non_private_dates.items():
                st.markdown(f"- **{date}**: {' | '.join(groups)}")
        else:
            st.write("Tidak ada sesi Non-Private.")

        st.markdown("---")
        
        # --- 3. Rincian Per Tanggal ---
        st.subheader("Rincian Per Tanggal (Detail Sesi & Nama)")
        
        for date, sessions in parsed_data.items():
            st.markdown(f"#### **{date}**")
            
            priv_sessions = [s for s in sessions if len(s) <= 2]
            non_priv_sessions = [s for s in sessions if len(s) > 2]
            
            # Private Detail
            if priv_sessions:
                total_priv_students = sum(len(s) for s in priv_sessions)
                st.markdown(f"* **Private** ({len(priv_sessions)} sesi, {total_priv_students} murid):")
                if len(priv_sessions) == 1:
                    st.markdown(f"  * {', '.join(priv_sessions[0])}")
                else:
                    for idx, s in enumerate(priv_sessions, 1):
                        st.markdown(f"  * Sesi {idx}: {', '.join(s)}")
            else:
                st.markdown("* **Private**: Tidak ada")
                
            # Non-Private Detail
            if non_priv_sessions:
                total_non_priv_students = sum(len(s) for s in non_priv_sessions)
                st.markdown(f"* **Non-Private** ({len(non_priv_sessions)} sesi, {total_non_priv_students} murid):")
                if len(non_priv_sessions) == 1:
                    st.markdown(f"  * {', '.join(non_priv_sessions[0])}")
                else:
                    for idx, s in enumerate(non_priv_sessions, 1):
                        st.markdown(f"  * Sesi {idx}: {', '.join(s)}")
            else:
                st.markdown("* **Non-Private**: Tidak ada")
                
            daily_total = (len(priv_sessions) * 100000) + (len(non_priv_sessions) * 120000)
            st.markdown(f"* **Total Pendapatan**: Rp {daily_total:,.0f}".replace(",", "."))
            st.write("")

        st.markdown("---")
        
        # --- 4. Rekap Total Pendapatan Akhir ---
        st.subheader("Rekap Total Pendapatan Akhir")
        
        tot_priv_income = total_private_sessions * 100000
        tot_non_priv_income = total_non_private_sessions * 120000
        grand_total = tot_priv_income + tot_non_priv_income
        
        st.write(f"* **Total Sesi Private**: {total_private_sessions} sesi × Rp 100.000 = **Rp {tot_priv_income:,.0f}**".replace(",", "."))
        st.write(f"* **Total Sesi Non-Private**: {total_non_private_sessions} sesi × Rp 120.000 = **Rp {tot_non_priv_income:,.0f}**".replace(",", "."))
        st.markdown(f"### **Total Keseluruhan Pendapatan: Rp {grand_total:,.0f}**".replace(",", "."))
