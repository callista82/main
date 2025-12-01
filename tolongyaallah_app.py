# Aplikasi Streamlit: Visualisasi Medan Potensial (Kontur & Heatmap) + Ekspor KMZ untuk Google Earth
# File: streamlit_pemetaan_magnetik_gravity.py
# Petunjuk singkat:
# - Unggah CSV yang memiliki kolom: X, Y, Value (header wajib: X,Y,Value)
# - Data X,Y diasumsikan dalam koordinat LAT/LON (derajat). Jika data dalam UTM atau sistem lain, konversi dulu ke lat/lon.
# - Aplikasi menampilkan scatter, interpolasi grid (griddata), heatmap dan peta kontur.
# - Opsi untuk mengunduh gambar PNG dan paket KMZ (KML + PNG) yang bisa langsung diimpor ke Google Earth.
# - Jalankan: `streamlit run streamlit_pemetaan_magnetik_gravity.py`

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import io
import zipfile
import base64
import matplotlib
from matplotlib import ticker

st.set_page_config(page_title="Pemetaan Medan Potensial", layout="wide")

st.title("Aplikasi Pemetaan Medan Potensial — Kontur & Heatmap")
st.markdown("Upload CSV berisi kolom `X, Y, Value` — X dan Y diasumsikan lat/lon (derajat). Jika tidak, konversi dulu ke lat/lon.")

# --- Sidebar controls ---
st.sidebar.header("Pengaturan Interpolasi & Visual")
grid_res = st.sidebar.slider("Resolusi grid (pixel per sumbu)", min_value=50, max_value=1000, value=250, step=50)
method = st.sidebar.selectbox("Metode interpolasi (scipy.griddata)", options=["linear", "cubic", "nearest"], index=0)
show_contours = st.sidebar.checkbox("Tampilkan kontur", value=True)
n_contours = st.sidebar.slider("Jumlah garis kontur", 5, 40, 12)
colormap = st.sidebar.selectbox("Colormap (matplotlib)", options=sorted([c for c in plt.colormaps()]), index=plt.colormaps().index('viridis') if 'viridis' in plt.colormaps() else 0)
anomaly_center = st.sidebar.checkbox("Pusatkan colormap di 0 (berguna untuk anomali)", value=False)

