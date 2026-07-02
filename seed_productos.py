"""
Seed script for bulk product import.
Usage: python seed_productos.py <ruta_carpeta_imagenes>

Expected folder structure:
  <ruta>/
    boligrafos/   -> $3  -> categoria "Boligrafos"
    termos/       -> $13 -> categoria "Termos"
    mousepads/    -> $7  -> categoria "Mousepads"
"""
import sys
import os
import uuid
import sqlite3
import shutil

CATEGORY_CONFIG = {
    'boligrafos': {'price': 3.00, 'category': 'Boligrafos'},
    'termos':     {'price': 13.00, 'category': 'Termos'},
    'mousepads':  {'price': 7.00,  'category': 'Mousepads'},
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_IMAGES = os.path.join(BASE_DIR, 'pagina-web-sublime', 'static', 'images')
DB_PATH = os.environ.get(
    'DATABASE_PATH',
    os.path.join(BASE_DIR, 'Sublime', 'BD', 'database.db')
)

ALLOWED_EXT = {'.jpg', '.jpeg', '.png'}


def product_name_from_file(filename):
    name = os.path.splitext(filename)[0]
    name = name.strip().replace('_', ' ').replace('-', ' ')
    name = ' '.join(name.split())
    return name


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <ruta_carpeta_imagenes>")
        sys.exit(1)

    source_dir = sys.argv[1]
    if not os.path.isdir(source_dir):
        print(f"Error: '{source_dir}' no es una carpeta valida.")
        sys.exit(1)

    os.makedirs(STATIC_IMAGES, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    def get_or_create_category(name):
        cur = conn.execute("SELECT id_categoria FROM categorias WHERE nombre = ?", (name,))
        row = cur.fetchone()
        if row:
            return row['id_categoria']
        cur = conn.execute("INSERT INTO categorias (nombre) VALUES (?)", (name,))
        return cur.lastrowid

    products_added = []
    image_map = {}

    for subfolder, cfg in CATEGORY_CONFIG.items():
        folder_path = os.path.join(source_dir, subfolder)
        if not os.path.isdir(folder_path):
            print(f"  [skip] No se encontro subcarpeta '{subfolder}'")
            continue

        cat_id = get_or_create_category(cfg['category'])
        files = sorted([
            f for f in os.listdir(folder_path)
            if os.path.splitext(f)[1].lower() in ALLOWED_EXT
        ])

        if not files:
            print(f"  [skip] '{subfolder}' no tiene imagenes JPG/PNG")
            continue

        print(f"\n  {cfg['category']} (${cfg['price']:.2f}) - {len(files)} productos:")

        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            uuid_name = f"{uuid.uuid4().hex}{ext}"
            src = os.path.join(folder_path, filename)
            dst = os.path.join(STATIC_IMAGES, uuid_name)
            shutil.copy2(src, dst)

            prod_name = product_name_from_file(filename)

            cur = conn.execute(
                "INSERT INTO productos (nombre, descripcion, costo, precio_venta, id_categoria, activo) "
                "VALUES (?, ?, ?, ?, ?, 1)",
                (prod_name, prod_name, cfg['price'], cfg['price'], cat_id)
            )
            prod_id = cur.lastrowid

            conn.execute(
                "INSERT INTO inventario (id_producto, stock_actual) VALUES (?, ?)",
                (prod_id, 10)
            )

            conn.execute(
                "INSERT INTO imagenes_productos (id_producto, ruta_imagen) VALUES (?, ?)",
                (prod_id, uuid_name)
            )

            products_added.append((prod_name, prod_name, cfg['price'], uuid_name, cfg['category']))
            image_map[filename] = uuid_name
            print(f"  + {filename} -> {prod_name}")

    conn.commit()
    conn.close()

    print(f"\n{'='*60}")
    print(f"OK {len(products_added)} productos insertados en la base de datos.")
    print(f"OK Imagenes copiadas a: {STATIC_IMAGES}")
    print(f"\nCodigo para agregar al seed en app.py:")
    print(f"{'='*60}")
    print()

    for cat_disp, cat_db in [
        ('Boligrafos', 'Boligrafos'),
        ('Mousepads', 'Mousepads'),
        ('Termos', 'Termos'),
    ]:
        cat_products = [p for p in products_added if p[4] == cat_disp]
        if cat_products:
            cat_key = cat_disp.lower()
            print(f"    # {cat_disp}")
            print(f"    {cat_key}_cat = conn.execute('SELECT id_categoria FROM categorias WHERE nombre = ? LIMIT 1', ('{cat_db}',)).fetchone()")
            print(f"    if {cat_key}_cat:")
            print(f"        {cat_key}_id = {cat_key}_cat['id_categoria']")
            print(f"        for nombre, descripcion, precio, imagen in [")
            for p in cat_products:
                print(f"            ('{p[0]}', '{p[1]}', {p[2]:.2f}, '{p[3]}'),")
            print(f"        ]:")
            print(f"            cur = conn.execute(")
            print(f"                'INSERT INTO productos (nombre, descripcion, costo, precio_venta, id_categoria, activo) VALUES (?, ?, ?, ?, ?, 1)',")
            print(f"                (nombre, descripcion, precio, precio, {cat_key}_id)")
            print(f"            )")
            print(f"            prod_id = cur.lastrowid")
            print(f"            conn.execute('INSERT INTO inventario (id_producto, stock_actual) VALUES (?, ?)', (prod_id, 10))")
            print(f"            conn.execute('INSERT INTO imagenes_productos (id_producto, ruta_imagen) VALUES (?, ?)', (prod_id, imagen))")
            print()

    print(f"    conn.commit()")


if __name__ == '__main__':
    main()
