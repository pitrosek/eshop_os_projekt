
from flask import Flask, render_template, url_for, request, redirect, flash, session, g, send_from_directory
import sqlite3
import os
import os, sqlite3
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "eshop.db")

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, is_admin INTEGER DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, price REAL, img TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, total REAL, created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    c.execute("CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER, product_id INTEGER, quantity INTEGER, subtotal REAL)")
    conn.commit()

    # vloží admina, pokud chybí
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, 1)",
                  ("admin", generate_password_hash("admin")))
        conn.commit()

    # vloží demo produkty, pokud chybí
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        demo = [
            ("Tričko", "Bavlněné tričko s logem.", 299, "placeholder.png"),
            ("Mikina", "Teplá mikina s kapucí.", 799, "placeholder.png"),
            ("Čepice", "Zimní čepice.", 199, "placeholder.png")
        ]
        c.executemany("INSERT INTO products (name, description, price, img) VALUES (?, ?, ?, ?)", demo)
        conn.commit()

    conn.close()

# === Automatické vytvoření při startu ===
if not os.path.exists(DATABASE):
    print("⚙️  Inicializuji databázi (eshop.db)...")
    init_db()
    print("✅ Databáze vytvořena.")

from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "eshop.db")

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # Replace with secure key in production

# ---------- Database helpers ----------
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False, commit=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    if commit:
        get_db().commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db(populate=True):
    db = sqlite3.connect(DATABASE)
    c = db.cursor()
    c.executescript("""
    DROP TABLE IF EXISTS users;
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS order_items;
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    );
    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL,
        img TEXT
    );
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        total INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        price INTEGER,
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    );
    """)
    if populate:
        # add a default admin user (password: admin) and sample products
        admin_pw = generate_password_hash("admin")
        c.execute("INSERT INTO users (username, password, is_admin) VALUES (?,?,1)",
                  ("admin", admin_pw))
        products = [
            ("Tričko", "Pohodlné tričko z bavlny.", 299, "placeholder.png"),
            ("Mikina", "Teplá mikina s kapucí.", 799, "placeholder.png"),
            ("Čepice", "Stylová čepice.", 199, "placeholder.png")
        ]
        c.executemany("INSERT INTO products (name, description, price, img) VALUES (?,?,?,?)", products)
    db.commit()
    db.close()

# ---------- Auth helpers ----------
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    user = query_db("SELECT id, username, is_admin FROM users WHERE id = ?", (uid,), one=True)
    return user

def login_user(user_row):
    session["user_id"] = user_row["id"]

def logout_user():
    session.pop("user_id", None)

# ---------- Routes ----------
@app.route("/")
def home():
    products = query_db("SELECT * FROM products")
    return render_template("index.html", products=products, user=current_user())

@app.route("/product/<int:product_id>")
def product(product_id):
    item = query_db("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    return render_template("product.html", item=item, user=current_user())

@app.route("/add_to_cart/<int:product_id>", methods=["POST","GET"])
def add_to_cart(product_id):
    qty = int(request.form.get("quantity", 1))
    cart = session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + qty
    session["cart"] = cart
    flash("Přidáno do košíku.")
    return redirect(request.referrer or url_for("home"))

@app.route("/cart")
def cart():
    cart = session.get("cart", {})
    items = []
    total = 0
    if cart:
        ids = ",".join(cart.keys())
        placeholders = ",".join("?"*len(cart))
        rows = query_db(f"SELECT * FROM products WHERE id IN ({placeholders})", tuple(cart.keys()))
        for r in rows:
            pid = str(r["id"])
            qty = cart.get(pid,0)
            subtotal = r["price"] * qty
            items.append({"product": r, "qty": qty, "subtotal": subtotal})
            total += subtotal
    return render_template("cart.html", items=items, total=total, user=current_user())

@app.route("/cart/remove/<int:product_id>")
def cart_remove(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart
    flash("Odebráno z košíku.")
    return redirect(url_for("cart"))

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or not password:
            flash("Vyplňte uživatelské jméno i heslo.")
            return redirect(url_for("register"))
        hashed = generate_password_hash(password)
        try:
            db = get_db()
            db.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, hashed))
            db.commit()
            flash("Registrace úspěšná — nyní se přihlaste.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Uživatel s tímto jménem již existuje.")
            return redirect(url_for("register"))
    return render_template("register.html", user=current_user())

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = query_db("SELECT * FROM users WHERE username = ?", (username,), one=True)
        if user and check_password_hash(user["password"], password):
            login_user(user)
            flash("Přihlášení úspěšné.")
            return redirect(url_for("home"))
        else:
            flash("Špatné uživatelské jméno nebo heslo.")
            return redirect(url_for("login"))
    return render_template("login.html", user=current_user())

