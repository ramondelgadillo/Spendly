from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

DB_FILE = "expenses.db"

# Connect to the database
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Create the expenses table if it doesn't exist
def init_db():
    if not os.path.exists(DB_FILE):
        conn = get_db_connection()
        conn.execute("""
            CREATE TABLE expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

# Home page: display list of expenses (newest first) + total
@app.route("/")
def index():
    category_filter = request.args.get("category")

    conn = get_db_connection()
    
    if category_filter and category_filter != "All":
        expenses = conn.execute(
            "SELECT * FROM expenses WHERE category = ? ORDER BY date DESC",
            (category_filter,)
        ).fetchall()
    else:
        expenses = conn.execute(
            "SELECT * FROM expenses ORDER BY date DESC"
        ).fetchall()

    total = conn.execute("SELECT SUM(amount) FROM expenses").fetchone()[0] or 0

    category_summary = conn.execute("""
        SELECT category, SUM(amount) as total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        category_summary=category_summary,
        selected_category=category_filter or "All"
    )


# Add expense page: GET (form) and POST (submit)
@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        name = request.form["name"]
        amount = request.form["amount"]
        category = request.form["category"]

        if not name or not amount or not category:
            return "All fields are required", 400

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO expenses (name, amount, category, date) VALUES (?, ?, ?, ?)",
            (name, float(amount), category, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add_expense.html")

# Delete a single expense
@app.route("/delete/<int:id>", methods=["POST"])
def delete_expense(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# Edit an expense
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_expense(id):
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form["name"]
        amount = request.form["amount"]
        category = request.form["category"]

        if not name or not amount or not category:
            return "All fields are required", 400

        conn.execute(
            "UPDATE expenses SET name = ?, amount = ?, category = ?, date = ? WHERE id = ?",
            (name, float(amount), category, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    # GET request – pre-fill the form
    expense = conn.execute("SELECT * FROM expenses WHERE id = ?", (id,)).fetchone()
    conn.close()

    if expense is None:
        return "Expense not found", 404

    return render_template("edit_expense.html", expense=expense)


# Initialize database and run app
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
