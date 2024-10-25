from flask import Flask, request, jsonify, session, make_response
import sqlite3
from flask_cors import CORS
from sqlite3 import Error



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})


#############################################
# Funciones para la base de datos
#############################################

def create_db():
    try:
        conn = sqlite3.connect('mibasededatos.db')
        cursor = conn.cursor()


        # Crear tabla de usuarios_empresa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios_empresa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT NOT NULL UNIQUE,
                rol TEXT NOT NULL,
                contraseña TEXT NOT NULL,
                nombre_empresa TEXT NOT NULL,
                url_img TEXT NULL,
                codigo TEXT NULL
            )
        ''')


        # Crear tabla de trabajadores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trabajadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT NOT NULL UNIQUE,
                contraseña TEXT NOT NULL,
                rol TEXT NOT NULL,
                url_img TEXT NULL,
                emailEmpresa TEXT NOT NULL
            )
        ''')

        
        # Crear tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT NOT NULL UNIQUE,
                contraseña TEXT NOT NULL,
                rol TEXT NOT NULL
            )
        ''')
        

        # Crear tabla de horarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS horarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                correo TEXT NOT NULL,
                dia TEXT NOT NULL ,
                hora TEXT NOT NULL,
                reservadoUsuario TEXT NULL,
                FOREIGN KEY (correo) REFERENCES usuarios(correo)
                       
            )
        ''')
        

     
        """
        # Crear tabla de citas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS citas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trabajador_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                descripcion TEXT,
                FOREIGN KEY (trabajador_id) REFERENCES trabajadores(id)
            )
        ''')
        """

        conn.commit()
        conn.close()
        print("Tablas creadas con éxito.")
    except Error as e:
        print(f"Error al crear las tablas: {e}")

# Crear las tablas al inicio de la aplicación
create_db()


#############################################
# Ruta de inicio para verificar que el servidor está funcionando
#############################################
@app.route('/', methods=["GET"])
def index():
    return jsonify({'message': 'Bienvenido a la API de usuarios'})


#############################################
# Rutas para autenticación
#############################################


@app.route('/login', methods=['POST'])
def iniciar_usuario():
    data = request.get_json()
    print(data)
    correo = data.get('email')
    contraseña = data.get('password')

    try:
        conn = sqlite3.connect('mibasededatos.db')
        cursor = conn.cursor()

        # Comprobar en la tabla de usuarios
        cursor.execute('''
            SELECT correo, contraseña, rol
            FROM usuarios
            WHERE correo = ?
        ''', (correo,))
        usuario = cursor.fetchone()

        # Comprobar en la tabla de trabajadores
        cursor.execute('''
            SELECT correo, contraseña, rol
            FROM trabajadores
            WHERE correo = ?
        ''', (correo,))
        trabajador = cursor.fetchone()

        # Comprobar en la tabla de administradores
        cursor.execute('''
            SELECT correo, contraseña, rol
            FROM usuarios_empresa
            WHERE correo = ?
        ''', (correo,))
        administrador = cursor.fetchone()

        conn.close()

        # Verificar credenciales y guardar en una cookie
        response = make_response()
        if usuario and usuario[1] == contraseña:
            response = make_response(jsonify({'rol': "usuario"}), 200)
            response.set_cookie('correo', correo)  # Guardar el correo en una cookie
        elif trabajador and trabajador[1] == contraseña:
            response = make_response(jsonify({'rol': "trabajador", "correo":correo}), 200)
            response.set_cookie('correo', correo)  # Guardar el correo en una cookie
        elif administrador and administrador[1] == contraseña:
            response = make_response(jsonify({'rol': "administrador"}), 200)
            response.set_cookie('correo', correo)  # Guardar el correo en una cookie
        else:
            return jsonify({'message': 'Correo o contraseña incorrectos'}), 401

        return response
    except sqlite3.Error as e:
        print(e)
        return jsonify({'message': 'Error al intentar iniciar sesión', 'error': str(e)}), 500

