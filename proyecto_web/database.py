import mysql.connector


#CONEXIÓN
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="J@seD@vid240421",
        database="unitecnar_extensiones"
    )


#LOGIN
def login(correo, password):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM usuarios WHERE correo=%s AND password=%s",
        (correo, password)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user


#CREAR USUARIO
def crear_usuario(nombre, correo, password, rol="usuario"):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO usuarios (nombre, correo, password, rol) VALUES (%s, %s, %s, %s)",
        (nombre, correo, password, rol)
    )

    conn.commit()
    cursor.close()
    conn.close()


#USUARIOS
def obtener_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def eliminar_usuario(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

def obtener_usuario_por_correo(correo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE correo=%s", (correo,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def actualizar_perfil(id, nombre, password=None):
    conn = conectar()
    cursor = conn.cursor()

    if password:
        cursor.execute(
            "UPDATE usuarios SET nombre=%s, password=%s WHERE id=%s",
            (nombre, password, id)
        )
    else:
        cursor.execute(
            "UPDATE usuarios SET nombre=%s WHERE id=%s",
            (nombre, id)
        )

    conn.commit()
    cursor.close()
    conn.close()

def verificar_password(id, password):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM usuarios WHERE id=%s AND password=%s",
        (id, password)
    )

    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return user


# 📋 ACTIVIDADES
def crear_actividad(data):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO actividades
(nombre, descripcion, tipologia, modalidad, programa, fecha, participantes, horas, facultad, carrera)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, data)

    conn.commit()
    cursor.close()
    conn.close()

def obtener_actividades():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM actividades ORDER BY id DESC")
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data

def eliminar_actividad(id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM actividades WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    conn.close()


#BÚSQUEDA
def buscar_actividades(filtro):
    conn = conectar()
    cursor = conn.cursor()

    query = "SELECT * FROM actividades WHERE 1=1"
    params = []

    if filtro.get("texto"):
        query += " AND nombre LIKE %s"
        params.append(f"%{filtro['texto']}%")

    if filtro.get("tipologia"):
        query += " AND tipologia=%s"
        params.append(filtro["tipologia"])

    if filtro.get("modalidad"):
        query += " AND modalidad=%s"
        params.append(filtro["modalidad"])

    if filtro.get("programa"):
        query += " AND programa=%s"
        params.append(filtro["programa"])

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data


#HISTORIAL
def guardar_historial(accion, descripcion, usuario="Admin"):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO historial (accion, descripcion, usuario) VALUES (%s, %s, %s)",
        (accion, descripcion, usuario)
    )

    conn.commit()
    cursor.close()
    conn.close()

def obtener_historial():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM historial ORDER BY fecha DESC")
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data