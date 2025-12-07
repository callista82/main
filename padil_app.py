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
   roject", "Duration_hours"]
)
