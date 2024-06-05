from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pymysql

login_manager = LoginManager()
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'
login_manager.init_app(app)

class User(UserMixin):
    es_admin = False

@login_manager.user_loader
def user_loader(email):
    miConexion = pymysql.connect(host ='172.17.0.3',user ='admin',passwd ='admin',db = 'proyecto')
    cur = miConexion.cursor()
    cur.execute('SELECT Correo_Electronico, Admin FROM Usuarios WHERE Correo_Electronico = %s', (email,))
    user_db = cur.fetchone()
    if user_db is None:
        return
    user = User()
    user.id = email
    user.es_admin = user_db[1]
    return user

@app.route('/register', methods=['GET'])
def register_get():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register_post():
    email = request.form['email']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    pais = request.form['paisNacimiento']
    departamento = request.form['deptoNacimiento']
    municipio = request.form['municipioNacimiento']
    telefono = request.form['telefono']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password == confirm_password:
        miConexion = pymysql.connect(host ='172.17.0.3',user ='admin',passwd ='admin',db = 'proyecto')
        cur = miConexion.cursor()
        cur.execute('INSERT INTO Usuarios (Correo_Electronico, Nombre, Apellido, Telefono, Contrasena, Pais_Nacimiento, Departamento_Nacimiento, Municipio_Nacimiento) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (email, nombre, apellido, telefono, password, pais, departamento, municipio))
        miConexion.commit()
        miConexion.close()
    else:
        return 'La contraseña y la confirmación de la contraseña no coinciden.', 400

    return redirect(url_for('login_get'))

@app.route('/login', methods=['GET'])
def login_get():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    miConexion = pymysql.connect(host ='172.17.0.3',user ='admin',passwd ='admin',db = 'proyecto')
    cur = miConexion.cursor()
    cur.execute('SELECT Contrasena, Admin FROM Usuarios WHERE Correo_Electronico = %s', (email,))
    user_db = cur.fetchone()
    if user_db is None or user_db[0] != password:
        return 'Correo electrónico o contraseña incorrectos'
    user = User()
    user.id = email
    user.es_admin = user_db[1]
    login_user(user)
    return redirect(url_for('inicio'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Has cerrado sesión'  

@app.route('/protected')
@login_required
def protected():
    if current_user.es_admin:
        return 'Eres un administrador'
    else:
        return 'Eres un usuario'

@app.route('/inicio')
def inicio():
    miConexion = pymysql.connect(host ='172.17.0.3',user ='admin',passwd ='admin',db = 'proyecto')
    cur = miConexion.cursor()
    cur.execute('SELECT Nombre_Producto FROM Producto')
    productos = cur.fetchall()
    miConexion.close()

    return render_template('inicio.html', productos=productos)

@app.route('/', methods=['GET'])
def home():
    miConexion = pymysql.connect(host ='172.17.0.3',user ='admin',passwd ='admin',db = 'proyecto')
    cur = miConexion.cursor()

    cur.execute('select Id_Departamento, Nombre_Departamento, Id_Pais from departamento')
    departamentos = cur.fetchall()

    cur.execute('select Nombre_pais, Id_Pais from pais')
    paises = cur.fetchall()

    cur.execute('select Id_municipio, Nombre_municipio, Id_departamento from municipio')
    municipios = cur.fetchall()

    miConexion.close()

    return render_template('index.html', departamentos=departamentos, paises=paises, municipios=municipios)

@app.route('/get_departamentos/<paisId>', methods=['GET'])
def get_departamentos(paisId):
    miConexion = pymysql.connect(host ='172.17.0.3',user ='admin',passwd ='admin',db = 'proyecto')
    cur = miConexion.cursor()

    cur.execute('select Id_Departamento, Nombre_Departamento from departamento where Id_Pais = %s', (paisId,))
    departamentos = cur.fetchall()

    miConexion.close()

    return jsonify(departamentos=departamentos)

@app.route('/get_municipios/<deptoId>', methods=['GET'])
def get_municipios(deptoId):
    miConexion = pymysql.connect(host ='172.17.0.3',user ='admin',passwd ='admin',db = 'proyecto')
    cur = miConexion.cursor()

    cur.execute('select Id_municipio, Nombre_municipio from municipio where Id_departamento = %s', (deptoId,))
    municipios = cur.fetchall()

    miConexion.close()

    return jsonify(municipios=municipios)

@app.route('/admin')
@login_required
def admin():
    if current_user.es_admin:
        return render_template('admin.html')
    else:
        return 'No tienes permiso para acceder a esta página'
    
@app.route('/carrito')
@login_required
def carrito():
    return render_template('carrito.html')

@app.route('/comprar', methods=['POST'])
@login_required
def comprar():
    return 'La compra fue realizada'

@app.route('/agregar_mercancia', methods=['GET'])
@login_required
def agregar_mercancia():
    if current_user.es_admin:
        return render_template('agregar_mercancia.html')
    else:
        return 'No tienes permiso para acceder a esta página'

@app.route('/agregar_mercancia_post', methods=['POST'])
@login_required
def agregar_mercancia_post():
    if current_user.es_admin:
        nombre_producto = request.form['nombre_producto']
        descripcion_producto = request.form['descripcion_producto']
        precio_producto = request.form['precio_producto']
        tipo_producto = request.form['tipo_producto']
        talla_producto = request.form['talla_producto']
        color_producto = request.form['color_producto']
        cantidad_producto = request.form['cantidad_producto']

        miConexion = pymysql.connect(host ='172.17.0.3',user ='admin',passwd ='admin',db = 'proyecto')
        cur = miConexion.cursor()
        cur.execute('INSERT INTO Producto (Nombre_Producto, Descripcion_Producto, Precio_Producto, Tipo_Producto, Talla_Producto, Color_Producto, Cantidad) VALUES (%s, %s, %s, %s, %s, %s, %s)', (nombre_producto, descripcion_producto, precio_producto, tipo_producto, talla_producto, color_producto, cantidad_producto))
        miConexion.commit()
        miConexion.close()

        return 'La mercancía ha sido agregada exitosamente'
    else:
        return 'No tienes permiso para acceder a esta página'

@app.route('/eliminar_mercancia', methods=['GET'])
@login_required
def eliminar_mercancia():
    if current_user.es_admin:
        return render_template('eliminar_mercancia.html')
    else:
        return 'No tienes permiso para acceder a esta página'
    
@app.route('/eliminar_mercancia_post', methods=['POST'])
@login_required
def eliminar_mercancia_post():
    if current_user.es_admin:
        codigo_producto = request.form['codigo_producto']

        miConexion = pymysql.connect(host ='172.17.0.3',user ='admin',passwd ='admin',db = 'proyecto')
        cur = miConexion.cursor()
        cur.execute('DELETE FROM Producto WHERE Id_Producto = %s', (codigo_producto,))
        miConexion.commit()
        miConexion.close()

        return 'El producto ha sido eliminado exitosamente'
    else:
        return 'No tienes permiso para acceder a esta página'
    
@app.route('/gestionar_mercancia', methods=['GET'])
@login_required
def gestionar_mercancia():
    if current_user.es_admin:
        return render_template('gestionar_mercancia.html')
    else:
        return 'No tienes permiso para acceder a esta página'

@app.route('/gestionar_descuentos', methods=['GET'])
@login_required
def gestionar_descuentos():
    if current_user.es_admin:
        return render_template('gestionar_descuentos.html')
    else:
        return 'No tienes permiso para acceder a esta página'

@app.route('/gestionar_descuentos_post', methods=['POST'])
@login_required
def gestionar_descuentos_post():
    if current_user.es_admin:
        codigo_producto = request.form['codigo_producto']
        porcentaje_descuento = request.form['porcentaje_descuento']
        accion = request.form['accion']

        miConexion = pymysql.connect(host ='172.17.0.3',user ='admin',passwd ='admin',db = 'proyecto')
        cur = miConexion.cursor()

        if accion == 'aplicar':
            cur.execute('UPDATE Producto SET Precio_Producto = Precio_Producto - (Precio_Producto * %s / 100) WHERE Id_Producto = %s', (porcentaje_descuento, codigo_producto))
        elif accion == 'quitar':
            cur.execute('UPDATE Producto SET Precio_Producto = Precio_Producto + (Precio_Producto * %s / 100) WHERE Id_Producto = %s', (porcentaje_descuento, codigo_producto))

        miConexion.commit()
        miConexion.close()

        return 'El descuento ha sido gestionado exitosamente'
    else:
        return 'No tienes permiso para acceder a esta página'

@app.route('/ver_stock', methods=['GET'])
@login_required
def ver_stock():
    if current_user.es_admin:
        miConexion = pymysql.connect(host ='172.17.0.3',user ='admin',passwd ='admin',db = 'proyecto')
        cur = miConexion.cursor()
        cur.execute('SELECT Id_Producto, Nombre_Producto, Cantidad, Precio_Producto, Talla_Producto, Color_Producto FROM Producto')
        stock = cur.fetchall()
        miConexion.close()

        return render_template('ver_stock.html', stock=stock)
    else:
        return 'No tienes permiso para acceder a esta página'

@app.route('/actualizar_mercancia', methods=['GET'])
@login_required
def actualizar_mercancia():
    if current_user.es_admin:
        return render_template('actualizar_mercancia.html')
    else:
        return 'No tienes permiso para acceder a esta página'

@app.route('/actualizar_mercancia_post', methods=['POST'])
@login_required
def actualizar_mercancia_post():
    if current_user.es_admin:
        codigo_producto = request.form['codigo_producto']
        cantidad_producto = int(request.form['cantidad_producto'])
        accion = request.form['accion']

        miConexion = pymysql.connect(host ='172.17.0.3',user ='admin',passwd ='admin',db = 'proyecto')
        cur = miConexion.cursor()

        if accion == 'agregar':
            cur.execute('UPDATE Producto SET Cantidad = Cantidad + %s WHERE Id_Producto = %s', (cantidad_producto, codigo_producto))
        elif accion == 'quitar':
            cur.execute('UPDATE Producto SET Cantidad = Cantidad - %s WHERE Id_Producto = %s', (cantidad_producto, codigo_producto))

        miConexion.commit()
        miConexion.close()

        return 'La mercancía ha sido actualizada exitosamente'
    else:
        return 'No tienes permiso para acceder a esta página'

if __name__ == '__main__':

    miConexion = pymysql.connect(host='172.17.0.3', user='admin', passwd='admin', db='proyecto')
    cur = miConexion.cursor()

    # Crear la tabla 'Pais' si no existe
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Pais (
        Id_Pais INT PRIMARY KEY NOT NULL,
        Nombre_Pais VARCHAR(20)
    )
    ''')

    # Crear la tabla 'Departamento' si no existe
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Departamento (
        Id_Departamento INT PRIMARY KEY NOT NULL,
        Nombre_Departamento VARCHAR(20),
        Id_Pais INT,
        FOREIGN KEY(Id_Pais) REFERENCES Pais(Id_Pais)
    )
    ''')

    # Crear la tabla 'Municipio' si no existe
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Municipio (
        Id_municipio INT PRIMARY KEY NOT NULL,
        Nombre_municipio VARCHAR(20),
        Id_departamento INT,
        FOREIGN KEY(Id_departamento) REFERENCES Departamento(Id_Departamento)
    )
    ''')
    
    # Crear la tabla 'Producto' si no existe
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Producto (
        Id_Producto INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
        Nombre_Producto VARCHAR(40) NOT NULL,
        Descripcion_Producto VARCHAR(60) NOT NULL,
        Precio_Producto INT NOT NULL,
        Tipo_Producto VARCHAR(20) NOT NULL,
        Talla_Producto VARCHAR(30) NOT NULL,
        Color_Producto VARCHAR(30) NOT NULL,
        Cantidad INT
    )
    ''')

    # Crear la tabla 'Usuarios' si no existe
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Usuarios (
        Correo_Electronico VARCHAR(255) PRIMARY KEY NOT NULL,
        Nombre VARCHAR(255) NOT NULL,
        Apellido VARCHAR(255) NOT NULL,
        Telefono INT NOT NULL,
        Contrasena VARCHAR(255) NOT NULL,
        Pais_Nacimiento INT NOT NULL,
        Departamento_Nacimiento INT NOT NULL,
        Municipio_Nacimiento INT NOT NULL,
        Admin BOOLEAN DEFAULT FALSE NOT NULL,
        FOREIGN KEY(Pais_Nacimiento) REFERENCES Pais(Id_Pais),
        FOREIGN KEY(Departamento_Nacimiento) REFERENCES Departamento(Id_Departamento),
        FOREIGN KEY(Municipio_Nacimiento) REFERENCES Municipio(Id_municipio)
    )
    ''')


    # Insertar datos en la tabla 'Pais' si está vacía
    cur.execute('SELECT COUNT(*) FROM Pais')
    if cur.fetchone()[0] == 0:
        cur.execute('''
        INSERT INTO Pais (Id_Pais, Nombre_Pais) VALUES
        (4,'Afganistan'),
        (276,'Alemania'),
        (32, 'Argentina'),
        (56, 'Belgica'),
        (68, 'Bolivia'),
        (634, 'Qatar'),
        (156, 'China'),
        (192, 'Cuba'),
        (170, 'Colombia'),
        (250, 'Francia')
        ''')

    # Insertar datos en la tabla 'Departamento' si está vacía
    cur.execute('SELECT COUNT(*) FROM Departamento')
    if cur.fetchone()[0] == 0:
        cur.execute('''
        INSERT INTO Departamento (Id_Departamento, Nombre_Departamento, Id_Pais) VALUES
        (92,'Kabul', 4), (93,'Kandaharl', 4), (94,'Herat', 4),
        (37,'Berlin', 276), (36,'Hamburgo', 276), (35,'Munich', 276),
        (32,'Buenos Aires', 32), (33,'Cordoba', 32), (34,'Rosario', 32),
        (57,'Bruselas', 56), (58,'Gent', 56), (59,'Namur', 56),
        (69,'Sucre', 68), (70,'La paz', 68), (71,'Tarija', 68),
        (635,'Doha', 634), (636,'Al Khor', 634), (157,'Pekin', 156),
        (158,'Shangai', 156), (193,'La habana', 192), (194,'Santa Clara', 192),
        (171,'Bogota', 170), (172,'Amazonas', 170), (173,'Pereira', 170),
        (251,'Paris', 250)
        ''')

    # Insertar datos en la tabla 'Municipio' si está vacía
    cur.execute('SELECT COUNT(*) FROM Municipio')
    if cur.fetchone()[0] == 0:
        cur.execute('''
        INSERT INTO Municipio (Id_municipio, Nombre_municipio, Id_departamento) VALUES
        (1,'Dashti Barchi',92), (2,'Kartey Sakhi',92),
        (3,'Ghorak',93), (4,'Daman',93),
        (5,'Shar Noe',94), (6,'Fargha',94),
        (7,'Mitte',37), (8,'Pankow',37),
        (9,'Tomesh',36), (10,'Appen',36),
        (11,'Aying',35), (12,'Brunnthal',35),
        (13,'Florencio',32), (14,'Varela',32),
        (15,'Alicia',33), (16,'Alma Fuerte',33),
        (17,'Perez',34), (18,'Funes',34),
        (19,'Jette',57), (20,'Forest',57),
        (21,'Lederberg',58), (22,'Afsnee',58),
        (23,'Ardenas',59), (24,'Condroz',59),
        (25,'San Lucas',69), (26,'Monteagudo',69),
        (27,'Laja',70), (28,'Pucarani',70),
        (29,'Bermejo',71), (30,'San lorenzo',71),
        (31,'Al Wakrah',635), (32,'Al Daayen ',635),
        (33,'Beijing',157), (34,'Distrito de Xicheng',157),
        (35,'Tianjin',158), (36,'Provincia de Jilin',158),
        (37,'Habana del este',193), (38,'Habana Vieja',193),
        (39,'Ranchuelo',194), (40,'Santo Domingo',194),
        (41,'Teusaquillo',171), (42,'Fontibon',171),
        (43,'Leticia',172), (44,'Puerto Alegria',172),
        (45,'Guatica',173), (46,'Belen de Umbria',173),
        (47,'Le Marais',251), (48,'Campos eliseos',251)
        ''')

    # Crear la tabla 'Comentarios' si no existe
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Comentarios (
        Id_Comentario INT AUTO_INCREMENT PRIMARY KEY,
        Id_Producto INT NOT NULL,
        Correo_Usuario VARCHAR(50) NOT NULL,
        Comentario VARCHAR(500) NOT NULL,
        Fecha DATETIME,
        FOREIGN KEY(Id_Producto) REFERENCES Producto(Id_Producto),
        FOREIGN KEY(Correo_Usuario) REFERENCES Usuarios(Correo_Electronico)
    )
    ''')

    # Crear la tabla 'Carrito' si no existe
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Carrito (
        Id_Carrito INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
        Correo_Usuario VARCHAR(50) NOT NULL,
        FOREIGN KEY(Correo_Usuario) REFERENCES Usuarios(Correo_Electronico)
    )
    ''')

    # Crear la tabla 'Items_Carrito' si no existe
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Items_Carrito (
        Id_Item INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
        Id_Carrito INT,
        Id_Producto INT,
        Cantidad_Producto INT,
        FOREIGN KEY(Id_Carrito) REFERENCES Carrito(Id_Carrito),
        FOREIGN KEY(Id_Producto) REFERENCES Producto(Id_Producto)
    )
    ''')

    # Crear la tabla 'Valoraciones_Productos' si no existe
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Valoraciones_Productos (
        Id_Valoracion INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
        Id_Producto INT NOT NULL,
        Correo_Usuario VARCHAR(50) NOT NULL,
        Valoracion INT,
        FOREIGN KEY(Id_Producto) REFERENCES Producto(Id_Producto),
        FOREIGN KEY(Correo_Usuario) REFERENCES Usuarios(Correo_Electronico)
    )
    ''')

    cur.execute('''
    INSERT INTO Usuarios (Correo_Electronico, Nombre, Apellido, Telefono, Contrasena, Pais_Nacimiento, Departamento_Nacimiento, Municipio_Nacimiento, Admin)
    VALUES('b.uribe@utp.edu.co', 'Brahyan', 'Uribe', 1234567890, 'Oconer49', 170, 171, 25, TRUE)
    ON DUPLICATE KEY UPDATE Correo_Electronico=Correo_Electronico
    ''')

    # Hacer commit para guardar los cambios
    miConexion.commit()

    # Mostrar los datos de las tablas 'Usuarios' y 'Producto'
    cur.execute('SELECT * FROM Usuarios')
    print("Usuarios:")
    for usuario in cur.fetchall():
        print(usuario)

    cur.execute('SELECT * FROM Producto')
    print("\nProductos:")
    for producto in cur.fetchall():
        print(producto)

    # Cerrar la conexión
    miConexion.close()

    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5001, debug = True)