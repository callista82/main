import streamlit as st
import pandas as pd
import datetime
import os
import altair as alt

# ===============================
# 1. LOAD / CREATE DATABASE CSV
# ===============================
FILE = "time_log.csv"

if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["Project", "Start_Time", "End_Time", "Duration_hours"])
    df.to_csv(FILE, index=False)

st.title("Aplikasi Logbook Pencatat Waktu Proyek & Analisis Efisiensi")

# ===============================
# 2. INPUT FORM PENGISIAN DATA
# ===============================
st.subheader("Input Waktu Aktivitas")

project_name = st.text_input("Nama Proyek / Aktivitas")
start_time = st.time_input("Waktu Mulai", datetime.datetime.now().time())
end_time = st.time_input("Waktu Selesai", datetime.datetime.now().time())

# Hitung durasi otomatis
start_dt = datetime.datetime.combine(datetime.date.today(), start_time)
end_dt = datetime.datetime.combine(datetime.date.today(), end_time)
duration_hours = (end_dt - start_dt).total_seconds() / 3600

if st.button("Simpan Data"):
    if project_name.strip() != "":
        new_data = pd.DataFrame([[project_name, start_time, end_time, duration_hours]],
                                columns=["Project", "Start_Time", "End_Time", "Duration_hours"])
        
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(FILE, index=False)
        st.success(f"Data berhasil disimpan! Durasi = {duration_hours:.2f} jam")
    else:
        st.warning("Nama proyek harus diisi.")

# ===============================
# 3. TAMPILKAN DATA
# ===============================
st.subheader(" Database Waktu")
st.dataframe(df)

# ===============================
# 4. VISUALISASI
# ===============================

df["Date"] = pd.to_datetime(df["Start_Time"], errors='coerce')  # convert jika diperlukan

st.subheader("Grafik Durasi Per Proyek")
chart_project = alt.Chart(df).mark_bar().encode(
    x="Project",
    y="Duration_hours",
    tooltip=["Project", "Duration_hours"]
)
st.altair_chart(chart_project, use_container_width=True)

st.subheader("Tren Waktu (Hari / Urutan Input)")
chart_trend = alt.Chart(df.reset_index()).mark_line(point=True).encode(
    x="index",
    y="Duration_hours",
    tooltip=["Project", "Duration_hours"]
)
st.altair_chart(chart_trend, use_container_width=True)
