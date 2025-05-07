from flask import Flask, render_template, request, redirect, url_for,send_file
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import matplotlib.pyplot as plt
import os
import sqlite3
import requests
import ejercicio2
import ejercicio3
import ejercicio4
from queries import get_top_clientes, get_top_tipos, get_top_empleados


app = Flask(__name__)

db_path = "incidencias.db"
image_folder = "static/images"
os.makedirs(image_folder, exist_ok=True)

# Función para validar usuario
def validar_usuario(nombre, contrasena):
    if nombre == 'admin' and contrasena == 'admin':
        return True

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE nombre = ? AND id_emp = ?", (nombre, contrasena))
    usuario = cursor.fetchone()
    conn.close()
    return usuario is not None

# Redirige al login al entrar por primera vez
@app.route('/')
def index():
    return redirect(url_for('login'))

# Login simple sin sesiones
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['username']
        contrasena = request.form['password']
        if validar_usuario(nombre, contrasena):
            return redirect(url_for('inicio'))
        else:
            return render_template('login.html', error="Credenciales incorrectas")
    return render_template('login.html')

# Página principal después de hacer login
@app.route('/inicio')
def inicio():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    x = request.args.get('x', default=5, type=int)
    modo = request.args.get('modo', default='clientes')

    if modo == 'clientes':
        resultados = get_top_clientes(x)
        titulo = f"Top {x} clientes con más incidencias"
    elif modo == 'tipos':
        resultados = get_top_tipos(x)
        titulo = f"Top {x} tipos de incidencia con más tiempo de resolución"
    elif modo == 'empleados':
        resultados = get_top_empleados(x)
        titulo = f"Top {x} empleados que más tiempo han empleado"
    else:
        resultados = []
        titulo = "Sin resultados"

    return render_template('dashboard.html', titulo=titulo, resultados=resultados)

@app.route('/vulnerabilidades')
def vulnerabilidades():
    try:
        response = requests.get("https://cve.circl.lu/api/last", timeout=10)
        response.raise_for_status()
        datos = response.json()[:10]  # Solo los últimos 10
        cvul = [
            {
                "id": v.get("id") or "Sin ID",
                "summary": v.get("summary") or "No disponible",
                "cvss": v.get("cvss") if v.get("cvss") is not None else "N/A",
                "published": v.get("Published") or "Sin fecha"
            }
            for v in datos
        ]

    except Exception as e:
        cvul = []
        print("Error al obtener vulnerabilidades:", e)

    return render_template("vulnerabilidades.html", vulnerabilidades=cvul)


@app.route('/generar_informe')
def generar_informe():
    # Crear carpeta de gráficos si no existe
    if not os.path.exists("graficos"):
        os.makedirs("graficos")

    # Conexión y lectura
    conn = sqlite3.connect("incidencias.db")
    clientes_df = pd.read_sql_query("SELECT * FROM clientes", conn)
    empleados_df = pd.read_sql_query("SELECT * FROM empleados", conn)
    tipos_df = pd.read_sql_query("SELECT * FROM tipos_incidentes", conn)
    tickets_df = pd.read_sql_query("SELECT * FROM tickets_emitidos", conn)
    contactos_df = pd.read_sql_query("SELECT * FROM contactos_con_empleados", conn)
    conn.close()

    # Generar gráficos
    incidencias_count = tickets_df["tipo_incidencia"].value_counts().reset_index()
    incidencias_count.columns = ["tipo", "cantidad"]
    plt.figure(figsize=(6, 4))
    plt.bar(incidencias_count["tipo"], incidencias_count["cantidad"])
    plt.tight_layout()
    plt.savefig("graficos/incidencias_tipo.png")
    plt.close()

    plt.figure(figsize=(6, 4))
    tickets_df["satisfaccion_cliente"].hist(bins=5)
    plt.tight_layout()
    plt.savefig("graficos/satisfaccion.png")
    plt.close()

    tiempo_por_empleado = contactos_df.groupby("id_emp")["tiempo"].sum().reset_index()
    tiempo_por_empleado = pd.merge(tiempo_por_empleado, empleados_df, on="id_emp")
    plt.figure(figsize=(6, 4))
    plt.bar(tiempo_por_empleado["nombre"], tiempo_por_empleado["tiempo"])
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("graficos/tiempo_empleados.png")
    plt.close()

    # Generar PDF
    doc = SimpleDocTemplate("static/informe_completo.pdf", pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph("Informe de Actividad - Empresa de Ciberseguridad", styles["Title"]),
             Spacer(1, 12)]

    # Clientes
    story.append(Paragraph("Clientes", styles["Heading2"]))
    tabla_clientes = [clientes_df.columns.tolist()] + clientes_df.values.tolist()
    t = Table(tabla_clientes)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.gray),
                           ("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Gráficos
    story.append(Paragraph("Incidencias por Tipo", styles["Heading2"]))
    story.append(Image("graficos/incidencias_tipo.png", width=400, height=300))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Satisfacción de Clientes", styles["Heading2"]))
    story.append(Image("graficos/satisfaccion.png", width=400, height=300))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Tiempo por Empleado", styles["Heading2"]))
    story.append(Image("graficos/tiempo_empleados.png", width=400, height=300))

    # Guardar
    doc.build(story)

    # Descargar
    return send_file("static/informe_completo.pdf", as_attachment=True)

#practica1

@app.route('/ej1')
def ej1():
    return render_template('ej1.html')

@app.route('/ej2')
def ej2():
    resultados = ejercicio2.calcular_estadisticas(db_path)
    return render_template('ej2.html', **resultados)

@app.route('/ej3')
def ej3():
    resultados = ejercicio3.calcular_estadisticas(db_path)
    return render_template('ej3.html', resultados=resultados)


@app.route('/ej4')
def ej4():
    ejercicio4.generar_graficos(db_path, image_folder)
    return render_template('ej4.html')

if __name__ == '__main__':
    app.run(debug=True)