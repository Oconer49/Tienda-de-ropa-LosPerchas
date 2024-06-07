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
    miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
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
        miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
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
    miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
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
    miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
    cur = miConexion.cursor()
    cur.execute('SELECT Nombre_Producto FROM Producto')
    productos = cur.fetchall()
    miConexion.close()

    return render_template('inicio.html', productos=productos)

@app.route('/', methods=['GET'])
def home():
    miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
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
    miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
    cur = miConexion.cursor()

    cur.execute('select Id_Departamento, Nombre_Departamento from departamento where Id_Pais = %s', (paisId,))
    departamentos = cur.fetchall()

    miConexion.close()

    return jsonify(departamentos=departamentos)

@app.route('/get_municipios/<deptoId>', methods=['GET'])
def get_municipios(deptoId):
    miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
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

        miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
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

        miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
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

        miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
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
        miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
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

        miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
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
    app.run(debug=True)