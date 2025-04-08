from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import get_connection
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'clave_secreta_valemi'

# Configuración para subida de imágenes
UPLOAD_FOLDER = 'static/img/productos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PRODUCTOS_POR_PAGINA = 5

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# RUTA INDEX
@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT whatsapp, instagram FROM configuracion WHERE id = 1")
    config = cursor.fetchone()
    cursor.execute("SELECT * FROM productos ORDER BY id DESC LIMIT 3")
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', productos=productos, whatsapp=config['whatsapp'], instagram=config['instagram'])

# RUTA MENU
@app.route('/menu')
def menu():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT whatsapp, instagram FROM configuracion WHERE id = 1")
    config = cursor.fetchone()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('menu.html', productos=productos, whatsapp=config['whatsapp'], instagram=config['instagram'], mostrar_botones=True)

# RUTA CONTACTO
@app.route('/contacto')
def contacto():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT whatsapp, instagram FROM configuracion WHERE id = 1")
    config = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('contacto.html', whatsapp=config['whatsapp'], instagram=config['instagram'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s AND contrasena = %s", (usuario, contrasena))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['usuario'] = user['usuario']
            return redirect(url_for('admin'))
        else:
            error = "Credenciales inválidas"

    return render_template('login.html', error=error)

@app.route('/admin')
def admin():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    page = request.args.get('page', 1, type=int)
    per_page = PRODUCTOS_POR_PAGINA
    offset = (page - 1) * per_page

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos LIMIT %s OFFSET %s", (per_page, offset))
    productos = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total FROM productos")
    total_productos = cursor.fetchone()['total']
    total_pages = (total_productos + per_page - 1) // per_page

    cursor.close()
    conn.close()

    return render_template('admin.html', usuario=session['usuario'], productos=productos, current_page=page, total_pages=total_pages)


@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    nombre = request.form['nombre'].strip()
    precio = request.form['precio']
    imagen = request.files['imagen']

    if not nombre or not precio or not imagen:
        flash('⚠️ Todos los campos son obligatorios.')
        return redirect(url_for('admin'))

    if not allowed_file(imagen.filename):
        flash('⚠️ Formato de imagen no permitido.')
        return redirect(url_for('admin'))

    filename = secure_filename(imagen.filename)
    ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    imagen.save(ruta_imagen)

    ruta_guardada = f'img/productos/{filename}'

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE nombre = %s", (nombre,))
    if cursor.fetchone():
        flash('⚠️ Ya existe un producto con ese nombre.')
        cursor.close()
        conn.close()
        return redirect(url_for('admin'))

    cursor.execute("INSERT INTO productos (nombre, precio, imagen) VALUES (%s, %s, %s)", (nombre, precio, ruta_guardada))
    conn.commit()
    cursor.close()
    conn.close()

    flash('✅ Producto agregado correctamente.')
    return redirect(url_for('admin'))

@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        nuevo_precio = request.form['precio']
        nueva_imagen = request.files.get('imagen')

        cursor.execute("SELECT imagen FROM productos WHERE id = %s", (id,))
        producto_actual = cursor.fetchone()
        imagen_actual = producto_actual['imagen'] if producto_actual else ''

        imagen_guardar = imagen_actual

        if nueva_imagen and nueva_imagen.filename:
            if allowed_file(nueva_imagen.filename):
                filename = secure_filename(nueva_imagen.filename)
                ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                nueva_imagen.save(ruta_imagen)
                imagen_guardar = f'img/productos/{filename}'

                if imagen_actual and imagen_guardar != imagen_actual:
                    ruta_anterior = os.path.join('static', imagen_actual)
                    if os.path.exists(ruta_anterior):
                        os.remove(ruta_anterior)
            else:
                flash('⚠️ Formato de imagen no permitido.')
                return redirect(url_for('editar_producto', id=id))

        cursor.execute("UPDATE productos SET nombre = %s, precio = %s, imagen = %s WHERE id = %s", (nuevo_nombre, nuevo_precio, imagen_guardar, id))
        conn.commit()
        cursor.close()
        conn.close()

        flash('✅ Producto actualizado correctamente')
        return redirect(url_for('admin'))

    cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('editar_producto.html', producto=producto)

@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT imagen FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()

    if producto and producto['imagen']:
        ruta_completa = os.path.join('static', producto['imagen'])
        if os.path.exists(ruta_completa):
            os.remove(ruta_completa)

    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('✅ Producto eliminado correctamente')
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nuevo_whatsapp = request.form['whatsapp'].strip()
        nuevo_instagram = request.form['instagram'].strip()

        cursor.execute("UPDATE configuracion SET whatsapp = %s, instagram = %s WHERE id = 1", (nuevo_whatsapp, nuevo_instagram))
        conn.commit()
        flash("✅ Configuración actualizada correctamente.")
        cursor.close()
        conn.close()
        return redirect(url_for('configuracion'))

    # GET - Obtener valores actuales
    cursor.execute("SELECT * FROM configuracion WHERE id = 1")
    config = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('configuracion.html', config=config)


if __name__ == '__main__':
    app.run(debug=True)
