import sqlite3
import pandas as pd
import numpy as np

def calcular_estadisticas(db_path):
    conn = sqlite3.connect(db_path)
    df_tickets = pd.read_sql_query("SELECT * FROM tickets_emitidos", conn)
    df_contactos = pd.read_sql_query("SELECT * FROM contactos_con_empleados", conn)
    conn.close()

    # Cálculo de estadísticas
    num_muestras_totales = len(df_tickets)

    # Incidentes con satisfacción >= 5
    df_satisfechos = df_tickets[df_tickets['satisfaccion_cliente'] >= 5]
    media_satisfechos = df_satisfechos['satisfaccion_cliente'].mean()
    desv_satisfechos = df_satisfechos['satisfaccion_cliente'].std()

    # Incidentes por cliente
    incidentes_por_cliente = df_tickets.groupby("cliente").size()
    media_incidentes_cliente = incidentes_por_cliente.mean()
    desv_incidentes_cliente = incidentes_por_cliente.std()

    # Horas totales por incidente
    horas_por_incidente = df_contactos.groupby("id_ticket")["tiempo"].sum()
    media_horas_incidente = horas_por_incidente.mean()
    desv_horas_incidente = horas_por_incidente.std()

    # Valores mínimo y máximo
    min_horas = horas_por_incidente.min()
    max_horas = horas_por_incidente.max()

    # Tiempo entre apertura y cierre de incidentes
    df_tickets["tiempo_resolucion"] = pd.to_datetime(df_tickets["fecha_cierre"]) - pd.to_datetime(df_tickets["fecha_apertura"])
    min_tiempo_resolucion = df_tickets["tiempo_resolucion"].min()
    max_tiempo_resolucion = df_tickets["tiempo_resolucion"].max()

    # Incidentes por empleado
    incidentes_por_empleado = df_contactos.groupby("id_emp").size()
    min_incidentes_empleado = incidentes_por_empleado.min()
    max_incidentes_empleado = incidentes_por_empleado.max()

    # Resultados
    resultados = {
        "num_muestras": num_muestras_totales,
        "media_satisfechos": media_satisfechos,
        "desv_satisfechos": desv_satisfechos,
        "media_incidentes_cliente": media_incidentes_cliente,
        "desv_incidentes_cliente": desv_incidentes_cliente,
        "media_horas_incidente": media_horas_incidente,
        "desv_horas_incidente": desv_horas_incidente,
        "min_horas": min_horas,
        "max_horas": max_horas,
        "min_tiempo_resolucion": min_tiempo_resolucion,
        "max_tiempo_resolucion": max_tiempo_resolucion,
        "min_incidentes_empleado": min_incidentes_empleado,
        "max_incidentes_empleado": max_incidentes_empleado
    }

    # Mostrar resultados por consola
    print("=== Resultados del Ejercicio 2 ===")
    for key, value in resultados.items():
        print(f"{key}: {value}")

    return resultados
