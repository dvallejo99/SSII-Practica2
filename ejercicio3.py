import json
import pandas as pd
from datetime import datetime

def calcular_estadisticas(db_path):

    # Cargar el archivo JSON
    file_path = "datos/datos.json"
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Extraer los incidentes y tipos de incidentes
    tipos_incidentes = {tipo["id_inci"]: tipo["nombre"] for tipo in data["tipos_incidentes"]}
    incidentes = data["tickets_emitidos"]

    # Filtrar solo los incidentes de tipo "Fraude" (id_inci = 5)
    fraude_incidentes = [inci for inci in incidentes if inci["tipo_incidencia"] == 5]

    # Crear lista con la información estructurada
    fraude_data = []
    for inci in fraude_incidentes:
        for contacto in inci["contactos_con_empleados"]:
            fecha_contacto = datetime.strptime(contacto["fecha"], "%Y-%m-%d")
            fraude_data.append({
                "empleado_id": contacto["id_emp"],
                "cliente": inci["cliente"],
                "fecha": fecha_contacto,
                "dia_semana": fecha_contacto.strftime("%A"),
                "tipo_incidencia": tipos_incidentes[str(inci["tipo_incidencia"])],
                "tiempo_contacto": contacto["tiempo"]
            })

    # Convertir a DataFrame
    df_fraude = pd.DataFrame(fraude_data)

    # Orden correcto de los días de la semana
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Número de incidentes por agrupación
    incidentes_por_empleado = df_fraude.groupby("empleado_id")["tipo_incidencia"].count()
    incidentes_por_cliente = df_fraude.groupby("cliente")["tipo_incidencia"].count()
    incidentes_por_dia_semana = df_fraude.groupby("dia_semana")["tipo_incidencia"].count().reindex(days_order).fillna(0)


    # Número de actuaciones realizadas por los empleados en estos incidentes
    actuaciones_por_empleado = df_fraude.groupby("empleado_id")["tiempo_contacto"].count()

    # Análisis estadístico del tiempo de contacto
    analisis_estadistico = df_fraude["tiempo_contacto"].agg(["median", "mean", "var", "max", "min"])

    # Resultados (corrección de indentación)
    resultados = {
        "Número de incidentes por empleado": incidentes_por_empleado,
        "Número de incidentes por cliente": incidentes_por_cliente,
        "Número de incidentes por día de la semana": incidentes_por_dia_semana,
        "Número de actuaciones por empleado": actuaciones_por_empleado,
        "Análisis estadístico del tiempo de contacto": analisis_estadistico
    }

    # Mostrar resultados por consola
    print("=== Resultados del Ejercicio 3 ===")
    for key, value in resultados.items():
        print(f"{key}: {value}")

    return resultados

