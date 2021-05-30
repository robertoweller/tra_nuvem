# pip3 install joblib
# pip3 install openml
import pandas as pd
import numpy as np
from gtda.time_series import Resampler, SlidingWindow, takens_embedding_optimal_parameters, \
    TakensEmbedding, PermutationEntropy
from gtda.homology import WeakAlphaPersistence, VietorisRipsPersistence
from gtda.diagrams import Scaler, Filtering, PersistenceEntropy, BettiCurve, PairwiseDistance
from gtda.graphs import KNeighborsGraph, GraphGeodesicDistance

from gtda.pipeline import Pipeline

import numpy as np
from sklearn.metrics import pairwise_distances

import plotly.express as px
from plotly.offline import init_notebook_mode, iplot
init_notebook_mode(connected=True)

# gtda plotting functions
from gtda.plotting import plot_heatmap

# Import data from openml
import openml


x_periodic = np.linspace(0, 10, 1000)
# Euler?
y_periodic = np.cos(5 * x_periodic)
print(y_periodic)


dt = pd.DataFrame(y_periodic)
print(dt)


dt.plot(figsize=(12, 7))