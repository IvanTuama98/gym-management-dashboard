import os
import sqlite3
from flask import Flask, render_template, url_for, request, redirect, session, flash
from dotenv import load_dotenv
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from translations import TRANSLATIONS
app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')


@app.route("/")
def index():
    user_id = session.get("user_id")
    if not user_id:
        return render_template("welcome.html")

    #Connection to the Database
    conn = sqlite3.connect("gym.db")
    db = conn.cursor()


    row = db.execute("""
        SELECT COUNT(DISTINCT client_id) 
        FROM payments 
        WHERE user_id = ? 
        AND (julianday('now') - julianday(payment_date)) <= 30
    """, (user_id,)).fetchone()
    active_clients = row[0] if row and row[0] is not None else 0

    row = db.execute("SELECT SUM(amount) FROM payments WHERE user_id = ?", (user_id,)).fetchone()
    total_revenue = row[0] if row and row[0] is not None else 0.0

    row = db.execute("""
        SELECT SUM(amount) 
        FROM payments 
        WHERE user_id = ? 
        AND strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')
    """, (user_id,)).fetchone()

    monthly_earnings = row[0] if row and row[0] is not None else 0.0

    conn.close()

    return render_template(
        "index.html", 
        active_clients=active_clients,
        monthly_earnings=monthly_earnings,
        total_revenue=total_revenue, 
    )

# ---------------------------------------------------------
# Register page
# ---------------------------------------------------------

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == 'POST':

        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if not username or not password or not confirm_password:
            flash("Missing username/password.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("The passwords do not match.", "error")
            return render_template("register.html")

        try:
            conn = sqlite3.connect("gym.db")
            db = conn.cursor()

            # Hash password
            hash_password = generate_password_hash(password)

            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash_password))

            user_id = db.lastrowid

            conn.commit()
            conn.close()

            session["user_id"] = user_id
            return redirect("/")

        except sqlite3.IntegrityError:
            conn.close()
            flash("Username already exists")
            return render_template("register.html")
        
    else:
        return render_template("register.html")

# ---------------------------------------------------------
# Login page
# ---------------------------------------------------------

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Missing username/password.", "error")
            return render_template("login.html")

        conn = sqlite3.connect("gym.db")
        conn.row_factory = sqlite3.Row
        db = conn.cursor()

        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        conn.close()

        if not user or not check_password_hash(user["hash"], password):
            flash("User does not exists.")
            return render_template("login.html")

        session["user_id"] = user[0]
        return redirect("/")


    else:
        return render_template("login.html")

# ---------------------------------------------------------
# Log out
# ---------------------------------------------------------

@app.route("/logout")
def logout():
    session.clear()
    flash("The session has been closed.")
    return redirect("/")

@app.route("/clients/add", methods=["GET","POST"])
def add_client():
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")

        if not name:
            flash("Name is empty.", "error")
            return render_template("add_client.html")

        user_id = session.get("user_id")
        if not user_id:
            return redirect("/login")

        now = datetime.today()
        registration_date = now.strftime("%Y-%m-%d")

        conn = sqlite3.connect("gym.db")
        db = conn.cursor()

        db.execute("INSERT INTO clients (user_id, name, phone, registration_date, status) VALUES (?, ?, ?, ?, 'active')", (user_id, name, phone, registration_date))

        conn.commit()
        conn.close()
        flash("The client has been registered successfully.")
        return redirect("/")

    else:
        return render_template("add_client.html")

# ---------------------------------------------------------
# Clients
# ---------------------------------------------------------