@app.route("/logout")
def logout():
    logout_user()
    flash("Odhlášeno.")
    return redirect(url_for("home"))

# Admin: manage products
def admin_required():
    user = current_user()
    if not user or user["is_admin"] != 1:
        flash("Přístup odepřen.")
        return False
    return True

@app.route("/admin/products")
def admin_products():
    if not admin_required():
        return redirect(url_for("login"))
    products = query_db("SELECT * FROM products")
    return render_template("admin_products.html", products=products, user=current_user())

@app.route("/admin/products/new", methods=["GET","POST"])
def admin_products_new():
    if not admin_required():
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form["name"]
        desc = request.form.get("description","")
        price = int(request.form["price"])
        img = request.form.get("img","placeholder.png")
        db = get_db()
        db.execute("INSERT INTO products (name, description, price, img) VALUES (?,?,?,?)", (name, desc, price, img))
        db.commit()
        flash("Produkt vytvořen.")
        return redirect(url_for("admin_products"))
    return render_template("admin_product_edit.html", product=None, user=current_user())

@app.route("/admin/products/edit/<int:product_id>", methods=["GET","POST"])
def admin_products_edit(product_id):
    if not admin_required():
        return redirect(url_for("login"))
    product = query_db("SELECT * FROM products WHERE id = ?", (product_id,), one=True)
    if request.method == "POST":
        name = request.form["name"]
        desc = request.form.get("description","")
        price = int(request.form["price"])
        img = request.form.get("img","placeholder.png")
        db = get_db()
        db.execute("UPDATE products SET name=?, description=?, price=?, img=? WHERE id=?", (name, desc, price, img, product_id))
        db.commit()
        flash("Produkt upraven.")
        return redirect(url_for("admin_products"))
    return render_template("admin_product_edit.html", product=product, user=current_user())

@app.route("/admin/products/delete/<int:product_id>", methods=["POST","GET"])
def admin_products_delete(product_id):
    if not admin_required():
        return redirect(url_for("login"))
    db = get_db()
    db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()
    flash("Produkt smazán.")
    return redirect(url_for("admin_products"))

# Simple checkout that creates an order (no payment integration)
@app.route("/checkout", methods=["POST"])
def checkout():
    user = current_user()
    if not user:
        flash("Pro dokončení nákupu se musíte přihlásit.")
        return redirect(url_for("login"))
    cart = session.get("cart", {})
    if not cart:
        flash("Košík je prázdný.")
        return redirect(url_for("cart"))
    total = 0
    for pid, qty in cart.items():
        row = query_db("SELECT price FROM products WHERE id = ?", (pid,), one=True)
        total += row["price"] * int(qty)
    db = get_db()
    cur = db.execute("INSERT INTO orders (user_id, total) VALUES (?,?)", (user["id"], total))
    order_id = cur.lastrowid
    for pid, qty in cart.items():
        row = query_db("SELECT price FROM products WHERE id = ?", (pid,), one=True)
        db.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?,?,?,?)",
                   (order_id, pid, qty, row["price"]))
    db.commit()
    session["cart"] = {}
    flash(f"Objednávka #{order_id} vytvořena, celkem {total} Kč.")
    return redirect(url_for("home"))

# Static files (images)
@app.route("/static/img/<path:filename>")
def static_img(filename):
    return send_from_directory(os.path.join(BASE_DIR, "static", "img"), filename)

# Admin/init helper route - create DB if missing
@app.route("/initdb")
def initdb_route():
    if os.path.exists(DATABASE):
        flash("DB already exists.")
        return redirect(url_for("home"))
    init_db(populate=True)
    flash("DB inicializována. Admin/admin by měl fungovat.")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
