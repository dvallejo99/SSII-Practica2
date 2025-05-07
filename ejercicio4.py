import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

def generar_graficos(db_path, image_folder):
    conn = sqlite3.connect(db_path)
    df_tickets = pd.read_sql_query("SELECT * FROM tickets_emitidos", conn)
    df_contactos = pd.read_sql_query("SELECT * FROM contactos_con_empleados", conn)
    conn.close()

    # Convertir fechas a datetime
    df_tickets['fecha_apertura'] = pd.to_datetime(df_tickets['fecha_apertura'], errors='coerce')
    df_tickets['fecha_cierre'] = pd.to_datetime(df_tickets['fecha_cierre'], errors='coerce')
    df_tickets['tiempo_resolucion'] = (df_tickets['fecha_cierre'] - df_tickets['fecha_apertura']).dt.total_seconds() / 3600

    # Media de tiempo de resolución por tipo de mantenimiento
    if 'es_mantenimiento' in df_tickets.columns:
        df_tickets['es_mantenimiento'] = df_tickets['es_mantenimiento'].astype(int)
        media_tiempo_mantenimiento = df_tickets.groupby('es_mantenimiento')['tiempo_resolucion'].mean()
        print("=== Media de tiempo de resolución por tipo de mantenimiento ===")
        print(media_tiempo_mantenimiento)

        plt.figure(figsize=(8, 6))
        media_tiempo_mantenimiento.plot(kind='bar', color=['blue', 'orange'])
        plt.title("Media de tiempo de resolución por tipo de mantenimiento")
        plt.xlabel("Tipo de Mantenimiento (0: No, 1: Sí)")
        plt.ylabel("Media de tiempo de resolución (horas)")
        plt.xticks([0, 1], ['No Mantenimiento', 'Mantenimiento'], rotation=0)
        plt.grid(axis='y')
        plt.savefig(os.path.join(image_folder, 'media_tiempo_mantenimiento.png'))
        plt.close()

    # Boxplot de tiempos de resolución por tipo de incidente
    if 'tipo_incidencia' in df_tickets.columns:
        print("=== Boxplot de tiempos de resolución por tipo de incidente ===")
        print(df_tickets.groupby('tipo_incidencia')['tiempo_resolucion'].describe())

        plt.figure(figsize=(10, 6))
        df_tickets.boxplot(column='tiempo_resolucion', by='tipo_incidencia', showfliers=False, whis=[5, 95])
        plt.title("Distribución de tiempos de resolución por tipo de incidente")
        plt.suptitle("")
        plt.ylabel("Horas")
        plt.xlabel("Tipo de Incidente")
        plt.grid()
        plt.savefig(os.path.join(image_folder, 'boxplot_tiempos_resolucion.png'))
        plt.close()

    # Top 5 clientes más críticos
    if 'es_mantenimiento' in df_tickets.columns and 'tipo_incidencia' in df_tickets.columns and 'cliente' in df_tickets.columns:
        clientes_criticos = df_tickets[(df_tickets['es_mantenimiento'] == 1) & (df_tickets['tipo_incidencia'] != 1)]
        clientes_top = clientes_criticos['cliente'].value_counts().nlargest(5)
        print("=== Top 5 clientes más críticos ===")
        print(clientes_top)

        plt.figure(figsize=(10, 6))
        clientes_top.plot(kind='bar', color='red')
        plt.title("Top 5 Clientes Críticos")
        plt.xlabel("Cliente")
        plt.ylabel("Número de Incidentes")
        plt.xticks(rotation=45)
        plt.grid()
        plt.savefig(os.path.join(image_folder, 'top_clientes_criticos.png'))
        plt.close()

    # Número total de actuaciones por empleado
    if 'id_emp' in df_contactos.columns:
        actuaciones_por_empleado = df_contactos['id_emp'].value_counts()
        print("=== Número total de actuaciones por empleado ===")
        print(actuaciones_por_empleado)

        plt.figure(figsize=(10, 6))
        actuaciones_por_empleado.plot(kind='bar', color='blue')
        plt.title("Número total de actuaciones por empleado")
        plt.xlabel("Empleado")
        plt.ylabel("Número de Actuaciones")
        plt.xticks(rotation=45)
        plt.grid()
        plt.savefig(os.path.join(image_folder, 'actuaciones_por_empleado.png'))
        plt.close()

    # Total de actuaciones por día de la semana
    if 'fecha' in df_contactos.columns:
        df_contactos['fecha'] = pd.to_datetime(df_contactos['fecha'], errors='coerce')
        df_contactos['dia_semana'] = df_contactos['fecha'].dt.day_name()
        actuaciones_por_dia = df_contactos['dia_semana'].value_counts()
        print("=== Total de actuaciones por día de la semana ===")
        print(actuaciones_por_dia)

        plt.figure(figsize=(10, 6))
        actuaciones_por_dia.plot(kind='bar', color='green')
        plt.title("Total de actuaciones por día de la semana")
        plt.xlabel("Día de la Semana")
        plt.ylabel("Número de Actuaciones")
        plt.xticks(rotation=45)
        plt.grid()
        plt.savefig(os.path.join(image_folder, 'actuaciones_por_dia_semana.png'))
        plt.close()