# Ruta para registrar usuarios
@app.route('/registro', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    nombre = data.get('username')
    correo = data.get('email')
    contraseña = data.get('password')
    rol = 'usuario'

    try:
        conn = sqlite3.connect('mibasededatos.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usuarios (nombre, correo, contraseña, rol)
            VALUES (?, ?, ?, ?)
        ''', (nombre, correo, contraseña, rol))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Usuario registrado correctamente'}), 201
    except Error as e:
        print(e)
        conn.close()
        return jsonify({'message': 'Error al intentar registrar el usuario'}), 400

# Ruta para registrar administrador
@app.route('/registroadm', methods=['POST'])
def register_admin():
    try:
        data = request.get_json()
        nombre = data['username']
        email = data['email']
        contrasena = data['password']
        rol = data['rol']
        nombre_empresa = data['nom']
        url_img = data['url_img']
        code = data['code']

        conn = sqlite3.connect('mibasededatos.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usuarios_empresa (nombre, correo, rol, contraseña, nombre_empresa, url_img, codigo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, email, rol, contrasena, nombre_empresa, url_img, code))

        conn.commit()
        conn.close()

        return jsonify({"message": "Administrador registrado con éxito"}), 201
    except Error as e:
        print(e)
        conn.close()
        return jsonify({"message": "Error al registrar al administrador"}), 400

@app.route('/registrotrabajador', methods=['POST'])
def registrar_trabajador():
    data = request.get_json()
    nombre = data.get('username') 
    correo = data.get('email')     
    contraseña = data.get('password') 
    emailEmpresa = data.get('emailEmpresa')
    url_img = data.get('url_img')
    rol = 'trabajador'

    if not nombre or not correo or not contraseña:
        return jsonify({'message': 'Faltan datos para registrar el trabajador'}), 400

    try:
        conn = sqlite3.connect('mibasededatos.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO trabajadores (nombre, correo, contraseña, rol, emailEmpresa, url_img) VALUES (?, ?, ?, ?, ?, ?)''', (nombre, correo, contraseña, rol, emailEmpresa, url_img))
        conn.commit()
        
        # Obtener el id del trabajador recién registrado
        trabajador_id = cursor.lastrowid        
        conn.close()
        return jsonify({'message': 'Trabajador registrado correctamente', 'id': trabajador_id, 'nombre': nombre}), 201
    except Error as e:
        print(e)
        conn.close()
        return jsonify({'message': 'Error al intentar registrar al trabajador', 'error': str(e)}), 400


#############################################
# Rutas para trabajadores
#############################################

# Ruta para eliminar trabajadores
@app.route('/eliminartrabajador', methods=['POST'])
def eliminar_trabajador():
    data = request.get_json()
    correo = data.get('email')
    try:
        conn = sqlite3.connect('mibasededatos.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM trabajadores WHERE correo = ?", (correo,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Trabajador eliminado correctamente'}), 200
    except Error as e:
        print(e)
        return jsonify({'message': 'Error al intentar eliminar al trabajador'}), 500

