import pandas as pd
import numpy as np
from gtda.homology import VietorisRipsPersistence
from gtda.plotting import plot_diagram

VR = VietorisRipsPersistence(homology_dimensions=[0, 1, 2])  # Parameter explained in the text
 
acoes = pd.read_csv("gol.csv", decimal=".", header=None)
# np.floar é obsoleto, vou usar o float sozinho
# acoes_array = acoes.values[1:,4:5].astype(np.float)
acoes_array = acoes.values[1:,4:5].astype(float)
acoes_df = pd.DataFrame(acoes_array)

td = acoes_df.head()
print(td)

td = [[i, 0, 0] for i in td[0]]
print(td)

X = np.array(td)
print(X)

m = X.reshape(1, *X.shape)
diagrams = VR.fit_transform(m)
print(diagrams.shape)

i = 0
plot_diagram(diagrams[i])