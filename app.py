import os
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Конфигурация Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_to_telegram(order):
    """Отправка сообщения в Telegram"""
    message = (
        f"📦 *Новый заказ!*\n"
        f"👤 *Имя:* {order['customerName']}\n"
        f"📧 *Email:* {order['customerEmail']}\n"
        f"🍯 *Товар:* {order['product']}\n"
        f"⚖️ *Количество:* {order['quantity']} кг"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, json=payload)
    return response.ok


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/order', methods=['POST'])
def order():
    data = request.get_json()
    product = data.get('product')
    quantity = data.get('quantity')
    customer_name = data.get('customerName')
    customer_email = data.get('customerEmail')

    # Логирование заказа на сервере
    print(f"Новый заказ: {customer_name} ({customer_email}) заказал {quantity} кг {product}")

    # Отправка в Telegram
    order_data = {
        'product': product,
        'quantity': quantity,
        'customerName': customer_name,
        'customerEmail': customer_email
    }
    if send_to_telegram(order_data):
        return jsonify({'message': f'Спасибо, {customer_name}! Ваш заказ на {quantity} кг {product} принят и отправлен менеджеру.'})
    else:
        return jsonify({'message': 'Ошибка при отправке заказа менеджеру. Попробуйте снова.'}), 500

# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Получаем PORT из окружения или используем 5000
    app.run(host='0.0.0.0', port=port)