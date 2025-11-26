import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

# ===========================
# STREAMLIT UI
# ===========================
st.title("Visualisasi Medan Potensial - Kontur & Heatmap")
st.write("Upload file CSV berisi kolom X, Y, Value")

# Upload CSV
file = st.file_uploader("Upload CSV", type=["csv"])

if file is not None:
    # Membaca CSV
    data = pd.read_csv(file)
    st.subheader("Data Asli")
    st.dataframe(data.head())

    # Pastikan kolom benar
    if {'X', 'Y', 'Value'}.issubset(data.columns):
        
        # Konversi ke numpy array
        x = data['X'].values
        y = data['Y'].values
        z = data['Value'].values

        # Membuat grid interpolasi
        grid_x, grid_y = np.mgrid[min(x):max(x):200j, min(y):max(y):200j]
        grid_z = griddata((x, y), z, (grid_x, grid_y), method='cubic')

        # =======================
        # Plot Kontur
        # =======================
        st.subheader("Peta Kontur Anomali")
        fig1, ax1 = plt.subplots()
        kontur = ax1.contourf(grid_x, grid_y, grid_z, 20)
        plt.scatter(x, y, c='k', s=10, label="Titik Data")
        plt.colorbar(kontur, ax=ax1, label="Nilai Anomali")
        plt.legend()
        st.pyplot(fig1)

        # =======================
        # Plot Heatmap
        # =======================
        st.subheader("Peta Heatmap Anomali")
        fig2, ax2 = plt.subplots()
        heat = ax2.imshow(grid_z.T, extent=(min(x), max(x), min(y), max(y)),
                          origin='lower', aspect='auto')
        plt.colorbar(heat, ax=ax2, label="Nilai Anomali")
        st.pyplot(fig2)

    else:
        st.error("CSV harus memiliki kolom: X, Y, Value")