# Ruta para obtener trabajadores
@app.route('/obtenertrabajadores', methods=['POST'])
def obtener_trabajadores_empresa():
    data = request.get_json()
    emailEmpresa = data.get('emailEmpresa')
    try:
        conn = sqlite3.connect('mibasededatos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, correo, contraseña, rol, url_img FROM trabajadores WHERE emailEmpresa = ?", (emailEmpresa,))
        trabajadores = cursor.fetchall()
        conn.close()
        print(trabajadores)
        trabajadores_list = [{'username': t[0], 'email': t[1], 'contraseña': t[2], 'rol': t[3], 'url_img': t[4]} for t in trabajadores]
        print(trabajadores_list)
        return jsonify(trabajadores_list), 200
    except Error as e:
        print(e)
        conn.close()
        return jsonify({'message': 'Error al obtener los trabajadores'}), 500



#############################################
# rutas para horarios
#############################################
@app.route('/obtenerhorarios', methods=['POST'])
def obtenerhorarios():
    data = request.get_json()
    correo = data.get('correo')
    dia = data.get('dia')
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('mibasededatos.db')
        cursor = conn.cursor()

        # Consultar horarios de la tabla horarios donde coincida el correo y el día
        cursor.execute('SELECT hora, reservadoUsuario FROM horarios WHERE correo = ? AND dia = ?', (correo, dia))
        horarios = cursor.fetchall()
        conn.close()

        # Convertir los resultados a una lista de horarios
        lista_horarios = [{'hora': h[0], 'reservadoUsuario': h[1]} for h in horarios]
        return jsonify(lista_horarios), 200
    except Error as e:
        print(e)
        return jsonify({'message': 'Error al obtener los horarios', 'error': str(e)}), 400

@app.route('/horarios', methods=['POST'])
def guardar_horario():
        data = request.get_json()  # Obtener los datos enviados desde el frontend
        print(data)
        dia = data.get('dia')
        hora = data.get('hora')
        correo = data.get('correo')

        # Verificar si se recibieron todos los datos
        if not dia or not hora:
            return jsonify({'message': 'Faltan datos: día o hora'}), 400

        try:
            # Conectar con la base de datos
            conn = sqlite3.connect('mibasededatos.db')
            cursor = conn.cursor()

            # Insertar el nuevo horario en la tabla 'horarios'
            cursor.execute('''
                INSERT INTO horarios (correo, dia, hora)
                VALUES (?, ?, ?)
            ''', (correo, dia, hora))
            
            conn.commit()  # Guardar los cambios en la base de datos
            conn.close()

            return jsonify({'message': 'Horario guardado exitosamente'}), 200

        except sqlite3.Error as e:
            return jsonify({'message': 'Error al guardar el horario', 'error': str(e)}),500

@app.route('/eliminar-horario', methods=['POST'])
def eliminar_horario():
    data = request.get_json()
    correo = data.get('correo')
    dia = data.get('dia')
    hora = data.get('hora')
    print('---------------------------------')
    print(data)
    print('---------------------------------')

    if not correo or not dia or not hora:
        return jsonify({'message': 'Faltan datos: correo, día o hora'}), 400

    try:
        conn = sqlite3.connect('mibasededatos.db')
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM horarios 
            WHERE correo = ? AND dia = ? AND hora = ?
        ''', (correo, dia, hora))

        if cursor.rowcount == 0:
            return jsonify({'message': 'No se encontró el horario para eliminar'}), 404

        conn.commit()
        conn.close()
        return jsonify({'message': 'Horario eliminado correctamente'}), 200
    except Error as e:
        print(e)
        return jsonify({'message': 'Error al intentar eliminar el horario', 'error': str(e)}), 500




#############################################
# Rutas para obtener información de la empresa
#############################################

@app.route('/obtener-empresas', methods=['GET'])
def obtener_empresas():
    try:
        conn = sqlite3.connect('mibasededatos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre_empresa, url_img, correo FROM usuarios_empresa")
        empresas = cursor.fetchall()
        conn.close()

        empresas_list = [{'id': e[0], 'nombre_empresa': e[1], 'url_img': e[2], 'correo': e[3]} for e in empresas]

        return jsonify(empresas_list), 200
    except Error as e:
        print(e)
        return jsonify({'message': 'Error al obtener las empresas'}), 500
    
@app.route('/obtener-trabajadores', methods=['GET'])
def obtener_trabajadores():
    correo = request.args.get('correoEmpresa')

    try:
        conn = sqlite3.connect('mibasededatos.db')
        cursor = conn.cursor()
        cursor.execute('SELECT nombre, correo, url_img FROM trabajadores WHERE emailEmpresa = ?', (correo,))
        trabajadores = cursor.fetchall()
        conn.close()

        # Convertir a una lista de diccionarios
        lista_trabajadores = [{'nombre': t[0], 'correo': t[1], 'url_img': t[2]} for t in trabajadores]
        return jsonify(lista_trabajadores), 200
    except Error as e:
        print(e)
        return jsonify({'message': 'Error al obtener los trabajadores', 'error': str(e)}), 400


@app.route('/obtener-trabajador', methods=['GET'])
def obtener_trabajador():
    correo = request.args.get('correoTrajabador')
    try:
        conn = sqlite3.connect('mibasededatos.db')
        cursor = conn.cursor()
        cursor.execute('SELECT nombre, correo,  url_img, emailEmpresa FROM trabajadores WHERE correo = ?', (correo,))
        trabajadores = cursor.fetchall()
        cursor.execute('SELECT nombre_empresa FROM usuarios_empresa WHERE correo = ?', (trabajadores[0][3],))
        nombreEmpresa = cursor.fetchall()
            
        conn.close()
        
        # Convertir a una lista de diccionarios
        lista_trabajadores = {'nombre': trabajadores[0][0], 'correo': trabajadores[0][1], 'url_img': trabajadores[0][2], 'nombreEmpresa': nombreEmpresa}
        return jsonify(lista_trabajadores), 200
    except Error as e:
        print(e)
        conn.close()
        return jsonify({'message': 'Error al obtener el trabajador', 'error': str(e)}), 400






"""


           
@app.route('/agregar-horario', methods=['POST'])
def agregar_horario():
    data = request.get_json()
    print(data)
    correo = data.get('correo')
    dia = data.get('dia')
    hora = data.get('hora')

    if not correo or not dia or not hora:
        return jsonify({'message': 'Faltan datos para agregar el horario'}), 400

    try:
        conn = sqlite3.connect('mibasededatos.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO horarios (correo, dia, hora)
            VALUES (?, ?, ?)
        ''', (correo, dia, hora))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Horario agregado correctamente'}), 201
    except Error as e:
        print(e)
        return jsonify({'message': 'Error al agregar el horario'}), 500
    
 


