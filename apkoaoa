import numpy as np

# Placeholder for the CSV file path. Please replace with your actual file path.
# Ensure your CSV has columns like X, Y, and value (or similar numeric data).
csv_file_path = 'survey_data.csv'  # e.g., 'data/field_survey.csv'

# Load the data using numpy.genfromtxt()
# Assuming the CSV is comma-delimited and has no header row.
# If your CSV has a header, set `skip_header=1`.
# If your delimiter is different, adjust `delimiter` accordingly.
try:
    survey_data = np.genfromtxt(csv_file_path, delimiter=',')
    print("Survey data loaded successfully.")
    print(f"Shape of survey_data: {survey_data.shape}")
    print("First 5 rows of survey_data:")
    print(survey_data[:5])
except FileNotFoundError:
    print(f"Error: The file '{csv_file_path}' was not found. Please ensure the path is correct and the file exists.")
except Exception as e:
    print(f"An error occurred while loading the data: {e}")
# Create a dummy CSV file for demonstration purposes
# In a real scenario, you would replace 'survey_data.csv' with your actual file path.
dummy_data = """
X,Y,value
1,1,10.5
1,2,11.2
1,3,10.8
2,1,12.1
2,2,13.5
2,3,12.9
3,1,11.0
3,2,10.1
3,3,9.5
"""

csv_file_path = 'survey_data.csv'

with open(csv_file_path, 'w') as f:
    f.write(dummy_data)

print(f"Dummy file '{csv_file_path}' created successfully.")

# Now, re-attempt to load the data using numpy.genfromtxt()
# Assuming the CSV is comma-delimited and has a header row, so we skip_header=1.
try:
    survey_data = np.genfromtxt(csv_file_path, delimiter=',', skip_header=1)
    print("Survey data loaded successfully.")
    print(f"Shape of survey_data: {survey_data.shape}")
    print("First 5 rows of survey_data:")
    print(survey_data[:5])
except Exception as e:
    print(f"An error occurred while loading the data: {e}")
import numpy as np
import os

# Corrected dummy CSV data without the initial newline character
dummy_data = "X,Y,value\n1,1,10.5\n1,2,11.2\n1,3,10.8\n2,1,12.1\n2,2,13.5\n2,3,12.9\n3,1,11.0\n3,2,10.1\n3,3,9.5"

csv_file_path = 'survey_data.csv'

with open(csv_file_path, 'w') as f:
    f.write(dummy_data)

print(f"Dummy file '{csv_file_path}' recreated successfully with corrected data.")

# Re-attempt to load the data using numpy.genfromtxt()
# Assuming the CSV is comma-delimited and has a header row, so we skip_header=1.
try:
    survey_data = np.genfromtxt(csv_file_path, delimiter=',', skip_header=1)
    print("Survey data loaded successfully after correction.")
    print(f"Shape of survey_data: {survey_data.shape}")
    print("First 5 rows of survey_data:")
    print(survey_data[:5])
except Exception as e:
    print(f"An error occurred while loading the data: {e}")
x = survey_data[:, 0]
y = survey_data[:, 1]
values = survey_data[:, 2]

print(f"X coordinates (first 5): {x[:5]}")
print(f"Y coordinates (first 5): {y[:5]}")
print(f"Values (first 5): {values[:5]}")
from scipy.interpolate import griddata

# Create a regular grid for interpolation
# Determine the range for X and Y from the original data
xi = np.linspace(x.min(), x.max(), 100) # 100 points for X-axis
yi = np.linspace(y.min(), y.max(), 100) # 100 points for Y-axis

grid_x, grid_y = np.meshgrid(xi, yi)

# Perform grid interpolation
# 'linear' is a common interpolation method, 'cubic' or 'nearest' can also be used.
points = np.vstack((x, y)).T
grid_z = griddata(points, values, (grid_x, grid_y), method='linear')

print(f"Shape of grid_x: {grid_x.shape}")
print(f"Shape of grid_y: {grid_y.shape}")
print(f"Shape of interpolated grid_z: {grid_z.shape}")
print("Interpolation complete. grid_z contains the interpolated values.")
import matplotlib.pyplot as plt

# Create a contour plot of the interpolated data
plt.figure(figsize=(10, 8))
plt.contourf(grid_x, grid_y, grid_z, levels=50, cmap='viridis') # Using 'viridis' colormap with 50 levels

# Add a colorbar
cbar = plt.colorbar()
cbar.set_label('Value')

# Set axis labels and title
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.title('Contour Plot of Interpolated Survey Data')

# Display the plot
plt.show()
