from os import path
from data.generate_datasets import make_point_clouds
from gtda.homology import VietorisRipsPersistence
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

n_samples_per_class = 10
point_clouds, labels = make_point_clouds(n_samples_per_class, 10, 0.1)
point_clouds.shape
print(f"There are {point_clouds.shape[0]} point clouds in {point_clouds.shape[2]} dimensions, "
      f"each with {point_clouds.shape[1]} points.")


VR = VietorisRipsPersistence(homology_dimensions=[0, 1, 2])  # Parameter explained in the text
diagrams = VR.fit_transform(point_clouds)
diagrams.shape

x = []
y = []

for v in point_clouds:
    x.append(v[0])
    y.append(v[1])


lis_sx = []

for p1 in x:
    
    lis_sx.append([p1[0], p1[1], p1[2]])


lis_sy = []
for p2 in y:
    
    lis_sy.append([p2[0], p2[1], p2[2]])

plt.plot(x, y, 'go') # green bolinha
plt.title("nuvem de pontos")
plt.grid(True)
plt.xlabel("eixo horizontal")
plt.ylabel("eixo vertical")
plt.show()

# acoes = pd.read_csv("gol.csv", decimal=".", header=None)
acoes = pd.read_csv("gol.csv")
# acoes_array = acoes.values[1:,4:5].astype(np.float)
# acoes_df = pd.DataFrame(acoes_array)
acoes_df = pd.DataFrame(acoes)
ler = acoes_df.head()
print(ler['A'])


# Esse código foi usado para gerar o banco de dados
"""gol = []
gol = zip(lis_sx, lis_sy)

arq_gol = open('gol.csv', 'w')

arq_gol.write('A;B;C;D;E;F;\n')
arq_gol.write('Px1;Py1;Pz1;Px2;Py2;Pz2;\n')

for gx, gy in list(gol):
    arq_gol.write(f'{gx[0]};{gx[1]};{gx[2]};{gy[0]};{gx[1]};{gy[2]};\n')
    print(f'P1:{gx[0]}, {gx[1]}, {gx[2]}, P2:{gy[0]}, {gx[1]}, {gy[2]}')

arq_gol.close()"""