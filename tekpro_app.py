import streamlit as st
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt


# ========================
# Fungsi-fungsi utama
# ========================

def load_data(csv_file):
    """
    Membaca file CSV dan memastikan kolom yang dibutuhkan ada.
    Kolom yang dibutuhkan: X, Y, Anomali
    """
    df = pd.read_csv(csv_file)
    required_cols = {"X", "Y", "Anomali"}
    if not required_cols.issubset(df.columns):
        raise ValueError(
            f"File CSV harus memiliki kolom: {', '.join(required_cols)}. "
            f"Kolom yang ada: {', '.join(df.columns)}"
        )
    return df


def interpolate_grid(df, n_grid=100, method="cubic"):
    """
    Melakukan interpolasi ke grid teratur menggunakan scipy.griddata.

    Parameters
    ----------
    df : DataFrame dengan kolom X, Y, Anomali
    n_grid : ukuran grid (n_grid x n_grid)
    method : 'linear', 'cubic', atau 'nearest'
    """
    x = df["X"].values
    y = df["Y"].values
    z = df["Anomali"].values

    # Membuat grid teratur di domain X-Y
    xi = np.linspace(x.min(), x.max(), n_grid)
    yi = np.linspace(y.min(), y.max(), n_grid)
    XI, YI = np.meshgrid(xi, yi)

    # Interpolasi
    ZI = griddata((x, y), z, (XI, YI), method=method)

    return XI, YI, ZI


def make_kml(df, name="Survei Medan Potensial"):
    """
    Membuat string file KML sederhana berisi titik-titik survei
    yang dapat dibuka di Google Earth (desktop maupun web).
    """
    kml_header = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
    <name>{name}</name>
    <description>Lokasi titik survei medan potensial</description>
"""
    kml_footer = """</Document>
</kml>
"""

    placemarks = []
    for _, row in df.iterrows():
        x = row["X"]
        y = row["Y"]
        val = row["Anomali"]
        placemark = f"""
    <Placemark>
        <name>Anomali: {val:.2f}</name>
        <description>X={x}, Y={y}, Anomali={val}</description>
        <!-- Asumsi X=longitude, Y=latitude (sesuaikan dengan data Anda) -->
        <Point>
            <coordinates>{x},{y},0</coordinates>
        </Point>
    </Placemark>
"""
        placemarks.append(placemark)

    kml_body = "".join(placemarks)
    kml_full = kml_header + kml_body + kml_footer
    return kml_full


def plot_contour(XI, YI, ZI, df, cmap="viridis", show_points=True):
    """
    Membuat plot kontur / heatmap menggunakan matplotlib.
    """
    fig, ax = plt.subplots()
    # Heatmap / pcolormesh, masking NaN dulu supaya plot rapi
    Z_masked = np.ma.array(ZI, mask=np.isnan(ZI))
    pcm = ax.pcolormesh(XI, YI, Z_masked, shading="auto", cmap=cmap)
    cbar = fig.colorbar(pcm, ax=ax)
    cbar.set_label("Anomali")

    if show_points:
        ax.scatter(df["X"], df["Y"], s=20, edgecolor="k", facecolor="none", label="Titik data")
        ax.legend()

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Peta Anomali Medan Potensial (Interpolasi)")
    ax.set_aspect("equal")

    fig.tight_layout()
    return fig


# ========================
# Aplikasi Streamlit
# ========================

def main():
    st.title("Peta Anomali Medan Potensial")
    st.write(
        """
Aplikasi ini:
1. Mengimpor data survei medan potensial (X, Y, Anomali).
2. Melakukan interpolasi ke grid teratur.
3. Menampilkan visualisasi peta kontur / heatmap.
4. Menghasilkan file **KML** yang bisa dibuka di **Google Earth**.
"""
    )

    st.sidebar.header("Pengaturan")

    # Pilihan contoh data
    use_example = st.sidebar.checkbox("Gunakan data contoh", value=True)

    uploaded_file = None
    if not use_example:
        uploaded_file = st.file_uploader("Upload file CSV (kolom: X, Y, Anomali)", type=["csv"])

    # Parameter grid dan metode interpolasi
    n_grid = st.sidebar.slider("Ukuran grid (resolusi)", min_value=30, max_value=200, value=100, step=10)
    method = st.sidebar.selectbox("Metode interpolasi", ["linear", "cubic", "nearest"])
    show_points = st.sidebar.checkbox("Tampilkan titik data", value=True)

    # Muat data
    if use_example:
        st.subheader("Menggunakan data contoh")
        df = load_data("data_survei_medan_potensial.csv")
    else:
        if uploaded_file is None:
            st.warning("Silakan upload file CSV terlebih dahulu atau aktifkan 'Gunakan data contoh'.")
            return
        df = load_data(uploaded_file)

    st.write("### Data Survei (tabel)")
    st.dataframe(df)

    # Interpolasi & plot
    with st.spinner("Melakukan interpolasi dan membuat peta..."):
        XI, YI, ZI = interpolate_grid(df, n_grid=n_grid, method=method)
        fig = plot_contour(XI, YI, ZI, df, show_points=show_points)
        st.pyplot(fig)

    # ========================
    # Pembuatan file KML
    # ========================
    st.write("### Ekspor Lokasi ke Google Earth (KML)")
    kml_name = st.text_input("Nama layer KML", value="Survei Medan Potensial")
    if st.button("Buat file KML"):
        kml_data = make_kml(df, name=kml_name)
        st.download_button(
            label="Download KML untuk Google Earth",
            data=kml_data,
            file_name="survei_medan_potensial.kml",
            mime="application/vnd.google-earth.kml+xml",
        )
        st.info("Setelah di-download, buka file KML tersebut di Google Earth (desktop / web).")


if __name__ == "__main__":
    main()