@app.route("/clients", methods=["GET"])
def clients():
    user_id = session.get("user_id")
    if not user_id:
        flash("You must log in in order to see the clients.", "error")
        return redirect("/login")

    conn = sqlite3.connect("gym.db")
    db = conn.cursor()

    raw_clients = db.execute("""
        SELECT c.id, c.name, c.phone, c.registration_date, MAX(p.payment_date)
        FROM clients c
        LEFT JOIN payments p ON c.id = p.client_id
        WHERE c.user_id = ?
        GROUP BY c.id
        ORDER BY c.id DESC
    """, (user_id,)).fetchall()
    
    conn.close()

    today = datetime.now().date()
    clients_list = []

    for client in raw_clients:
        client_id, name, phone, reg_date, last_payment = client
        
        if last_payment:
            payment_date = datetime.strptime(last_payment, "%Y-%m-%d").date()
            is_active = (today - payment_date).days <= 30
        else:
            is_active = False

        clients_list.append({
            "id": client_id,
            "name": name,
            "phone": phone,
            "registration_date": reg_date,
            "last_payment": last_payment or "No payments",
            "status": "Active" if is_active else "Overdue",
            "badge": "bg-success" if is_active else "bg-danger"
        })

    return render_template("clients.html", clients=clients_list)

# ---------------------------------------------------------
# Edit specific client by their id
# ---------------------------------------------------------

@app.route("/clients/edit/<int:id>", methods=["GET", "POST"])
def edit_client(id):

    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    conn = sqlite3.connect("gym.db")
    conn.row_factory = sqlite3.Row
    db = conn.cursor()

    client = db.execute("SELECT * FROM clients WHERE id = ? and user_id = ?", (id, user_id)).fetchone()
    if not client:
        flash("Client not found.", "error")
        conn.close()
        return redirect("/clients")

    if request.method == "POST":
        
        name = request.form.get("name").strip()
        if not name:
            flash("You must provide a name", "error")
            conn.close()
            return redirect(f"/clients/edit/{id}")
        
        phone = request.form.get("phone").strip()
        
        db.execute("UPDATE clients SET name = ?, phone = ? WHERE id = ? and user_id = ?", (name, phone, id, user_id))
        conn.commit()
        conn.close()
        flash("Client updated successfully!", "success")
        return redirect("/clients")

    else:
        conn.close()
        return render_template("edit_client.html", client=client)

# ---------------------------------------------------------
# Delete specific client
# ---------------------------------------------------------

