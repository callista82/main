import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

st.title("Aplikasi Pencatat Waktu Proyek")

CSV_FILE = "database_proyek.csv"

# -----------------------------------------------------------
# FUNGSI: Membuat file CSV jika belum ada
# -----------------------------------------------------------
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["Proyek", "WaktuMulai", "WaktuSelesai", "DurasiJam"])
    df_init.to_csv(CSV_FILE, index=False)

# -----------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------
df = pd.read_csv(CSV_FILE)

st.subheader(" Input Data Proyek")

# -----------------------------------------------------------
# FORM INPUT
# -----------------------------------------------------------
with st.form("input_form"):
    proyek = st.text_input("Nama Proyek / Aktivitas")
    waktu_mulai = st.datetime_input("Waktu Mulai")
    waktu_selesai = st.datetime_input("Waktu Selesai")

    submit = st.form_submit_button("Simpan Data")

# -----------------------------------------------------------
# PROSES PENYIMPANAN
# -----------------------------------------------------------
if submit:
    if proyek == "":
        st.error("Nama proyek tidak boleh kosong.")
    elif waktu_selesai <= waktu_mulai:
        st.error("Waktu selesai harus lebih besar dari waktu mulai.")
    else:
        durasi = (waktu_selesai - waktu_mulai).total_seconds() / 3600  # dalam jam

        new_data = pd.DataFrame({
            "Proyek": [proyek],
            "WaktuMulai": [waktu_mulai],
            "WaktuSelesai": [waktu_selesai],
            "DurasiJam": [durasi]
        })

        # tambahkan ke CSV
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

        st.success("Data berhasil disimpan!")

# -----------------------------------------------------------
# TAMPILKAN DATA
# -----------------------------------------------------------
st.subheader("📋 Data Aktivitas")
st.dataframe(df)

# -----------------------------------------------------------
# GRAFIK DURASI PER PROYEK
# -----------------------------------------------------------
st.subheader("📈 Grafik Durasi per Proyek")

if len(df) > 0:
    fig, ax = plt.subplots()
    df.groupby("Proyek")["DurasiJam"].sum().plot(kind="bar", ax=ax)
    ax.set_ylabel("Durasi (jam)")
    ax.set_title("Total Durasi per Proyek")
    st.pyplot(fig)
else:
    st.info("Belum ada data untuk ditampilkan.")

# -----------------------------------------------------------
# GRAFIK TREND WAKTU
# -----------------------------------------------------------
st.subheader("📉 Tren Waktu Penyelesaian")

if len(df) > 0:
    df_sorted = df.sort_values("WaktuMulai")

    fig2, ax2 = plt.subplots()
    ax2.plot(df_sorted["WaktuMulai"], df_sorted["DurasiJam"], marker="o")
    ax2.set_xlabel("Tanggal")
    ax2.set_ylabel("Durasi (jam)")
    ax2.set_title("Trend Durasi Aktivitas")
    plt.xticks(rotation=45)
    st.pyplot(fig2)
else:
    st.info("Belum ada data tren waktu.")
