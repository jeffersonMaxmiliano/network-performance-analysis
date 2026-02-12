import pandas as pd
import matplotlib.pyplot as plt
import os

# --- Configuration ---
TOPIC = 'webcam'
RESOLUTION = 'dci4k'
N_HOSTS = 1
TIME_LIMIT = 300  # Exact time limit in seconds

# Color palette
COLOR_NODE1 = '#55a868'  # Green
COLOR_NODE2 = '#c44e52'  # Red

# File paths
PATH_NODE1 = 'Wi-FI_6_80_web.csv'
PATH_NODE2 = '5G_webcam.csv'

save_directory = r'C:\Users\jefferson\Desktop\Testbed\ISCC_2026'

PARAMETERS = ['fps', 'bitrate_mbps']
UNITS = {'fps': 'FPS', 'bitrate_mbps': 'Bitrate (Mbps)'}

# --- Function to process data ---
def process_data(path):
    if not os.path.exists(path):
        print(f"⚠️ File not found: {path}")
        return None, None

    df = pd.read_csv(path)
    numeric_columns = ['fps', 'bitrate_mbps', 'tempo_relativo', 'n_host']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df_base = df[
        (df['n_host'] == N_HOSTS) &
        (df['fonte'] == TOPIC) &
        (df['resolucao'] == RESOLUTION) &
        (df['tempo_relativo'] <= TIME_LIMIT)
    ]

    df_mean = df_base.groupby('tempo_relativo')[PARAMETERS].mean().reset_index()
    df_std = df_base.groupby('tempo_relativo')[PARAMETERS].std().reset_index()
    return df_mean, df_std

# --- 1. Load Data ---
n1_mean, n1_std = process_data(PATH_NODE1)
n2_mean, n2_std = process_data(PATH_NODE2)

# --- 2. Create Subplots ---
fig, axs = plt.subplots(len(PARAMETERS), 1, figsize=(12, 10), sharex=True)
if len(PARAMETERS) == 1:
    axs = [axs]

for i, param in enumerate(PARAMETERS):

    # --- Plot Node 1 (Wi-Fi 6) ---
    if n1_mean is not None:
        mean_val1 = n1_mean[param].mean()
        min_val1 = n1_mean[param].min()
        max_val1 = n1_mean[param].max()
        legend_n1 = f'Node Wi-Fi 6: (Min: {min_val1:.2f}, Max: {max_val1:.2f}, Avg: {mean_val1:.2f})'

        axs[i].plot(
            n1_mean['tempo_relativo'],
            n1_mean[param],
            color=COLOR_NODE1,
            linewidth=2.5,
            label=legend_n1
        )

        axs[i].fill_between(
            n1_mean['tempo_relativo'],
            n1_mean[param] - n1_std[param],
            n1_mean[param] + n1_std[param],
            color=COLOR_NODE1,
            alpha=0.2
        )

    # --- Plot Node 2 (5G) ---
    if n2_mean is not None:
        mean_val2 = n2_mean[param].mean()
        min_val2 = n2_mean[param].min()
        max_val2 = n2_mean[param].max()
        legend_n2 = f'Node 5G: (Min: {min_val2:.2f}, Max: {max_val2:.2f}, Avg: {mean_val2:.2f})'

        axs[i].plot(
            n2_mean['tempo_relativo'],
            n2_mean[param],
            color=COLOR_NODE2,
            linewidth=2.5,
            label=legend_n2
        )

        axs[i].fill_between(
            n2_mean['tempo_relativo'],
            n2_mean[param] - n2_std[param],
            n2_mean[param] + n2_std[param],
            color=COLOR_NODE2,
            alpha=0.2
        )

    # --- Formatting ---
    axs[i].set_ylabel(UNITS.get(param, param), fontsize=35, fontweight='bold')

    # 🔹 Floating legend with adjustable position
    legend = axs[i].legend(
        fontsize=22,
        frameon=True,
        facecolor='white',
        framealpha=0.9
    )
    legend.set_draggable(True)

    axs[i].grid(True, linestyle='--', alpha=0.5)
    axs[i].tick_params(axis='both', which='major', labelsize=16)
    axs[i].set_xlim(0, TIME_LIMIT)

    if param == 'bitrate_mbps':
        axs[i].set_ylim(0, 95)

axs[-1].set_xlabel('Time (s)', fontsize=35, fontweight='bold')

plt.tight_layout()

# --- 3. Save Figure ---
os.makedirs(save_directory, exist_ok=True)
file_name = f"COMPARATIVE-{TOPIC}-{RESOLUTION}.pdf"
full_path = os.path.join(save_directory, file_name)
fig.savefig(full_path, dpi=300, bbox_inches='tight')

print(f"✅ Comparison chart (0–300 s) successfully saved at: {full_path}")
plt.show()
