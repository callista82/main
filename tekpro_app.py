import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import io
import zipfile
import base64
import urllib.parse

st.set_page_config(layout="wide", page_title="Pemetaan Medan Potensial")
st.title("Aplikasi Pemetaan Medan Potensial - Kontur & Heatmap")
st.write("Upload CSV berisi kolom: X, Y, Value (separator koma).")

uploaded_file = st.file_uploader("Upload file CSV", type=["csv"]) 

# Helper: value -> RGB (as hex rrggbb)
def value_to_rgb_hex(v, vmin, vmax):
    # Normalize 0..1
    if np.isnan(v):
        return 'ffffff'
    t = (v - vmin) / (vmax - vmin) if vmax > vmin else 0.5
    # Use a simple diverging map: blue -> white -> red
    if t < 0.5:
        # blue to white
        t2 = t / 0.5
        r = int(255 * t2 + 0 * (1 - t2))
        g = int(255 * t2 + 0 * (1 - t2))
        b = 255
    else:
        # white to red
        t2 = (t - 0.5) / 0.5
        r = 255
        g = int(255 * (1 - t2) + 255 * 0 * t2)
        b = int(255 * (1 - t2) )
    return f"{r:02x}{g:02x}{b:02x}"

# KML color format: aabbggrr
def rgb_hex_to_kml_color(hexrgb, alpha=255):
    r = hexrgb[0:2]
    g = hexrgb[2:4]
    b = hexrgb[4:6]
    a = f"{alpha:02x}"
    # KML wants aabbggrr
    return a + b + g + r

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Gagal membaca CSV: {e}")
        st.stop()

    # Check columns
    cols = [c.lower() for c in df.columns]
    # find X,Y,Value columns
    try:
        xi = [c for c in df.columns if c.lower().startswith('x')][0]
        yi = [c for c in df.columns if c.lower().startswith('y')][0]
        vi = [c for c in df.columns if (c.lower().startswith('v') or c.lower().startswith('value') or c.lower().startswith('z'))][0]
    except Exception:
        st.error('CSV harus punya kolom X, Y, Value (nama kolom bebas, minimal mengandung X, Y, dan Value/Z).')
        st.stop()

    x = df[xi].astype(float).values
    y = df[yi].astype(float).values
    val = df[vi].astype(float).values

    # Grid resolution (adjustable)
    col1, col2 = st.columns([1,3])
    with col1:
        res = st.slider('Resolusi grid (sisi, lebih besar = resolusi lebih rendah/butuh lebih cepat)', 50, 400, 200)
        method = st.selectbox('Metode interpolasi', ['linear', 'cubic', 'nearest'])
        show_contour = st.checkbox('Tampilkan kontur', value=True)
        show_heatmap = st.checkbox('Tampilkan heatmap (imshow)', value=True)

    # Create grid
    xmin, xmax = x.min(), x.max()
    ymin, ymax = y.min(), y.max()
    xi_lin = np.linspace(xmin, xmax, res)
    yi_lin = np.linspace(ymin, ymax, res)
    XI, YI = np.meshgrid(xi_lin, yi_lin)
    points = np.column_stack((x, y))

    # Interpolate
    try:
        ZI = griddata(points, val, (XI, YI), method=method)
    except Exception as e:
        st.warning(f'Griddata error: {e}. Falling back to nearest.')
        ZI = griddata(points, val, (XI, YI), method='nearest')

    # Plot
    with col2:
        fig, ax = plt.subplots(figsize=(8,6))
        vmin = np.nanmin(ZI)
        vmax = np.nanmax(ZI)
        if show_heatmap:
            im = ax.imshow(np.flipud(ZI), extent=(xmin, xmax, ymin, ymax), aspect='auto')
            plt.colorbar(im, ax=ax, label='Value')
        if show_contour:
            cs = ax.contour(XI, YI, ZI, 10, linewidths=0.7, colors='k')
            ax.clabel(cs, inline=True, fontsize=8)
        ax.scatter(x, y, c='white', s=8, edgecolors='black')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('Peta Medan Potensial')
        st.pyplot(fig)

    # Export image to PNG
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)


# ============================
# SIMPAN HEATMAP SEBAGAI PNG (OVERLAY)
# ============================
heat_buf = io.BytesIO()
plt.imsave(heat_buf, np.flipud(ZI), cmap='jet')
heat_buf.seek(0)

# ============================
# BUAT KML GROUND OVERLAY (ANTI ERROR XML)
# ============================
kml_doc = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + \
"<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n" + \
"<Document>\n" + \
"  <name>Peta Heatmap Medan Potensial</name>\n" + \
"  <GroundOverlay>\n" + \
"    <name>Heatmap Overlay</name>\n" + \
"    <Icon>\n" + \
"      <href>heatmap.png</href>\n" + \
"    </Icon>\n" + \
"    <LatLonBox>\n" + \
f"      <north>{ymax}</north>\n" + \
f"      <south>{ymin}</south>\n" + \
f"      <east>{xmax}</east>\n" + \
f"      <west>{xmin}</west>\n" + \
"    </LatLonBox>\n" + \
"  </GroundOverlay>\n" + \
"</Document>\n" + \
"</kml>"

# ============================
# BUNGKUS JADI KMZ
# ============================
kmz_bytes = io.BytesIO()
with zipfile.ZipFile(kmz_bytes, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("doc.kml", kml_doc)
    zf.writestr("heatmap.png", heat_buf.getvalue())

kmz_bytes.seek(0)

# ============================
# TOMBOL DOWNLOAD
# ============================
st.download_button(
    "✅ Download Heatmap KMZ (Buka di Google Earth)",
    kmz_bytes,
    "heatmap_overlay.kmz",
    mime="application/vnd.google-earth.kmz"
)

st.success("✅ Heatmap siap dibuka di Google Earth Pro!")