@app.route('/horarios', methods=['GET', 'POST'])
def manage_schedules():
    conn = get_db_connection()
    
    if request.method == 'POST':
        # Guardar un nuevo horario
        correo = request.json.get('correo')
        dia = request.json.get('dia')
        hora = request.json.get('hora')
        
        conn.execute('INSERT INTO horarios (correo, dia, hora) VALUES (?, ?, ?)', (correo, dia, hora))
        conn.commit()
        conn.close()
        return jsonify({"message": "Horario guardado exitosamente"}), 201

    elif request.method == 'GET':
        # Obtener todos los horarios
        horarios = conn.execute('SELECT dia, hora FROM horarios').fetchall()
        conn.close()
        
        # Convertir los resultados a una lista de diccionarios
        result = [{'dia': row['dia'], 'hora': row['hora']} for row in horarios]
        return jsonify(result)
    

"""

@app.route('/reservar-horario', methods=['POST'])
def reservar_horario():
    data = request.get_json()
    correTrajabador = data.get('correo')
    dia = data.get('dia')
    hora = data.get('hora')
    correoUsuario = data.get('correoUsuario')
    print(data)



    try:
        conn = sqlite3.connect('mibasededatos.db')
        cursor = conn.cursor()


        # actualizar el horario en la tabla 'horarios' el campo reservadoUsuario con el correo del usuario
        cursor.execute('''
            UPDATE horarios
            SET reservadoUsuario = ?
            WHERE correo = ? AND dia = ? AND hora = ?
        ''', (correoUsuario, correTrajabador, dia, hora))


        conn.commit()
        conn.close()
        return jsonify({'message': 'Cita reservada correctamente'}), 201
    except Error as e:
        print(e)

        conn.close()
        return jsonify({'message': 'Error al reservar la cita'}), 500






"""
# Ruta para eliminar horario
@app.route('/eliminar-horario2', methods=['POST'])  # Cambié el nombre de la ruta aquí
def eliminar_horario_por_correo():
    
        data = request.get_json()  # Obtener los datos enviados desde el frontend
        dia = data.get('dia')
        hora = data.get('hora')
        correo = data.get('correo')

        # Verificar si se recibieron todos los datos
        if not dia or not hora:
            return jsonify({'message': 'Faltan datos: día o hora'}), 400

        try:
            # Conectar con la base de datos
            conn = sqlite3.connect('mibasededatos.db')
            cursor = conn.cursor()

            # Eliminar el horario en la tabla 'horarios'
            cursor.execute('''
                DELETE FROM horarios
                WHERE correo = ? AND dia = ? AND hora = ?
            ''', (correo, dia, hora))
            
            conn.commit()  # Guardar los cambios en la base de datos
            conn.close()

            if cursor.rowcount > 0:
                return jsonify({'message': 'Horario eliminado exitosamente'}), 200
            else:
                return jsonify({'message': 'No se encontró el horario para eliminar'}), 404

        except sqlite3.Error as e:
            return jsonify({'message': 'Error al eliminar el horario', 'error': str(e)}), 500
    
"""




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)


