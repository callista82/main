import streamlit as st
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

# Set the page configuration for the Streamlit app
st.set_page_config(
    page_title="Visualisasi Anomali Data Survei",
    layout="centered" # Can be "wide" or "centered"
)

st.title("Visualisasi Anomali Data Survei")
st.write("Aplikasi ini memvisualisasikan anomali data survei medan potensi dengan memuat data, melakukan interpolasi grid, dan membuat visualisasi kontur atau heatmap.")

# File Uploader
uploaded_file = st.file_uploader("Unggah file CSV Anda", type=["csv"])

if uploaded_file is not None:
    try:
        # Read the uploaded file. Streamlit's file_uploader provides a file-like object.
        # Assuming the uploaded CSV is similar to the dummy data (comma-delimited, with header).
        survey_data = np.genfromtxt(uploaded_file, delimiter=',', skip_header=1)

        # Check if data was loaded successfully (e.g., not empty or all NaNs)
        if survey_data.size == 0 or np.all(np.isnan(survey_data)):
            st.error("Uploaded CSV file is empty or contains no valid numeric data after skipping header.")
        else:
            st.success("Data dari file CSV berhasil dimuat.")
            st.write(f"Shape of loaded data: {survey_data.shape}")
            st.write("First 5 rows of data:")
            st.dataframe(survey_data[:5]) # Use st.dataframe for better display in Streamlit

            # Store data in session state to persist across reruns
            st.session_state['survey_data'] = survey_data

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat data dari file: {e}")
else:
    st.info("Mohon unggah file CSV untuk memulai.")

# Extract X, Y, and Value columns (only if data is loaded)
if 'survey_data' in st.session_state and st.session_state['survey_data'] is not None:
    try:
        survey_data = st.session_state['survey_data']

        # Extract X, Y, and value columns
        x = survey_data[:, 0]
        y = survey_data[:, 1]
        values = survey_data[:, 2]

        st.success("Koordinat X, Y, dan nilai berhasil diekstrak.")
        # st.write(f"X coordinates (first 5): {x[:5]}") # Commented out for cleaner app
        # st.write(f"Y coordinates (first 5): {y[:5]}") # Commented out for cleaner app
        # st.write(f"Values (first 5): {values[:5]}") # Commented out for cleaner app

        # Store extracted data in session state for later use
        st.session_state['x'] = x
        st.session_state['y'] = y
        st.session_state['values'] = values

    except IndexError:
        st.error("File CSV yang diunggah tidak memiliki 3 kolom (X, Y, Value) yang diharapkan.")
    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengekstrak data kolom: {e}")

# Perform Grid Interpolation (only if X, Y, values are extracted)
if 'x' in st.session_state and 'y' in st.session_state and 'values' in st.session_state:
    try:
        x = st.session_state['x']
        y = st.session_state['y']
        values = st.session_state['values']

        # Create a regular grid for interpolation
        xi = np.linspace(x.min(), x.max(), 100) # 100 points for X-axis
        yi = np.linspace(y.min(), y.max(), 100) # 100 points for Y-axis

        grid_x, grid_y = np.meshgrid(xi, yi)

        # Perform grid interpolation
        points = np.vstack((x, y)).T
        grid_z = griddata(points, values, (grid_x, grid_y), method='linear')

        st.success("Interpolasi grid berhasil dilakukan.")
        # st.write(f"Shape of interpolated grid_z: {grid_z.shape}") # Commented out for cleaner app

        # Store interpolated data in session state for later use
        st.session_state['grid_x'] = grid_x
        st.session_state['grid_y'] = grid_y
        st.session_state['grid_z'] = grid_z

    except Exception as e:
        st.error(f"Terjadi kesalahan saat melakukan interpolasi grid: {e}")

# Visualize the Interpolated Data (only if grid_x, grid_y, grid_z are available)
if 'grid_x' in st.session_state and 'grid_y' in st.session_state and 'grid_z' in st.session_state:
    try:
        grid_x = st.session_state['grid_x']
        grid_y = st.session_state['grid_y']
        grid_z = st.session_state['grid_z']

        st.subheader("Visualisasi Peta Kontur")

        # Create a Matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create a contour plot of the interpolated data
        contour = ax.contourf(grid_x, grid_y, grid_z, levels=50, cmap='viridis') # Using 'viridis' colormap with 50 levels

        # Add a colorbar
        cbar = fig.colorbar(contour, ax=ax)
        cbar.set_label('Nilai Anomali')

        # Set axis labels and title
        ax.set_xlabel('Koordinat X')
        ax.set_ylabel('Koordinat Y')
        ax.set_title('Peta Kontur Data Survei Terinterpolasi')
        
        # Display the plot in Streamlit
        st.pyplot(fig)
        st.success("Peta kontur berhasil dibuat.")

    except Exception as e:
        st.error(f"Terjadi kesalahan saat membuat peta kontur: {e}")
else:
    st.info("Unggah file CSV, ekstrak data, dan lakukan interpolasi terlebih dahulu untuk melihat visualisasi.")
