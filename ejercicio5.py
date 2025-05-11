import json
import sqlite3
from datetime import datetime

import pandas as pd
from matplotlib import pyplot as plt
from sklearn import linear_model
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error
from sklearn.tree import DecisionTreeClassifier, plot_tree


def fromTickets_to_Df(tickets):
    records = []
    for ticket in tickets:
        cliente = int(ticket['cliente'])
        fecha_apertura = datetime.strptime(ticket['fecha_apertura'], '%Y-%m-%d')
        fecha_cierre = datetime.strptime(ticket['fecha_cierre'], '%Y-%m-%d')
        duracion_ticket = (fecha_cierre - fecha_apertura).days
        es_mantenimiento = int(ticket['es_mantenimiento'])
        tipo_incidencia = int(ticket['tipo_incidencia'])

        record = {
            'cliente': cliente,
            'duracion_ticket': duracion_ticket,
            'es_mantenimiento': es_mantenimiento,
            'tipo_incidencia': tipo_incidencia
        }
        if 'es_critico' in ticket.keys():
            record['es_critico'] = int(ticket['es_critico'])

        records.append(record)
    return pd.DataFrame(records)
def loadModels():
    ## Crear modelos ##
    modelos = []
    names = ['Modelo Lineal', 'Árbol de Decisión', 'Bosque Aleatorio']
    regr = linear_model.LogisticRegression()
    dTree = DecisionTreeClassifier(max_depth=4, random_state=42)
    rForest = RandomForestClassifier(random_state=42)
    modelos.append(regr)
    modelos.append(dTree)
    modelos.append(rForest)
    return modelos, names
def trainModel(model):
    # Se entrenan los modelos con todos los datos disponibles del JSON data_clasified
    # No se hace división entre train y test
    path = 'datos/data_clasified.json'
    with open(path, 'r') as f:
        data = json.load(f)

    tickets = data['tickets_emitidos']

    df = fromTickets_to_Df(tickets)
    X = df.drop('es_critico', axis=1)
    y = pd.DataFrame(df['es_critico'])

    return model.fit(X.values, y)
def graficar(ejeX, y_test, modelos, predicciones):
    # Graficamos las predicciones junto con y_test
    n_splits = len(modelos)
    fig, axs = plt.subplots(n_splits, 1, figsize=(15, 14), sharey=True)
    i = 0
    for model in modelos:
        ax = axs[i]
        y_pred = predicciones[i]
        ax.scatter(ejeX, y_test, s=300, alpha=0.5, marker='*', color='red')
        ax.scatter(ejeX, y_pred, color='blue', alpha=1)
        ax.set_title(names[i])
        ax.set_xlabel('Id. Cliente')
        ax.set_ylabel('Crítico')
        ax.set_xticks(ejeX)
        ax.set_yticks([0, 1])
        ax.set_ylim(-0.1, 1.1)  # para mantener consistencia vertical
        ax.grid(axis='x')
        i += 1

    fig.suptitle('Predicción de Tickets Críticos', fontsize=16)
    plt.tight_layout(rect=(0, 0, 1, 0.96), pad=2)
    plt.show()

    # Gráfica 2: Coeficientes del modelo lineal
    features = X.columns
    coef = modelos[0].coef_[0]
    plt.figure(figsize=(10, 6))
    plt.barh(features, coef)
    plt.xlabel('Coeficiente')
    plt.title('Coeficientes del Modelo de Regresión Logística')
    plt.grid(True)
    plt.show()

    # Gráfica 3: Árbol de Decisión
    plt.figure(figsize=(14, 8))
    plot_tree(modelos[1], feature_names=X.columns, class_names=['No Crítico', 'Crítico'], filled=True)
    plt.title('Estructura del Árbol de Decisión')
    plt.show()

    # Gráfica 4: Importancia de variables en Random Forest
    importancias = modelos[2].feature_importances_
    plt.figure(figsize=(10, 6))
    plt.barh(features, importancias)
    plt.xlabel('Importancia')
    plt.title('Importancia de Variables - Random Forest')
    plt.grid(True)
    plt.show()


## PREPROCESAMIENTO DE DATOS ##
path = 'datos/data_clasified.json'
with open(path, 'r') as f:
    data = json.load(f)

tickets = data['tickets_emitidos']

df = fromTickets_to_Df(tickets)
X = df.drop('es_critico', axis=1)
y = pd.DataFrame(df['es_critico'])

# 49 elementos en total. Dividimos 25 para train y 24 para test
corte = 25
X_train = X.values[:corte]
X_test = X.values[corte:len(X)]
y_train = y[:corte]
y_test = y[corte:len(y)]

## Crear modelos ##
modelos, names = loadModels()

# Entrenamos los modelos
predicciones = []
for model in modelos:
    model.fit(X_train, y_train)
    try:
        print(f'Coeficientes: {model.coef_}')
        print(f'Sesgo: {model.intercept_}')
    except AttributeError:
        print(f'Importancia de variables: {model.feature_importances_}')
    y_pred = model.predict(X_test)
    print("Mean squared error: %.2f" % mean_squared_error(y_test, y_pred))
    predicciones.append(y_pred)

# Graficamos
# Definimos eje X: Número de ticket emitido
ejeX = range(corte, len(X))
graficar(ejeX, y_test, modelos, predicciones)

