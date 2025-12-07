import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import io
import zipfile

st.set_page_config(layout="wide", page_title="Pemetaan Medan Potensial")
st.title("Aplikasi Pemetaan Medan Potensial - Kontur & Heatmap")
st.write("Upload CSV berisi kolom: X, Y, Value (separator koma).")

uploaded_file = st.file_uploader("Upload file CSV", type=["csv"]) 

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Gagal membaca CSV: {e}")
        st.stop()

    # ============================
    # TAMPILKAN TABEL DATA SURVEI
    # ============================
    st.subheader("Tabel Data Survei Medan Potensial")
    st.dataframe(df, use_container_width=True)
    st.write(f"Jumlah data: {len(df)} titik pengukuran")

    # ============================
    # CEK KOLOM X, Y, VALUE
    # ============================
    try:
        xi = [c for c in df.columns if c.lower().startswith('x')][0]
        yi = [c for c in df.columns if c.lower().startswith('y')][0]
        vi = [c for c in df.columns if (c.lower().startswith('v') or c.lower().startswith('value') or c.lower().startswith('z'))][0]
    except Exception:
        st.error('CSV harus punya kolom X, Y, dan Value.')
        st.stop()

    x = df[xi].astype(float).values
    y = df[yi].astype(float).values
    val = df[vi].astype(float).values

    # ============================
    # PENGATURAN INTERPOLASI
    # ============================
    col1, col2 = st.columns([1,3])
    with col1:
        res = st.slider('Resolusi grid', 50, 400, 200)
        method = st.selectbox('Metode interpolasi', ['linear', 'cubic', 'nearest'])
        show_contour = st.checkbox('Tampilkan kontur', value=True)
        show_heatmap = st.checkbox('Tampilkan heatmap', value=True)

    # ============================
    # BUAT GRID
    # ============================
    xmin, xmax = x.min(), x.max()
    ymin, ymax = y.min(), y.max()
    xi_lin = np.linspace(xmin, xmax, res)
    yi_lin = np.linspace(ymin, ymax, res)
    XI, YI = np.meshgrid(xi_lin, yi_lin)
    points = np.column_stack((x, y))

    # ============================
    # INTERPOLASI
    # ============================
    try:
        ZI = griddata(points, val, (XI, YI), method=method)
    except:
        ZI = griddata(points, val, (XI, YI), method='nearest')

    # ============================
    # PLOT PETA
    # ============================
    with col2:
        fig, ax = plt.subplots(figsize=(8,6))

        if show_heatmap:
            im = ax.imshow(np.flipud(ZI), extent=(xmin, xmax, ymin, ymax), aspect='auto')
            plt.colorbar(im, ax=ax, label='Value')

        if show_contour:
            try:
                cs = ax.contour(XI, YI, ZI, 10, linewidths=0.8, colors='black')
                ax.clabel(cs, inline=True, fontsize=8)
            except:
                pass

        ax.scatter(x, y, c='white', s=8, edgecolors='black')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('Peta Medan Potensial')

        st.pyplot(fig)

    # ============================
    # SIMPAN HEATMAP PNG
    # ============================
    vmin = np.nanmin(ZI)
    img = np.flipud(ZI.copy())
    img = np.nan_to_num(img, nan=vmin)

    heat_buf = io.BytesIO()
    plt.imsave(heat_buf, img, cmap='jet', format='png')
    heat_buf.seek(0)

    # ============================
    # BUAT FILE KML
    # ============================
    kml_doc = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>Peta Heatmap Medan Potensial</name>
  <GroundOverlay>
    <name>Heatmap Overlay</name>
    <Icon>
      <href>heatmap.png</href>
    </Icon>
    <LatLonBox>
      <north>{ymax}</north>
      <south>{ymin}</south>
      <east>{xmax}</east>
      <west>{xmin}</west>
    </LatLonBox>
  </GroundOverlay>
</Document>
</kml>
"""

    # ============================
    # BUNGKUS JADI KMZ
    # ============================
    kmz_bytes = io.BytesIO()
    with zipfile.ZipFile(kmz_bytes, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("doc.kml", kml_doc)
        zf.writestr("heatmap.png", heat_buf.getvalue())
    kmz_bytes.seek(0)

    # ============================
    # TOMBOL DOWNLOAD KMZ
    # ============================
    st.download_button(
        "Download Heatmap KMZ (Google Earth)",
        kmz_bytes.getvalue(),
        "heatmap_overlay.kmz",
        mime="application/vnd.google-earth.kmz"
    )

    st.success("Heatmap berhasil dibuat & bisa dibuka di Google Earth!")

else:
    st.info("Silakan upload file CSV untuk memulai.")
