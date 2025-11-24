import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

st.title("Visualisasi Medan Potensial (Grid Interpolation & Peta Anomali)")

# --- Upload CSV ---
uploaded_file = st.file_uploader("Upload file CSV (X, Y, Nilai)", type=["csv"])

if uploaded_file is not None:
    # Baca CSV
    data = pd.read_csv(uploaded_file)

    st.subheader("Data Asli")
    st.write(data.head())

    # Pastikan kolom benar
    required_cols = ['X', 'Y', 'Nilai']
    if not all(col in data.columns for col in required_cols):
        st.error("CSV harus memiliki kolom: X, Y, Nilai")
        st.stop()

    # Ambil data
    X = data['X'].values
    Y = data['Y'].values
    Z = data['Nilai'].values

    # --- Membuat grid ---
    grid_x, grid_y = np.mgrid[min(X):max(X):200j, min(Y):max(Y):200j]

    # --- Interpolasi ---
    grid_z = griddata((X, Y), Z, (grid_x, grid_y), method='cubic')

    st.subheader("Peta Kontur Anomali")
    fig1, ax1 = plt.subplots(figsize=(7, 6))
    contour = ax1.contourf(grid_x, grid_y, grid_z, levels=20)
    plt.colorbar(contour, ax=ax1, label="Nilai")
    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")
    ax1.set_title("Kontur Anomali (Interpolasi Grid)")
    st.pyplot(fig1)

    st.subheader("Heatmap Anomali")
    fig2, ax2 = plt.subplots(figsize=(7, 6))
    heat = ax2.imshow(grid_z.T, extent=[min(X), max(X), min(Y), max(Y)], origin='lower', aspect='auto')
    plt.colorbar(heat, ax=ax2, label="Nilai")
    ax2.set_xlabel("X")
    ax2.set_ylabel("Y")
    ax2.set_title("Heatmap Anomali (Interpolasi Grid)")
    st.pyplot(fig2)

    st.success("Visualisasi selesai!")


else:
    st.info("Silakan upload file CSV untuk memulai.")
