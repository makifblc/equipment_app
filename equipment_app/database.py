import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

#database bağlanma
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise Exception(f"Veritabanı bağlantı hatası: {e}")


def init_database():
    try:
        base_cfg = {k: v for k, v in DB_CONFIG.items() if k != "database"}
        conn = mysql.connector.connect(**base_cfg)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        raise Exception(f"Veritabanı oluşturma hatası: {e}")

    conn = get_connection()
    cursor = conn.cursor()


#tablo oluşturma(yoksa)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            icon VARCHAR(10) DEFAULT '',
            description TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category_id INT NOT NULL,
            name VARCHAR(200) NOT NULL,
            brand VARCHAR(100),
            price DECIMAL(10,2),
            purchase_link TEXT,
            description TEXT,
            rating DECIMAL(3,1) DEFAULT 0,
            image_path VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS specifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            spec_name VARCHAR(150) NOT NULL,
            spec_value VARCHAR(255),
            spec_unit VARCHAR(50),
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_ratings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            rating INT CHECK (rating BETWEEN 1 AND 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    conn.commit()
    _ensure_categories(cursor, conn)
    cursor.close()
    conn.close()

#veri çekme fonksiyonları
def _ensure_categories(cursor, conn):
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] > 0:
        return
    cursor.execute("INSERT INTO categories (name, icon, description) VALUES (%s,%s,%s)",
                   ("Klavye", "⌨", "Mekanik ve membran klavyeler"))
    cursor.execute("INSERT INTO categories (name, icon, description) VALUES (%s,%s,%s)",
                   ("Mouse", "🖱", "Gaming ve ofis fareleri"))
    cursor.execute("INSERT INTO categories (name, icon, description) VALUES (%s,%s,%s)",
                   ("Kulaklık", "🎧", "Kablolu ve kablosuz kulaklıklar"))
    conn.commit()


def get_all_categories():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories ORDER BY id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_products_by_category(category_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id=c.id WHERE p.category_id=%s ORDER BY p.rating DESC",
        (category_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_all_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT p.*, c.name as category_name, c.icon as category_icon FROM products p JOIN categories c ON p.category_id=c.id ORDER BY c.id, p.rating DESC"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_product_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id=c.id WHERE p.id=%s",
        (product_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_specifications(product_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM specifications WHERE product_id=%s ORDER BY id",
        (product_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def search_products(keyword):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    like = f"%{keyword}%"
    cursor.execute(
        "SELECT p.*, c.name as category_name, c.icon as category_icon FROM products p JOIN categories c ON p.category_id=c.id WHERE p.name LIKE %s OR p.brand LIKE %s OR p.description LIKE %s ORDER BY p.rating DESC",
        (like, like, like)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def add_product(category_id, name, brand, price, purchase_link, description, rating):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (category_id, name, brand, price, purchase_link, description, rating) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (category_id, name, brand, price, purchase_link, description, rating)
    )
    conn.commit()
    pid = cursor.lastrowid
    cursor.close()
    conn.close()
    return pid


def update_product(product_id, name, brand, price, purchase_link, description, rating):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET name=%s, brand=%s, price=%s, purchase_link=%s, description=%s, rating=%s WHERE id=%s",
        (name, brand, price, purchase_link, description, rating, product_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()


def add_specification(product_id, spec_name, spec_value, spec_unit=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO specifications (product_id, spec_name, spec_value, spec_unit) VALUES (%s,%s,%s,%s)",
        (product_id, spec_name, spec_value, spec_unit)
    )
    conn.commit()
    cursor.close()
    conn.close()


def update_specification(spec_id, spec_name, spec_value, spec_unit=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE specifications SET spec_name=%s, spec_value=%s, spec_unit=%s WHERE id=%s",
        (spec_name, spec_value, spec_unit, spec_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


def delete_specification(spec_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM specifications WHERE id=%s", (spec_id,))
    conn.commit()
    cursor.close()
    conn.close()


def add_user_rating(product_id, rating, comment=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_ratings (product_id, rating, comment) VALUES (%s,%s,%s)",
        (product_id, rating, comment)
    )
    new_avg_q = "SELECT AVG(rating) FROM user_ratings WHERE product_id=%s"
    cursor.execute(new_avg_q, (product_id,))
    new_avg = cursor.fetchone()[0]
    cursor.execute("UPDATE products SET rating=%s WHERE id=%s", (round(new_avg, 1), product_id))
    conn.commit()
    cursor.close()
    conn.close()


def get_user_ratings(product_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM user_ratings WHERE product_id=%s ORDER BY created_at DESC",
        (product_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def toggle_favorite(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM favorites WHERE product_id=%s", (product_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("DELETE FROM favorites WHERE product_id=%s", (product_id,))
        result = False
    else:
        cursor.execute("INSERT INTO favorites (product_id) VALUES (%s)", (product_id,))
        result = True
    conn.commit()
    cursor.close()
    conn.close()
    return result


def is_favorite(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM favorites WHERE product_id=%s", (product_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row is not None


def get_favorites():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT p.*, c.name as category_name, c.icon as category_icon FROM products p JOIN categories c ON p.category_id=c.id JOIN favorites f ON f.product_id=p.id ORDER BY f.added_at DESC"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_stats():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as total FROM products")
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT c.name, COUNT(p.id) as cnt FROM categories c LEFT JOIN products p ON p.category_id=c.id GROUP BY c.id")
    by_cat = cursor.fetchall()
    cursor.execute("SELECT AVG(price) as avg_price, MIN(price) as min_price, MAX(price) as max_price FROM products")
    prices = cursor.fetchone()
    cursor.close()
    conn.close()
    return {"total": total, "by_category": by_cat, "prices": prices}