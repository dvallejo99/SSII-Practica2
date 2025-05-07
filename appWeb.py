from flask import Flask, render_template
import os
import ejercicio2
import ejercicio3
import ejercicio4

app = Flask(__name__)

db_path = "incidencias.db"
image_folder = "static/images"
os.makedirs(image_folder, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

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