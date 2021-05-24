import pandas as pd
import numpy as np

acoes = pd.read_csv("x.csv", decimal=".", header=None)
acoes_array = acoes.values[1:,4:5].astype(np.float)
acoes_df = pd.DataFrame(acoes_array)
print(acoes_df.head())
