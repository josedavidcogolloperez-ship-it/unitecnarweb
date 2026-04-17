from flask import Flask, render_template, request, redirect, url_for, session, send_file
from database import *
import pandas as pd
from openai import OpenAI

#IA
client = OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
)

app = Flask(__name__)
app.secret_key = "clave_segura_123"



# LOGIN
@app.route("/", methods=["GET", "POST"])
def login_view():
    if request.method == "POST":
        correo = request.form.get("correo")
        password = request.form.get("password")

        user = login(correo, password)

        if user:
            session["user"] = user[2]
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")



# REGISTRO
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        crear_usuario(
            request.form.get("nombre"),
            request.form.get("correo"),
            request.form.get("password"),
            "usuario"
        )
        return redirect("/")

    return render_template("registro.html")



# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



#DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    actividades = obtener_actividades()

    total = len(actividades)
    participantes = sum(int(a[7]) for a in actividades if a[7])
    horas = sum(int(a[8]) for a in actividades if a[8])

    recientes = actividades[::-1][:5]

    return render_template(
        "dashboard.html",
        total=total,
        participantes=participantes,
        horas=horas,
        recientes=recientes
    )



# ACTIVIDADES
@app.route("/actividades")
def actividades():
    if "user" not in session:
        return redirect("/")

    data = obtener_actividades()
    return render_template("actividades.html", data=data)

@app.route("/eliminar_actividad/<int:id>", methods=["POST"])
def eliminar_actividad_route(id):
    eliminar_actividad(id)

    guardar_historial(
        "Eliminación",
        f"Actividad eliminada ID {id}",
        session["user"]
    )

    return redirect("/actividades")    

    



#NUEVA ACTIVIDAD
@app.route("/nueva", methods=["GET", "POST"])
def nueva():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        data = (
    request.form.get("nombre"),
    request.form.get("descripcion"),
    request.form.get("tipologia"),
    request.form.get("modalidad"),
    request.form.get("programa"),
    request.form.get("fecha"),
    request.form.get("participantes"),
    request.form.get("horas"),
    request.form.get("facultad"),
    request.form.get("programa")  # carrera = programa seleccionado
    )

        crear_actividad(data)

        guardar_historial(
            "Creación",
            "Nueva actividad registrada",
            session["user"]
        )

        return redirect("/actividades")

    return render_template("nueva_actividad.html")



#BÚSQUEDA
@app.route("/busqueda", methods=["GET", "POST"])
def busqueda():
    if "user" not in session:
        return redirect("/")

    resultados = []

    if request.method == "POST":
        filtro = {
            "texto": request.form.get("texto"),
            "tipologia": request.form.get("tipologia"),
            "modalidad": request.form.get("modalidad"),
            "programa": request.form.get("programa")
        }

        resultados = buscar_actividades(filtro)

    return render_template("busqueda.html", resultados=resultados)



#REPORTES
@app.route("/reportes", methods=["GET", "POST"])
def reportes():
    if "user" not in session:
        return redirect("/")

    datos = []

    if request.method == "POST":
        tipo = request.form.get("tipo")
        data = obtener_actividades()

        if tipo == "tipologia":
            datos = sorted(data, key=lambda x: x[3])
        elif tipo == "programa":
            datos = sorted(data, key=lambda x: x[5])
        else:
            datos = data

    return render_template("reportes.html", datos=datos)



