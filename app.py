import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import requests

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, json=payload)
    return response.ok


def prepare_order_message(order):
    message = (
        f"📦 *Нове замовлення!*\n"
        f"👤 *Ім'я:* {order['customerName']}\n"
        f"📱 *Телефон:* {order['customerPhone']}\n"
        f"🏠 *Адреса доставки:* {order['customerAddress']}\n"
        f"🍯 *Товар:* {order['product']}\n"
        f"⚖️ *Об'єм:* {order['quantity']}\n"
        f"💬 *Коментар:* {order['comment'] if order['comment'] else 'Немає коментаря'}\n"
        f"🕒 *Час замовлення:* {order['timestamp']}"
    )
    return message


def prepare_customer_message(customer):
    message = (
        f"✉️ *Нове повідомлення від користувача!*\n"
        f"👤 *Ім'я:* {customer['customerName']}\n"
        f"📧 *Email:* {customer['customerEmail']}\n"
        f"💬 *Повідомлення:* {customer['customerMessage']}\n"
        f"🕒 *Час надсилання:* {customer['timestamp']}"
    )
    return message


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        json_path = os.path.join(os.getcwd(), 'products.json')
        with open(json_path, 'r', encoding='utf-8') as file:
            products = json.load(file)
        return jsonify(products), 200
    except FileNotFoundError:
        return jsonify({"error": "Файл products.json не знайдений"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/order', methods=['POST'])
def order():
    try:
        data = request.get_json()
        product = data.get('orderProduct')
        quantity = data.get('orderQuantity')
        customer_name = data.get('orderCustomerName')
        customer_phone = data.get('orderCustomerPhone')
        customer_address = data.get('orderCustomerAddress')
        comment = data.get('orderCustomerComment', '')

        if not all([product, quantity, customer_name, customer_phone, customer_address]):
            return jsonify({'message': '❌ Всі поля (товар, об\'єм, ім\'я, телефон, адреса) обов\'язкові для заповнення.'}), 400

        # Отримання часу замовлення
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Логування замовлення на сервері
        print(f"[{timestamp}] Нове замовлення: {customer_name} | {product} | {quantity} кг | {customer_phone} | {customer_address} | {comment}")

        # Отправка в Telegram
        order_data = {
            'customerName': customer_name,
            'customerEmail': data.get('customerEmail', 'Не вказано'),
            'product': product,
            'quantity': quantity,
            'customerPhone': customer_phone,
            'customerAddress': customer_address,
            'comment': comment,
            'timestamp': timestamp
        }

        prepared_order_message = prepare_order_message(order_data)
        if send_to_telegram(prepared_order_message):
            return jsonify({
                'message': f'✅ Дякуємо, {customer_name}! Ваше замовлення на {product} {quantity} прийняте та відправлене менеджеру.'
            })
        else:
            return jsonify({'message': '❌ Помилка при відправці замовлення менеджеру. Спробуйте знову.'}), 500

    except Exception as e:
        print(f"❌ Сталася помилка: {e}")
        return jsonify({'message': '❌ Внутрішня помилка сервера. Спробуйте пізніше.'}), 500


@app.route('/contactUs', methods=['POST'])
def contact_us():
    try:
        data = request.get_json()
        customer_name = data.get('customerName')
        customer_email = data.get('customerEmail')
        customer_message = data.get('customerMessage')

        # Отримання часу надсилання
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Логування повідомлення на сервері
        print(f"[{timestamp}] Нове повідомлення: {customer_name} ({customer_email}) написав повідомлення: {customer_message}")

        customer_data = {
            'customerName': customer_name,
            'customerEmail': customer_email,
            'customerMessage': customer_message,
            'timestamp': timestamp
        }

        prepared_message = prepare_customer_message(customer_data)
        if send_to_telegram(prepared_message):
            return jsonify({'message': f'✅ Дякуємо за звернення, {customer_name}! Ваше повідомлення успішно надіслано! Ми зв’яжемося з вами найближчим часом.'})
        else:
            return jsonify({'message': '❌ Помилка при відправці повідомлення. Cпробуйте знову.'}), 500
    except Exception as e:
        print(f"❌ Сталася помилка: {e}")
    return jsonify({'message': '❌ Внутрішня помилка сервера. Спробуйте пізніше.'}), 500


# if __name__ == '__main__':
#     app.run(debug=True)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)