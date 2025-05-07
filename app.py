from flask import Flask, render_template, request
from queries import get_top_clientes, get_top_tipos, get_top_empleados

app = Flask(__name__)

@app.route('/')
def index():
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

if __name__ == "__main__":
    app.run(debug=True)

import requests

@app.route('/vulnerabilidades')
def vulnerabilidades():
    try:
        response = requests.get("https://cve.circl.lu/api/last", timeout=10)
        response.raise_for_status()
        datos = response.json()[:10]  # Solo los últimos 10
        vulnerabilidades = [
            {
                "id": v.get("id"),
                "summary": v.get("summary"),
                "cvss": v.get("cvss"),
                "published": v.get("Published")
            }
            for v in datos
        ]
    except Exception as e:
        vulnerabilidades = []
        print("Error al obtener vulnerabilidades:", e)

    return render_template("vulnerabilidades.html", vulnerabilidades=vulnerabilidades)
