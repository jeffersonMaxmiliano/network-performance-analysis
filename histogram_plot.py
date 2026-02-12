import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# =========================================================
# 1. LIST OF FILES AND WI-FI CHANNELS
# =========================================================
#arquivos_config = [
#    {'arquivo': r'C:\Users\jefferson\Desktop\Testbed\ISCC_2026\Wi-Fi_20_brio.csv', 'Channel': 20},
#    {'arquivo': r'C:\Users\jefferson\Desktop\Testbed\ISCC_2026\Wi-Fi_20_web.csv',  'Channel': 20},
#    {'arquivo': r'C:\Users\jefferson\Desktop\Testbed\ISCC_2026\Wi-Fi_40_brio.csv', 'Channel': 40},
#    {'arquivo': r'C:\Users\jefferson\Desktop\Testbed\ISCC_2026\Wi-Fi_40_web.csv',  'Channel': 40},
#    {'arquivo': r'C:\Users\jefferson\Desktop\Testbed\ISCC_2026\Wi-Fi_80_brio.csv', 'Channel': 80},
#    {'arquivo': r'C:\Users\jefferson\Desktop\Testbed\ISCC_2026\Wi-Fi_80_web.csv',  'Channel': 80},
#]


# =========================================================
# 1. LIST OF 5G FILES
# =========================================================

arquivos_config = [
    {'arquivo': r'C:\Users\jefferson\Desktop\Testbed\ISCC_2026\5G_brio.csv', 'Channel': 5},
    {'arquivo': r'C:\Users\jefferson\Desktop\Testbed\ISCC_2026\5G_webcam.csv',  'Channel': 5},
]

dfs = []
for item in arquivos_config:
    try:
        df_temp = pd.read_csv(item['arquivo'])
        df_temp['Channel'] = item['Channel']
        dfs.append(df_temp)
    except FileNotFoundError:
        print(f"Warning: File {item['arquivo']} not found. Skipping.")

if not dfs:
    raise ValueError("No files were loaded!")

df_completo = pd.concat(dfs, ignore_index=True)

# =========================================================
# 2. DATA PROCESSING
# =========================================================
df_completo['fonte'] = df_completo['fonte'].replace({
    'brio': 'brio',
    'webcam': 'webcam'
})

df_completo['resolucao'] = df_completo['resolucao'].str.upper()

# =========================================================
# 3. DATA PREPARATION FOR PLOTTING
# =========================================================
df_plot = df_completo.rename(columns={
    'resolucao': 'Resolution',
    'fonte': 'Device',
    'fps': 'FPS',
    'bitrate_mbps': 'Bitrate (Mbps)'
})

ordem_resolucao = ['VGA', 'WVGA', 'XGA', 'HD', 'UXGA', 'FHD', 'QUADHD', 'DCI4K']
resolucoes_presentes = [
    r for r in ordem_resolucao
    if r in df_plot['Resolution'].unique()
]

df_long = df_plot.melt(
    id_vars=['Resolution', 'Device', 'Channel'],
    value_vars=['FPS', 'Bitrate (Mbps)'],
    var_name='Metric',
    value_name='Value'
)

# =========================================================
# 4. PLOT
# =========================================================
sns.set_theme(style="whitegrid")

palette_custom = {
    'brio': "#1ee35a",
    'webcam': "#e93030"
}

g = sns.catplot(
    data=df_long,
    x='Resolution',
    y='Value',
    hue='Device',
    col='Channel',
    row='Metric',
    kind='bar',
    height=3,
    aspect=1.5,
    sharey='row',
    margin_titles=True,
    palette=palette_custom,
    order=resolucoes_presentes,
    estimator='mean',
    errorbar='sd',
    width=0.45,
    linewidth=0.6,
    edgecolor='white',
    capsize=0.08
)

g.figure.set_size_inches(16, 8)

# =========================================================
# 5. FONTS AND LABELS
# =========================================================
g.set_axis_labels("", "")

# Wi-Fi 6 legend title
#g.set_titles(col_template="Wi-Fi channel: {col_name} MHz", row_template="")

# 5G legend title
g.set_titles(col_template="5G network", row_template="")

for ax in g.axes[0]:
    ax.set_title(ax.get_title(), fontsize=25)

for ax, row_name in zip(g.axes[:, 0], g.row_names):
    ax.set_ylabel(row_name, fontsize=25, fontweight='bold')

for ax in g.axes.flatten():
    ax.tick_params(axis='x', rotation=45, labelsize=25)
    ax.tick_params(axis='y', labelsize=25)

# =========================================================
# 6. FLOATING (DRAGGABLE) LEGEND
# =========================================================
if g._legend:
    g._legend.set_title("Device")
    g._legend.get_title().set_fontsize(25)

    labels_map = {
        'brio': 'Node 5G (LOS)',
        'webcam': 'Node 5G (NLOS)'
    }

    for text in g._legend.texts:
        text.set_text(labels_map[text.get_text()])
        text.set_fontsize(30)

    # 🔥 Make legend floating and draggable
    g._legend.set_draggable(True)

# =========================================================
# 7. SCALE ADJUSTMENT
# =========================================================
for i, row_name in enumerate(g.row_names):
    for ax in g.axes[i, :]:

        if row_name == 'FPS':
            ax.set_ylim(20, 31.9)
            ax.yaxis.set_major_locator(MultipleLocator(5))

        elif row_name == 'Bitrate (Mbps)':
            ax.set_ylim(0, 45)
            ax.yaxis.set_major_locator(MultipleLocator(5))

# =========================================================
# 8. SAVE ONLY WHEN CLOSING THE WINDOW
# =========================================================
def save_on_close(event):
    g.figure.savefig("grafico.pdf", bbox_inches="tight")
    print("PDF saved with the legend in the selected position.")

g.figure.canvas.mpl_connect("close_event", save_on_close)

plt.show()
