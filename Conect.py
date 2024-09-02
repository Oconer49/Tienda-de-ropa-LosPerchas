from Instance import database
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import datetime
from bson.objectid import ObjectId

login_manager = LoginManager()
app = Flask(__name__)
app.secret_key = 'q7panl8Q4GQnqMAI'
login_manager.init_app(app)

usuariosdb = database["usuarios"]
carritodb = database["carrito"]
comentariosdb = database["comentarios"]
departamentodb = database["departamento"]
items_carritodb = database["items_carrito"]
municipiodb = database["municipio"]
paisdb = database["pais"]
productodb = database["producto"]

class User(UserMixin):
    es_admin = False
    email = None

@login_manager.user_loader
def user_loader(email):
    datos = usuariosdb.find_one({"Correo_Electronico": email})
    if datos:
        user = User()
        user.id = email
        user.email = email
        user.es_admin = datos.get("Admin", False)
        return user
    return None

@app.route('/register', methods=['GET'])
def register_get():
    paises = list(paisdb.find({}))
    print(paises)
    return render_template('index.html', paises=paises)


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
        usuariosdb.insert_one({
            "Correo_Electronico": email,
            "Nombre": nombre,
            "Apellido": apellido,
            "Telefono": telefono,
            "Contrasena": password,
            "Pais_Nacimiento": pais,
            "Departamento_Nacimiento": departamento,
            "Municipio_Nacimiento": municipio
        })
        return redirect(url_for('login_get'))
    else:
        return 'La contraseña y la confirmación de la contraseña no coinciden.', 400

@app.route('/login', methods=['GET'])
def login_get():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    user_db = usuariosdb.find_one({"Correo_Electronico": email})
    
    if user_db is None or user_db["Contrasena"] != password:
        return 'Correo electrónico o contraseña incorrectos'
    
    user = User()
    user.id = email
    user.es_admin = user_db.get("Admin", False)
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
    productos = list(productodb.find({}))
    return render_template('inicio.html', productos=productos)

@app.route('/descripcion/<producto_id>')
def descripcion(producto_id):
    producto = productodb.find_one({"_id": ObjectId(producto_id)})
    comentarios = list(comentariosdb.find({"Id_Producto": ObjectId(producto_id)}))

    if producto is None:
        return 'Producto no encontrado', 404

    return render_template('descripcion.html', producto=producto, comentarios=comentarios)

@app.route('/', methods=['GET'])
def home():
    departamentos = list(departamentodb.find({}))
    paises = list(paisdb.find({}))
    municipios = list(municipiodb.find({}))

    return render_template('index.html', departamentos=departamentos, paises=paises, municipios=municipios)

@app.route('/get_departamentos/<paisId>', methods=['GET'])
def get_departamentos(paisId):
    departamentos = list(departamentodb.find({"Id_Pais": int(paisId)}))
    print("Departamentos:", departamentos)
    return jsonify(departamentos=[{
        'Id_Departamento': d['Id_Departamento'],
        'Nombre_Departamento': d['Nombre_Departamento']
    } for d in departamentos])

@app.route('/get_municipios/<deptoId>', methods=['GET'])
def get_municipios(deptoId):
    municipios = list(municipiodb.find({"Id_Departamento": int(deptoId)}))
    print("Municipios:", municipios)
    return jsonify(municipios=[{
        'Id_Municipio': m['Id_Municipio'],
        'Nombre_Municipio': m['Nombre_Municipio']
    } for m in municipios])

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
    carrito = carritodb.find_one({"Correo_Usuario": current_user.email})
    if carrito:
        productos = list(items_carritodb.find({"Id_Carrito": carrito["_id"]}))
    else:
        productos = []
    return render_template('carrito.html', productos=productos)

@app.route('/pagar', methods=['POST'])
@login_required
def pagar():
    carrito = carritodb.find_one({"Correo_Usuario": current_user.email})
    if carrito:
        total = 0
        productos = items_carritodb.find({"Id_Carrito": carrito["_id"]})
        for item in productos:
            producto = productodb.find_one({"_id": ObjectId(item["Id_Producto"])})
            total += producto["Precio_Producto"] * item["Cantidad_Producto"]
    else:
        total = 0

    return 'Compra exitosa! Tu total fue: $' + str(total)

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
        url_producto = request.form['url_producto']

        productodb.insert_one({
            "Nombre_Producto": nombre_producto,
            "Descripcion_Producto": descripcion_producto,
            "Precio_Producto": precio_producto,
            "Tipo_Producto": tipo_producto,
            "Talla_Producto": talla_producto,
            "Color_Producto": color_producto,
            "Cantidad": cantidad_producto,
            "url_producto": url_producto
        })

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
        productodb.delete_one({"_id": ObjectId(codigo_producto)})

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
        porcentaje_descuento = float(request.form['porcentaje_descuento'])
        accion = request.form['accion']

        producto = productodb.find_one({"_id": ObjectId(codigo_producto)})

        if accion == 'aplicar':
            nuevo_precio = producto["Precio_Producto"] - (producto["Precio_Producto"] * porcentaje_descuento / 100)
        elif accion == 'quitar':
            nuevo_precio = producto["Precio_Producto"] + (producto["Precio_Producto"] * porcentaje_descuento / 100)

        productodb.update_one({"_id": ObjectId(codigo_producto)}, {"$set": {"Precio_Producto": nuevo_precio}})

        return 'El descuento ha sido gestionado exitosamente'
    else:
        return 'No tienes permiso para acceder a esta página'

@app.route('/ver_stock', methods=['GET'])
@login_required
def ver_stock():
    if current_user.es_admin:
        stock = list(productodb.find({}))
        return render_template('ver_stock.html', stock=stock)
    else:
        return 'No tienes permiso para acceder a esta página'

@app.route('/inventario')
def inventario():
    productos = list(productodb.find({}))
    return render_template('inventario.html', productos=productos)

if __name__ == '__main__':
    app.run(debug=True)