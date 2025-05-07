import sqlite3

DB_PATH = "incidencias.db"

def get_top_clientes(x):
    query = """
        SELECT c.nombre, COUNT(*) AS total
        FROM tickets_emitidos t
        JOIN clientes c ON t.cliente = c.id_cli
        GROUP BY c.nombre
        ORDER BY total DESC
        LIMIT ?;
    """
    return _fetch_query(query, (x,))

def get_top_tipos(x):
    query = """
        SELECT ti.nombre, AVG(JULIANDAY(fecha_cierre) - JULIANDAY(fecha_apertura)) AS avg_dias
        FROM tickets_emitidos t
        JOIN tipos_incidentes ti ON t.tipo_incidencia = ti.id_inci
        GROUP BY ti.nombre
        ORDER BY avg_dias DESC
        LIMIT ?;
    """
    return _fetch_query(query, (x,))

def get_top_empleados(x):
    query = """
        SELECT e.nombre, SUM(cce.tiempo) AS total_horas
        FROM contactos_con_empleados cce
        JOIN empleados e ON cce.id_emp = e.id_emp
        GROUP BY e.nombre
        ORDER BY total_horas DESC
        LIMIT ?;
    """
    return _fetch_query(query, (x,))

def _fetch_query(query, params):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    conn.close()
    return resultados
