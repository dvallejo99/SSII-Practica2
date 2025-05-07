import json
import sqlite3

# Cargar datos desde el archivo JSON
with open("datos/datos.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Conectar a la base de datos SQLite
db_name = "incidencias.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Crear tablas
cursor.executescript('''
CREATE TABLE IF NOT EXISTS clientes (
    id_cli INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    telefono TEXT NOT NULL,
    provincia TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS empleados (
    id_emp INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    nivel INTEGER NOT NULL,
    fecha_contrato TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tipos_incidentes (
    id_inci INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tickets_emitidos (
    id_ticket INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente INTEGER NOT NULL,
    fecha_apertura TEXT NOT NULL,
    fecha_cierre TEXT NOT NULL,
    es_mantenimiento BOOLEAN NOT NULL,
    satisfaccion_cliente INTEGER NOT NULL,
    tipo_incidencia INTEGER NOT NULL,
    FOREIGN KEY (cliente) REFERENCES clientes(id_cli),
    FOREIGN KEY (tipo_incidencia) REFERENCES tipos_incidentes(id_inci)
);

CREATE TABLE IF NOT EXISTS contactos_con_empleados (
    id_contacto INTEGER PRIMARY KEY AUTOINCREMENT,
    id_ticket INTEGER NOT NULL,
    id_emp INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    tiempo REAL NOT NULL,
    FOREIGN KEY (id_ticket) REFERENCES tickets_emitidos(id_ticket),
    FOREIGN KEY (id_emp) REFERENCES empleados(id_emp)
);
''')


# Insertar datos en las tablas
def insert_data(table, columns, values):
    placeholders = ', '.join(['?' for _ in values[0]])
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    cursor.executemany(query, values)


# Insertar clientes
clientes_data = [(c["id_cli"], c["nombre"], c["telefono"], c["provincia"]) for c in data["clientes"]]
insert_data("clientes", ["id_cli", "nombre", "telefono", "provincia"], clientes_data)

# Insertar empleados
empleados_data = [(e["id_emp"], e["nombre"], e["nivel"], e["fecha_contrato"]) for e in data["empleados"]]
insert_data("empleados", ["id_emp", "nombre", "nivel", "fecha_contrato"], empleados_data)

# Insertar tipos de incidentes
tipos_incidentes_data = [(t["id_inci"], t["nombre"]) for t in data["tipos_incidentes"]]
insert_data("tipos_incidentes", ["id_inci", "nombre"], tipos_incidentes_data)

# Insertar tickets emitidos
ticket_values = []
contacto_values = []
fecha_cierre = None
for ticket in data["tickets_emitidos"]:
    for contacto in ticket["contactos_con_empleados"]:
        fecha_cierre = contacto["fecha"]
        contacto_values.append((len(ticket_values), contacto["id_emp"], contacto["fecha"], contacto["tiempo"]))

    ticket_values.append((ticket["cliente"], ticket["fecha_apertura"], fecha_cierre,
                          ticket["es_mantenimiento"], ticket["satisfaccion_cliente"], ticket["tipo_incidencia"]))


insert_data("tickets_emitidos",
            ["cliente", "fecha_apertura", "fecha_cierre", "es_mantenimiento", "satisfaccion_cliente",
             "tipo_incidencia"], ticket_values)
insert_data("contactos_con_empleados", ["id_ticket", "id_emp", "fecha", "tiempo"], contacto_values)

# Guardar y cerrar conexión
conn.commit()
conn.close()

print(f"Base de datos '{db_name}' creada y datos insertados exitosamente.")