# Upload CSV
uploaded_file = st.file_uploader("Pilih file CSV (X,Y,Value)", type=["csv"]) 

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Gagal membaca CSV: {e}")
        st.stop()

    required_cols = [c.lower() for c in df.columns]
    # try to normalize header names
    if not set(['x','y','value']).issubset(set(required_cols)):
        # try uppercase
        st.error("CSV harus memiliki kolom 'X', 'Y', 'Value' (nama kolom tidak sensitif huruf besar/kecil). Periksa header file Anda.")
        st.write("Kolom yang ditemukan:", list(df.columns))
        st.stop()

    # Normalize to X,Y,Value
    col_map = {orig: orig for orig in df.columns}
    # find matching
    mapping = {}
    for orig in df.columns:
        low = orig.lower()
        if low == 'x': mapping['X'] = orig
        if low == 'y': mapping['Y'] = orig
        if low == 'value': mapping['Value'] = orig

    data = df[[mapping['X'], mapping['Y'], mapping['Value']]].rename(columns={mapping['X']:'X', mapping['Y']:'Y', mapping['Value']:'Value'})
    data = data.dropna(subset=['X','Y','Value'])
    data['X'] = pd.to_numeric(data['X'], errors='coerce')
    data['Y'] = pd.to_numeric(data['Y'], errors='coerce')
    data['Value'] = pd.to_numeric(data['Value'], errors='coerce')
    data = data.dropna()

    st.subheader("Preview data survei")
    st.dataframe(data.head(20))

    # Calculate bounds
    minx, maxx = data['X'].min(), data['X'].max()
    miny, maxy = data['Y'].min(), data['Y'].max()

    # Build grid
    xi = np.linspace(minx, maxx, grid_res)
    yi = np.linspace(miny, maxy, grid_res)
    XI, YI = np.meshgrid(xi, yi)

    # Interpolate
    with st.spinner('Melakukan interpolasi...'):
        try:
            ZI = griddata(points=(data['X'].values, data['Y'].values), values=data['Value'].values, xi=(XI, YI), method=method)
        except Exception as e:
            st.error(f"Interpolasi gagal: {e}")
            st.stop()

    # Mask NaNs for plotting
    ZIm = np.ma.masked_invalid(ZI)

    # Option to center colormap at zero
    vmin = np.nanmin(ZI)
    vmax = np.nanmax(ZI)
    if anomaly_center:
        vmax_abs = max(abs(vmin), abs(vmax))
        norm = matplotlib.colors.TwoSlopeNorm(vmin=-vmax_abs, vcenter=0.0, vmax=vmax_abs)
    else:
        norm = None

    # Create figure
    fig, ax = plt.subplots(figsize=(8,6), dpi=120)
    pcm = ax.pcolormesh(XI, YI, ZIm, shading='auto', cmap=colormap, norm=norm)
    ax.scatter(data['X'], data['Y'], c='k', s=6, alpha=0.6, label='Titik survei')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Heatmap Anomali')
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    cbar = fig.colorbar(pcm, ax=ax, shrink=0.8)
    cbar.set_label('Value')

    # Contours
    if show_contours:
        try:
            CS = ax.contour(XI, YI, ZI, levels=n_contours, linewidths=0.6, cmap='gray')
            ax.clabel(CS, inline=1, fontsize=8, fmt='%1.2f')
        except Exception as e:
            st.warning(f"Gagal membuat kontur: {e}")

    st.pyplot(fig)

    # Add download options: PNG of current figure and KMZ for Google Earth
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)

    # Prepare KMZ (KML + PNG)
    # KML GroundOverlay requires bounds in lat/lon: north, south, east, west
    # We compute extents from min/max X/Y. WARNING: If input coords are not lat/lon, the overlay will be misplaced in GE.
    north = maxy
    south = miny
    east = maxx
    west = minx

    png_bytes = buf.getvalue()

    kml_template = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Overlay Anomali</name>
    <GroundOverlay>
      <name>Heatmap Anomali</name>
      <Icon>
        <href>images/heatmap.png</href>
      </Icon>
      <LatLonBox>
        <north>{north}</north>
        <south>{south}</south>
        <east>{east}</east>
        <west>{west}</west>
        <rotation>0</rotation>
      </LatLonBox>
    </GroundOverlay>
  </Document>
</kml>
'''

    # Build KMZ in-memory
    kmz_buf = io.BytesIO()
    with zipfile.ZipFile(kmz_buf, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('doc.kml', kml_template)
        zf.writestr('images/heatmap.png', png_bytes)
    kmz_buf.seek(0)

    # Streamlit download buttons
    st.download_button("Unduh gambar PNG (heatmap)", data=png_bytes, file_name='heatmap.png', mime='image/png')
    st.download_button("Unduh file KMZ (untuk Google Earth)", data=kmz_buf.getvalue(), file_name='anomali_overlay.kmz', mime='application/vnd.google-earth.kmz')

    st.markdown("**Catatan penting:** Jika koordinat X/Y Anda bukan lat/lon (derajat), konversi terlebih dahulu ke lat/lon agar overlay di Google Earth berada pada lokasi yang tepat. Jika data X/Y adalah UTM, gunakan paket seperti `pyproj` untuk konversi sebelum upload.")

else:
    st.info('Silakan unggah file CSV untuk memulai. Contoh format (header): X,Y,Value')
    st.markdown('Contoh CSV:\n``nX,Y,Value\n-7.250,112.750,12.34\n-7.251,112.751,10.21\n```')

# END
