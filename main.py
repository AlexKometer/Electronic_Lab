import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


st.set_page_config(layout="wide")
# Set the title of the Streamlit app
st.title("Bode Diagram Generator for High/Lowpass Filter")



#2 collums in streamlit
col1, col2 = st.columns([1, 1])


# Function to calculate gain
def calculate_gain(input_voltage, output_voltage):
    return 20 * np.log10(output_voltage / input_voltage)

# Ensure the directories exist
os.makedirs("saved_png", exist_ok=True)
os.makedirs("saved_csv", exist_ok=True)

with col1:
    # User inputs
    st.header("Filter Settings")
    input_voltage = st.number_input("Input Voltage (V)", min_value=0.0, max_value=24.0, value=1.0, step=0.01)

    frequency = st.number_input("Frequency (Hz)", min_value=0.1, value=1.0, step=1.0)
    output_voltage = st.number_input("Output Voltage (V)", min_value=0.0, max_value=24.0, value=1.0, step=0.01)
    phase_shift = st.number_input("Phase Shift (degrees)", min_value=-180.0, max_value=180.0, value=0.0, step=0.1)

    # Storing inputs
    if 'measurements' not in st.session_state:
        st.session_state['measurements'] = []

    if st.button("Add Measurement"):
        st.session_state['measurements'].append({'Frequency': frequency, 'Output Voltage': output_voltage, 'Phase Shift': phase_shift})



with col2:

    st.write("Measurements:")
    measurements_df = pd.DataFrame(st.session_state['measurements'])


    if not measurements_df.empty:
        # Sort measurements by frequency
        measurements_df.sort_values(by='Frequency', inplace=True)
        st.write(measurements_df)

        # Calculate gain
        measurements_df['Gain (dB)'] = measurements_df.apply(
            lambda row: calculate_gain(input_voltage, row['Output Voltage']), axis=1)

        # Find the -3dB point dynamically
        max_gain = measurements_df['Gain (dB)'].max()
        minus_3db_gain = max_gain - 3

        # Interpolating to find the frequency corresponding to the -3dB point
        minus_3db_freq = np.interp(minus_3db_gain, measurements_df['Gain (dB)'], measurements_df['Frequency'])

        # Plot Bode diagram and Phase diagram in the same plot
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Bode Diagram
        color = 'tab:blue'
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Gain (dB)', color=color)
        ax1.semilogx(measurements_df['Frequency'], measurements_df['Gain (dB)'], color=color)
        ax1.axhline(y=minus_3db_gain, color='r', linestyle='--', linewidth=0.7, label='-3dB')
        ax1.axvline(x=minus_3db_freq, color='g', linestyle='--', linewidth=0.7)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(which='both', linestyle='--', linewidth=0.5)

        # Phase Diagram
        ax2 = ax1.twinx()  # instantiate a second y-axis that shares the same x-axis
        color = 'tab:orange'
        ax2.set_ylabel('Phase Shift (degrees)', color=color)
        ax2.semilogx(measurements_df['Frequency'], measurements_df['Phase Shift'], color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        #fig.tight_layout()  # ensure the plot is cleanly laid out
        st.pyplot(fig)

        # Display the -3dB frequency
        st.write(f"The -3dB frequency is approximately: {minus_3db_freq:.2f} Hz")

        # Save combined plot as PNG
        plot_file_name = st.text_input("Enter file name to save combined plot", "combined_plot")

        if st.button("Save Combined Plot"):
            combined_plot_path = os.path.join("saved_png", f"{plot_file_name}.png")
            fig.savefig(combined_plot_path, format='png')
            st.success(f"Combined plot saved as {combined_plot_path}")

    # Save to CSV
    file_name = st.text_input("Enter file name to save CSV", "measurements.csv")
    if st.button("Save to CSV") and not measurements_df.empty:
        csv_path = os.path.join("saved_csv", file_name)
        measurements_df.to_csv(csv_path, index=False)
        st.success(f"File saved as {csv_path}")

st.write("© Copyright by: Alexander Kometer")
