from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
import sqlite3

# Ініціалізація Flask і авторизації
app = Flask(__name__)
auth = HTTPBasicAuth()

# Ініціалізація SQLite бази даних
DB_FILE = "store.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Таблиця для каталогу товарів
    cursor.execute('''CREATE TABLE IF NOT EXISTS catalog (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        type TEXT NOT NULL,
                        price REAL NOT NULL,
                        weight TEXT NOT NULL
                    )''')

    # Таблиця для користувачів
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL
                    )''')

    # Додавання початкових даних, якщо таблиці порожні
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO users (username, password) VALUES (?, ?)",
                           [("admin", "admpass"), ("user", "uspass")])

    cursor.execute("SELECT COUNT(*) FROM catalog")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO catalog (id, name, type, price, weight) VALUES (?, ?, ?, ?, ?)", [
            (1, "Apples", "fruit", 35.00, "1 kg"),
            (2, "Bananas", "fruit", 30.00, "1 kg"),
            (3, "Carrots", "vegetable", 25.00, "1 kg"),
            (4, "Potatoes", "vegetable", 20.00, "1 kg"),
            (5, "Chicken Breast", "meat", 120.00, "1 kg"),
            (6, "Pork Loin", "meat", 150.00, "1 kg"),
            (7, "Rice", "grain", 50.00, "1 kg"),
            (8, "Flour", "grain", 40.00, "1 kg"),
            (9, "Milk", "dairy", 25.00, "1 liter"),
            (10, "Cheese", "dairy", 200.00, "1 kg")
        ])

    conn.commit()
    conn.close()

# Виклик ініціалізації бази даних
init_db()

# Завантаження користувача для авторизації
@auth.get_password
def get_password(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Ендпоінт для роботи з усім каталогом
@app.route('/items', methods=['GET', 'POST'])
@auth.login_required
def manage_items():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT * FROM catalog")
        items = cursor.fetchall()
        conn.close()
        return jsonify({item[0]: {"name": item[1], "type": item[2], "price": item[3], "weight": item[4]} for item in items})

    elif request.method == 'POST':
        new_item = request.json
        if not new_item or "id" not in new_item or "name" not in new_item or "type" not in new_item or "price" not in new_item or "weight" not in new_item:
            return jsonify({"error": "Invalid data"}), 400

        try:
            cursor.execute("INSERT INTO catalog (id, name, type, price, weight) VALUES (?, ?, ?, ?, ?)",
                           (new_item["id"], new_item["name"], new_item["type"], new_item["price"], new_item["weight"]))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({"error": "Товар вже представлено"}), 400

        conn.close()
        return jsonify({"message": "Товар успішно додано!"}), 201

# Ендпоінт для роботи з конкретним товаром
@app.route('/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def manage_item(item_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM catalog WHERE id = ?", (item_id,))
    item = cursor.fetchone()

    if not item:
        conn.close()
        return jsonify({"error": "Item not found"}), 404

    if request.method == 'GET':
        conn.close()
        return jsonify({"name": item[1], "type": item[2], "price": item[3], "weight": item[4]})

    elif request.method == 'PUT':
        update_data = request.json
        if not update_data or "name" not in update_data or "type" not in update_data or "price" not in update_data or "weight" not in update_data:
            conn.close()
            return jsonify({"error": "Invalid data"}), 400

        cursor.execute("UPDATE catalog SET name = ?, type = ?, price = ?, weight = ? WHERE id = ?",
                       (update_data["name"], update_data["type"], update_data["price"], update_data["weight"], item_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Товар успішно змінено!"})

    elif request.method == 'DELETE':
        cursor.execute("DELETE FROM catalog WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Товар успішно видалено!"})

if __name__ == '__main__':
    app.run(debug=True)