#EXPORTAR EXCEL
@app.route("/exportar")
def exportar():
    if "user" not in session:
        return redirect("/")

    data = obtener_actividades()

    import xlsxwriter
    from collections import Counter

    archivo = "reporte.xlsx"
    workbook = xlsxwriter.Workbook(archivo)
    ws = workbook.add_worksheet("Dashboard")

    
    # TAMAÑO COLUMNAS
    ws.set_column('B:B', 2)
    ws.set_column('C:G', 25)
    ws.set_column('H:H', 5)

    
    #FORMATOS
    titulo = workbook.add_format({
        'bold': True,
        'font_size': 18,
        'align': 'center',
        'font_color': '#1F2937'
    })

    card1 = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#3B82F6',
        'font_color': 'white',
        'border': 1
    })

    card2 = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#10B981',
        'font_color': 'white',
        'border': 1
    })

    card3 = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#F59E0B',
        'font_color': 'white',
        'border': 1
    })

    header = workbook.add_format({
        'bold': True,
        'bg_color': '#2563EB',
        'font_color': 'white',
        'align': 'center',
        'border': 1
    })

    cell = workbook.add_format({
        'border': 1,
        'align': 'center',
        'text_wrap': True
    })

    
    #TITULO
    ws.merge_range('C2:G3', '📊 DASHBOARD DE ACTIVIDADES', titulo)

    
    #KPIs
    total = len(data)
    participantes = sum(int(a[7]) for a in data if a[7])
    horas = sum(int(a[8]) for a in data if a[8])

    ws.merge_range('C5:D7', f"TOTAL:\n{total:}", card1)
    ws.merge_range('E5:F7', f"PARTICIPANTES:\n{participantes:}", card2)
    ws.merge_range('G5:G7', f"HORAS:\n{horas:}", card3)

    
    #TABLA
    headers = ["Nombre", "Tipología", "Programa", "Fecha", "Participantes"]

    fila = 10

    for col, h in enumerate(headers):
        ws.write(fila, col + 2, h, header)

    for i, a in enumerate(data):
        ws.write(fila + 1 + i, 2, a[1], cell)
        ws.write(fila + 1 + i, 3, a[3], cell)
        ws.write(fila + 1 + i, 4, a[5], cell)
        ws.write(fila + 1 + i, 5, str(a[6]), cell)
        ws.write(fila + 1 + i, 6, a[7], cell)

   
    #GRÁFICA DE BARRAS
    chart = workbook.add_chart({'type': 'column'})

    chart.add_series({
        'name': 'Participantes',
        'categories': ['Dashboard', fila + 1, 2, fila + len(data), 2],
        'values':     ['Dashboard', fila + 1, 6, fila + len(data), 6],
        'fill': {'color': '#3B82F6'}
    })

    chart.set_title({'name': 'Participantes por Actividad'})

    ws.insert_chart('C20', chart)

   
    #GRÁFICA DE TORTA (TIPOLOGÍA)
    tipologias = [a[3] for a in data if a[3]]
    conteo = Counter(tipologias)

    fila_pie = fila + len(data) + 5

    ws.write(fila_pie, 2, "Tipología")
    ws.write(fila_pie, 3, "Cantidad")

    for i, (k, v) in enumerate(conteo.items()):
        ws.write(fila_pie + 1 + i, 2, k)
        ws.write(fila_pie + 1 + i, 3, v)

    pie = workbook.add_chart({'type': 'pie'})

    pie.add_series({
        'name': 'Distribución por Tipología',
        'categories': ['Dashboard', fila_pie + 1, 2, fila_pie + len(conteo), 2],
        'values':     ['Dashboard', fila_pie + 1, 3, fila_pie + len(conteo), 3],
    })

    pie.set_title({'name': 'Actividades por Tipología'})

    ws.insert_chart('H20', pie)

    workbook.close()

    return send_file(archivo, as_attachment=True)


#IA
@app.route("/ia", methods=["GET", "POST"])
def ia():
    if "user" not in session:
        return redirect("/")

    resultado = ""

    if request.method == "POST":
        texto = request.form.get("texto")

        try:
            respuesta = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": texto}]
            )
            resultado = respuesta.choices[0].message.content
        except:
            resultado = "⚠️ Error con IA"

    return render_template("ia.html", resultado=resultado)



#HISTORIAL
@app.route("/historial")
def historial():
    if "user" not in session:
        return redirect("/")

    datos = obtener_historial()
    return render_template("historial.html", datos=datos)


#USUARIOS
@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        nombre = request.form.get("nombre")
        correo = request.form.get("correo")
        password = request.form.get("password")
        rol = request.form.get("rol")

        crear_usuario(nombre, correo, password, rol)

        guardar_historial(
            "Creación",
            f"Usuario {nombre} creado",
            session["user"]
        )

        return redirect("/usuarios")

    data = obtener_usuarios()
    return render_template("usuarios.html", data=data)

#ELIMINAR USUARIO
@app.route("/eliminar_usuario/<int:id>")
def eliminar_user(id):
    eliminar_usuario(id)

    guardar_historial(
        "Eliminación",
        f"Usuario eliminado ID {id}",
        session["user"]
    )

    return redirect("/usuarios")


#CONFIGURACIÓN
@app.route("/configuracion", methods=["GET", "POST"])
def configuracion():
    if "user" not in session:
        return redirect("/")

    usuario = obtener_usuario_por_correo(session["user"])
    mensaje = ""

    if request.method == "POST":
        nombre = request.form.get("nombre")
        actual = request.form.get("actual")
        nueva = request.form.get("nueva")

        if nueva:
            if not verificar_password(usuario[0], actual):
                mensaje = "❌ Contraseña incorrecta"
            else:
                actualizar_perfil(usuario[0], nombre, nueva)
                mensaje = "✅ Contraseña actualizada"
        else:
            actualizar_perfil(usuario[0], nombre)
            mensaje = "✅ Perfil actualizado"

    return render_template("configuracion.html", usuario=usuario, mensaje=mensaje)     



#RUN
if __name__ == "__main__":
    app.run(debug=True)