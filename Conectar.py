

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
    miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
    cur = miConexion.cursor()
    cur.execute('SELECT Id_Carrito FROM Carrito WHERE Correo_Usuario = %s', (current_user.email,))
    carrito_id = cur.fetchone()[0]
    cur.execute('SELECT Producto.Id_Producto, Nombre_Producto, Precio_Producto, url_producto, Cantidad_Producto FROM Producto JOIN Items_Carrito ON Producto.Id_Producto = Items_Carrito.Id_Producto WHERE Id_Carrito = %s', (carrito_id,))
    productos = cur.fetchall()
    miConexion.close()

    return render_template('carrito.html', productos=productos)

@app.route('/pagar', methods=['POST'])
@login_required
def pagar():
    miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
    cur = miConexion.cursor()

    cur.execute('SELECT Id_Carrito FROM Carrito WHERE Correo_Usuario = %s', (current_user.email,))
    carrito_id = cur.fetchone()[0]

    cur.execute('SELECT SUM(Producto.Precio_Producto * Items_Carrito.Cantidad_Producto) FROM Producto JOIN Items_Carrito ON Producto.Id_Producto = Items_Carrito.Id_Producto WHERE Id_Carrito = %s', (carrito_id,))
    total = cur.fetchone()[0]

    miConexion.close()

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

        miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
        cur = miConexion.cursor()
        cur.execute('INSERT INTO Producto (Nombre_Producto, Descripcion_Producto, Precio_Producto, Tipo_Producto, Talla_Producto, Color_Producto, Cantidad, url_producto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (nombre_producto, descripcion_producto, precio_producto, tipo_producto, talla_producto, color_producto, cantidad_producto, url_producto))
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

@app.route('/agregar_al_carrito/<int:producto_id>', methods=['POST'])
@login_required
def agregar_al_carrito(producto_id):
    miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
    cur = miConexion.cursor()

    cur.execute('SELECT Id_Carrito FROM Carrito WHERE Correo_Usuario = %s', (current_user.email,))
    carrito = cur.fetchone()

    if carrito is None:
        cur.execute('INSERT INTO Carrito (Correo_Usuario) VALUES (%s)', (current_user.email,))
        carrito_id = cur.lastrowid
    else:
        carrito_id = carrito[0]
    cur.execute('INSERT INTO Items_Carrito (Id_Carrito, Id_Producto, Cantidad_Producto) VALUES (%s, %s, 1)', (carrito_id, producto_id))

    miConexion.commit()
    miConexion.close()

    return 'Producto añadido al carrito', 200

@app.route('/eliminar_del_carrito/<int:producto_id>', methods=['POST'])
@login_required
def eliminar_del_carrito(producto_id):
    miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
    cur = miConexion.cursor()
    cur.execute('SELECT Id_Carrito FROM Carrito WHERE Correo_Usuario = %s', (current_user.email,))
    carrito_id = cur.fetchone()[0]
    cur.execute('DELETE FROM Items_Carrito WHERE Id_Carrito = %s AND Id_Producto = %s', (carrito_id, producto_id))

    miConexion.commit()
    miConexion.close()

    return redirect(url_for('carrito'))

@app.route('/comentar/<int:producto_id>', methods=['POST'])
@login_required
def comentar(producto_id):
    comentario = request.form['comment']
    correo_usuario = current_user.email
    fecha = datetime.datetime.now()

    miConexion = pymysql.connect(host ='localhost',user ='root',passwd ='123daniel...',db = 'proyecto')
    cur = miConexion.cursor()
    cur.execute('INSERT INTO Comentarios (Id_Producto, Correo_Usuario, Comentario, Fecha) VALUES (%s, %s, %s, %s)', (producto_id, correo_usuario, comentario, fecha))
    miConexion.commit()
    miConexion.close()

    return redirect(url_for('descripcion', producto_id=producto_id))

if __name__ == '__main__':
    app.run(debug=True)
