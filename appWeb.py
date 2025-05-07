from flask import Flask, render_template, request, redirect, url_for
from flask import send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
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
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "Informe de Análisis de Incidentes")

    # Sección de estadísticas básicas (puedes modificarlo según lo que quieras mostrar)
    c.setFont("Helvetica", 12)
    y = height - 100
    top_clientes = get_top_clientes(5)
    c.drawString(100, y, "Top 5 Clientes con más incidencias:")
    y -= 20
    for cliente, cantidad in top_clientes:
        c.drawString(120, y, f"{cliente}: {cantidad} incidencias")
        y -= 20

    y -= 20
    top_empleados = get_top_empleados(5)
    c.drawString(100, y, "Top 5 Empleados con más tiempo invertido:")
    y -= 20
    for empleado, tiempo in top_empleados:
        c.drawString(120, y, f"{empleado}: {tiempo:.2f} horas")
        y -= 20

    c.showPage()
    c.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="informe.pdf", mimetype='application/pdf')




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