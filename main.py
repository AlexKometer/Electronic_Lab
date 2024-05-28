import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Set the title of the Streamlit app
st.title("Bode Diagram Generator for High/Lowpass Filter")


# Function to calculate gain
def calculate_gain(input_voltage, output_voltage):
    return 20 * np.log10(output_voltage / input_voltage)


# Ensure the directories exist
os.makedirs("saved_png", exist_ok=True)
os.makedirs("saved_csv", exist_ok=True)

# User inputs
st.sidebar.header("Filter Settings")
input_voltage = st.sidebar.number_input("Input Voltage (V)", min_value=0.0, max_value=24.0, value=1.0, step=0.01)

st.sidebar.header("Measurement Settings")
frequency = st.sidebar.number_input("Frequency (Hz)", min_value=0.1, value=1.0, step=0.1)
output_voltage = st.sidebar.number_input("Output Voltage (V)", min_value=0.0, max_value=24.0, value=1.0, step=0.01)

# Storing inputs
if 'measurements' not in st.session_state:
    st.session_state['measurements'] = []

if st.sidebar.button("Add Measurement"):
    st.session_state['measurements'].append({'Frequency': frequency, 'Output Voltage': output_voltage})

# Display the measurements
st.write("Measurements:")
measurements_df = pd.DataFrame(st.session_state['measurements'])

# Sort measurements by frequency
measurements_df.sort_values(by='Frequency', inplace=True)

st.write(measurements_df)

# Calculate gain and plot Bode diagram if there are measurements
if not measurements_df.empty:
    measurements_df['Gain (dB)'] = measurements_df.apply(
        lambda row: calculate_gain(input_voltage, row['Output Voltage']), axis=1)

    # Find the -3dB point dynamically
    max_gain = measurements_df['Gain (dB)'].max()
    minus_3db_gain = max_gain - 3

    # Interpolating to find the frequency corresponding to the -3dB point
    sorted_df = measurements_df.sort_values(by='Frequency')
    minus_3db_freq = np.interp(minus_3db_gain, sorted_df['Gain (dB)'], sorted_df['Frequency'])

    # Plot Bode diagram
    fig, ax = plt.subplots()
    ax.semilogx(sorted_df['Frequency'], sorted_df['Gain (dB)'])
    ax.set_title('Bode Diagram')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Gain (dB)')
    ax.axhline(y=minus_3db_gain, color='r', linestyle='--', linewidth=0.7, label='-3dB')
    ax.axvline(x=minus_3db_freq, color='g', linestyle='--', linewidth=0.7)
    ax.legend()
    ax.grid(which='both', linestyle='--', linewidth=0.5)
    st.pyplot(fig)

    # Display the -3dB frequency
    st.write(f"The -3dB frequency is approximately: {minus_3db_freq:.2f} Hz")

    # Save plot as PNG
    plot_file_name = st.text_input("Enter file name to save plot", "bode_plot")

    if st.button("Save Plot"):
        plot_path = os.path.join("saved_png", f"{plot_file_name}.png")
        fig.savefig(plot_path, format='png')
        st.success(f"Plot saved as {plot_path}")

# Save to CSV
file_name = st.text_input("Enter file name to save CSV", "measurements.csv")
if st.button("Save to CSV"):
    csv_path = os.path.join("saved_csv", file_name)
    measurements_df.to_csv(csv_path, index=False)
    st.success(f"File saved as {csv_path}")
