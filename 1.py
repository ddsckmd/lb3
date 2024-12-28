from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

# Каталог товару
catalog = {
    1: {"name": "Apples", "type": "fruit", "price": 35.00, "weight": "1 kg"},
    2: {"name": "Bananas", "type": "fruit", "price": 30.00, "weight": "1 kg"},
    3: {"name": "Carrots", "type": "vegetable", "price": 25.00, "weight": "1 kg"},
    4: {"name": "Potatoes", "type": "vegetable", "price": 20.00, "weight": "1 kg"},
    5: {"name": "Chicken Breast", "type": "meat", "price": 120.00, "weight": "1 kg"},
    6: {"name": "Pork Loin", "type": "meat", "price": 150.00, "weight": "1 kg"},
    7: {"name": "Rice", "type": "grain", "price": 50.00, "weight": "1 kg"},
    8: {"name": "Flour", "type": "grain", "price": 40.00, "weight": "1 kg"},
    9: {"name": "Milk", "type": "dairy", "price": 25.00, "weight": "1 liter"},
    10: {"name": "Cheese", "type": "dairy", "price": 200.00, "weight": "1 kg"},
}


# Дані для авторизації
users = {
    "admin": "admpass",
    "user": "uspass"
}

# Авторизація
@auth.get_password
def get_password(username):
    return users.get(username)



# Ендпоінт для роботи з усім каталогом
@app.route('/items', methods=['GET', 'POST'])
@auth.login_required  # Спочатку авторизація перед доступом
def manage_items():
    if request.method == 'GET':
        return jsonify(catalog)  # Каталог у форматі JSON

    elif request.method == 'POST':
        new_item = request.json  # Дані з боді в JSON

        # Чи усе передалось
        if not new_item or "id" not in new_item or "name" not in new_item or "type" not in new_item or "price" not in new_item or "weight" not in new_item:
            return jsonify({"error": "Invalid data"}), 400
        item_id = new_item["id"]
        if item_id in catalog:  # Перевірка чи є товар з таким id
            return jsonify({"error": "Товар вже представлено"}), 400
        catalog[item_id] = {
            "name": new_item["name"],
            "type": new_item["type"],
            "price": new_item["price"],
            "weight": new_item["weight"]
        }  # Щоб додати новий товар
        return jsonify({"message": "Товар успішно додано!"}), 201



# Ендпоінт для роботи з конкретним товаром
@app.route('/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def manage_item(item_id):
    if item_id not in catalog:
        return jsonify({"error": "Не знайдено"}), 404

    if request.method == 'GET':
        return jsonify(catalog[item_id])  # Дані про товар з конкретним ID


    elif request.method == 'PUT':
        update_data = request.json



        if not update_data or "name" not in update_data or "type" not in update_data or "price" not in update_data or "weight" not in update_data:
            return jsonify({"error": "Invalid data"}), 400
        catalog[item_id] = {
            "name": update_data["name"],
            "type": update_data["type"],
            "price": update_data["price"],
            "weight": update_data["weight"]
        }  # Оновлення інформації про товар
        return jsonify({"message": "Товар успішно змінено!"})

    elif request.method == 'DELETE':
        del catalog[item_id]  # Видалення товару
        return jsonify({"message": "Товар успішно видалено!"})

if __name__ == '__main__':
    app.run(debug=True)