@app.route("/clients/delete/<int:id>", methods=["POST"])
def delete_client(id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    conn = sqlite3.connect("gym.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    db = conn.cursor()

    db.execute("DELETE FROM clients WHERE id = ? AND user_id = ?", (id, user_id))

    conn.commit()
    conn.close()

    flash("Client deleted correctly.", "warning")
    return redirect("/clients")

# ---------------------------------------------------------
# Settings for the gym
# ---------------------------------------------------------

@app.route("/settings", methods=["GET", "POST"])
def settings():

    user_id = session.get("user_id")
    if not user_id:
        flash("You must log in in order to see the clients.", "error")
        return redirect("/login")

    conn = sqlite3.connect("gym.db")
    conn.row_factory = sqlite3.Row
    db = conn.cursor()

    if request.method == "POST":
        monthly_fee = request.form.get("monthly_fee")
        due_day = request.form.get("due_day")
        late_fee = request.form.get("late_fee")

        db.execute("UPDATE users SET monthly_fee = ?, due_day = ?, late_fee = ? WHERE id = ?", (monthly_fee, due_day, late_fee, user_id))
        conn.commit()
        conn.close()
        flash("Changes has been made successfully.")
        return redirect("/settings")

    else:
        settings = db.execute("SELECT monthly_fee, due_day, late_fee FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return render_template("settings.html", settings=settings)

# ---------------------------------------------------------
# Payment using the dashboard
# ---------------------------------------------------------
@app.route("/add_payment", methods=["GET", "POST"])
@app.route("/payments/add/<int:client_id>", methods=["GET", "POST"])
def add_payment(client_id=None):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    conn = sqlite3.connect("gym.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    db = conn.cursor()

    if request.method == "POST":
        selected_client_id = request.form.get("client_id")
        amount = request.form.get("amount")
        payment_date = datetime.now().strftime("%Y-%m-%d")
        month_covered = datetime.now().strftime("%B %Y")

        if not selected_client_id or not amount:
            flash("Please complete all required fields.", "danger")
            conn.close()
            return redirect(request.referrer or "/add_payment")

        db.execute("""
            INSERT INTO payments (user_id, client_id, amount, payment_date, month_covered)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, selected_client_id, amount, payment_date, month_covered))

        conn.commit()
        conn.close()

        flash("Payment registered successfully!", "success")
        return redirect("/")

    else:
        clients = db.execute(
            "SELECT id, name FROM clients WHERE user_id = ? ORDER BY name ASC",
            (user_id,)
        ).fetchall()

        if not clients:
            conn.close()
            flash("You need to register at least one client before adding a payment.", "warning")
            return redirect("/clients/add")

        # Obtener la cuota base y el recargo guardados en Settings
        user_row = db.execute("SELECT monthly_fee, late_fee FROM users WHERE id = ?", (user_id,)).fetchone()
        monthly_fee = user_row[0] if user_row and user_row[0] is not None else 0
        late_fee = user_row[1] if user_row and user_row[1] is not None else 0

        suggested_amount = monthly_fee

        if client_id:
            last_payment = db.execute("""
                SELECT payment_date FROM payments 
                WHERE user_id = ? AND client_id = ? 
                ORDER BY payment_date DESC LIMIT 1
            """, (user_id, client_id)).fetchone()

            if last_payment:
                last_date = datetime.strptime(last_payment[0], "%Y-%m-%d")
                days_diff = (datetime.now() - last_date).days
                
                if days_diff > 30:
                    suggested_amount = monthly_fee + late_fee
            else:
                suggested_amount = monthly_fee + late_fee

        conn.close()

        return render_template(
            "add_payment.html", 
            clients=clients, 
            suggested_amount=suggested_amount,
            selected_client_id=client_id
        )

# ---------------------------------------------------------
# Add payment for specific client 
# ---------------------------------------------------------

@app.route("/payments/add/<int:client_id>", methods=["GET", "POST"])
def add_payment_for_client(client_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    conn = sqlite3.connect("gym.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    db = conn.cursor()

    client = db.execute(
        "SELECT id, user_id, name FROM clients WHERE id = ? AND user_id = ?", 
        (client_id, user_id)
    ).fetchone()

    if not client:
        conn.close()
        flash("Cliente no encontrado.", "danger")
        return redirect("/clients")

    if request.method == "POST":
        amount = request.form.get("amount")
        payment_date = datetime.now().strftime("%Y-%m-%d")
        month_covered = datetime.now().strftime("%B %Y")

        if not amount:
            flash("Ingresa un monto válido.", "danger")
            conn.close()
            return redirect(f"/payments/add/{client_id}")

        db.execute("""
            INSERT INTO payments (user_id, client_id, amount, payment_date, month_covered)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, client_id, amount, payment_date, month_covered))

        conn.commit()
        conn.close()

        flash(f"¡Payment registered for {client[2]}!", "success")
        return redirect("/clients")

    else:
        row = db.execute("SELECT monthly_fee FROM users WHERE id = ?", (user_id,)).fetchone()
        suggested_amount = row[0] if row and row[0] is not None else 0

        conn.close()

        return render_template(
            "add_payment.html", 
            client=client, 
            suggested_amount=suggested_amount
        )

# ---------------------------------------------------------
# Payments page
# ---------------------------------------------------------

@app.route("/payments", methods=["GET"])
def payments_history():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    conn = sqlite3.connect("gym.db")
    conn.row_factory = sqlite3.Row
    db = conn.cursor()

    query = """
        SELECT 
            p.id,
            c.name AS client_name,
            p.amount,
            p.payment_date,
            p.month_covered
        FROM payments p
        INNER JOIN clients c ON p.client_id = c.id
        WHERE p.user_id = ?
        ORDER BY p.payment_date DESC, p.id DESC
    """
    
    payments = db.execute(query, (user_id,)).fetchall()
    conn.close()

    return render_template("payments.html", payments=payments)

@app.route("/set_language/<lang>")
def set_language(lang):
    if lang in ['es', 'en']:
        session['lang'] = lang
        return redirect(request.referrer or url_for('index'))

@app.context_processor
def inject_translations():
    def get_text(key):
        lang = session.get('lang', 'es')

        return TRANSLATIONS.get(lang, {}).get(key, key)

    return dict(get_text=get_text)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

# Run in terminal:
# $env:FLASK_DEBUG=1
# python -m flask run