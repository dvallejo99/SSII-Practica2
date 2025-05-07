
import os

import requests

import ejercicio2
import ejercicio3
import ejercicio4
from flask import Flask, render_template, request
from queries import get_top_clientes, get_top_tipos, get_top_empleados
app = Flask(__name__)

db_path = "incidencias.db"
image_folder = "static/images"
os.makedirs(image_folder, exist_ok=True)

@app.route('/')
def index():
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