import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Folder cu fișiere CSV
folder_path = 'CSV'
files = [f for f in os.listdir(folder_path) if f.startswith('frame_') and f.endswith('.csv')]
num_files = len(files)

if num_files == 0:
    raise FileNotFoundError('Nu s-au găsit fișiere CSV.')

# Matrice 3D: 8x8xN
all_data = np.zeros((8, 8, num_files))

for k, file_name in enumerate(files):
    file_path = os.path.join(folder_path, file_name)
    data = pd.read_csv(file_path, header=None).to_numpy()
    all_data[:, :, k] = data

# Media pe fiecare termistor
mean_data = np.mean(all_data, axis=2)

# ===== Heatmap =====
plt.figure(figsize=(6,6))
im = plt.imshow(mean_data, cmap='jet', vmin=0, vmax=4000)
plt.colorbar(im)

plt.axis('equal')
plt.tight_layout()
plt.gca().invert_yaxis()  # echivalent cu set(gca,'YDir','normal') în MATLAB
plt.title('Media valorilor termistorilor (0 - 4000)')
plt.xlabel('Termistor P1')
plt.ylabel('Bank')

# ===== Scriere valori peste heatmap =====
for i in range(8):
    for j in range(8):
        val = mean_data[i, j]
        text_color = 'white' if val <= 2500 else 'black'
        plt.text(j, i, f'{val:.0f}', ha='center', va='center',
                 color=text_color, fontsize=9, fontweight='bold')

plt.show()