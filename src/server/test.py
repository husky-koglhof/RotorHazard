from matplotlib import pyplot as plt
import os
import numpy as np


GAMMA_TABLE_PATH = os.path.join(os.path.dirname(__file__), 'gamma_table.npy')

# plt.imshow(np.load(GAMMA_TABLE_PATH), cmap='gray')
# plt.show()
print(np.load(GAMMA_TABLE_PATH))
