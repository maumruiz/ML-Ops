import pandas as pd

# En este caso se leen los datos desde archivos csv, pero
#  aqui podríamos estar obteniendo datos en tiempo real.
# Probablemente se necesiten estar actualizando los datos de precios de la leche,
#  variables climatologicas y macroeconomicas


def obtain_data():
    precipitaciones = pd.read_csv('./data/precipitaciones.csv')
    banco_central = pd.read_csv('./data/banco_central.csv')
    precio_leche = pd.read_csv('./data/precio_leche.csv')

    precipitaciones.to_pickle('saved/precipitaciones.pkl')
    banco_central.to_pickle('saved/banco_central.pkl')
    precio_leche.to_pickle('saved/precio_leche.pkl')