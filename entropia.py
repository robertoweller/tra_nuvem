from data.generate_datasets import make_point_clouds
from gtda.homology import VietorisRipsPersistence
from gtda.plotting import plot_diagram
import pandas as pd


n_samples_per_class = 10
point_clouds, labels = make_point_clouds(n_samples_per_class, 10, 0.1)
point_clouds.shape
print(f"There are {point_clouds.shape[0]} point clouds in {point_clouds.shape[2]} dimensions, "
      f"each with {point_clouds.shape[1]} points.")
# Aqui são 30 nuvens de pontos em 3 dimensões, cada uma com 100 pontos.
print(point_clouds)
VR = VietorisRipsPersistence(homology_dimensions=[0, 1, 2])  # Parameter explained in the text
diagrams = VR.fit_transform(point_clouds)
print(diagrams.shape)

i = 0
plot_diagram(diagrams[i])
