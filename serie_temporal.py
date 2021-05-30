# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd


# %%
acoes = pd.read_csv("gol.csv")
# acoes["Date"].to_period("M")

data = pd.to_datetime(acoes.Date) 

acoes.Date = data
# Por perido de mês .to_period("M")
sep = acoes.set_index("Date").to_period("M")

# acoes.Date
sep.plot(figsize = (15, 7))


# %%
# acoes.info()
sep.info()


# %%
acoes.Date = pd.to_datetime(acoes.Date)
acoes.info()


# %%
# dt_intervalo = dt.Date.astype('datetime64[M]')
# Testando separar por mês
# mas ainda não foi aplicado


# %%

# No caso, acoes["Date"] = acoes['Date'].dt.to_period('M')
acoes.set_index("Date", inplace=True)


# %%
acoes.info()


# %%
acoes.plot(figsize = (15, 7))


# %%
acoes.Close.plot(figsize = (14, 5))
# Aparti daqui vai ser usado só os valores de Close


# %%

# o metodo rolling é para aplicar medidas moveis, e o mean é o das médias
acoes.Close.rolling(12).mean()


# %%
acoes.Close.rolling(12).mean().plot(figsize=(14, 5))


# %%
# Agora agrupando por anos
acoes.Close.groupby(acoes.index.year).sum()


# %%
acoes.Close.groupby(acoes.index.year).sum().plot(figsize=(14, 5))


# %%
acoes.Close.diff().groupby(acoes.index.month).mean().plot(figsize=(14, 5))


# %%
# Ver apenas as informações de 2017 até 2019
f = (acoes.index.year >= 2017) & (acoes.index.year <= 2019)
# aplicando o filtro, aplicando a diferença, agrupando por mês e gerando o gráfico
# acoes[f].Close.diff().groupby(acoes.index.month).mean().plot(figsize=(14, 5))


# %%

acoes.Close.diff().groupby(acoes.index.month).mean()


# %%
acoes.Close.diff().plot(figsize=(15, 6))


# %%
f = (acoes.index.year >= 2017) & (acoes.index.year <= 2018)
# aplicando o filtro, aplicando a diferença, agrupando por mês
acoes[f].Close.diff().plot(figsize=(15, 6))


# %%
f = (acoes.index.year >= 2019) & (acoes.index.year <= 2021)
# aplicando o filtro, aplicando a diferença, agrupando por mês
acoes[f].Close.diff().plot(figsize=(15, 6))


# %%
acoes.Close.diff().groupby(acoes.index.month).mean().plot(figsize=(14, 5))


# %%
acoes.Close.diff().groupby(acoes.index.month).mean().plot(figsize=(14, 5), kind = "bar")


# %%
serie = acoes.Close.diff().groupby(acoes.index.month).mean()
serie


# %%
from visibility_graph import visibility_graph
import networkx as nx
import matplotlib.pyplot as plt

serie_t = list(serie)
serie_t

gg = visibility_graph(serie_t)

g = nx.Graph()
gg.nodes()

serie_t


# %%
g.edges()


# %%
# ([(0, 1), (0, 2)(-), (0, 3), (0, 4)(-), (1, 2), (1, 3), (2, 3), (3, 4)])
# Olhando para esses vetores eles são parecidos

for i in gg.nodes():
    g.add_node(i)

g.nodes()


# %%
for fu in list(gg.edges()):
    g.add_edge(fu[0], fu[1])

g.edges()


# %%
# Mostra o dicionario do vetores
g.degree()


# %%
# gerando matrix adjacency
adi = nx.adj_matrix(g)
# Mostrando ela completa
adi.todense()


# %%
plt.figure(1)
nx.draw_networkx(g, pos=nx.spring_layout(g), with_labels=True)
plt.show()


# %%



