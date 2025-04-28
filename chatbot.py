# Install required packages first
# pip install flask twilio pillow pytesseract flask_sqlalchemy googletrans==4.0.0-rc1 requests

from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from PIL import Image
import pytesseract
import os

from app.models import db, Buyer, Product
from app.utils import recognize_product, download_image, remove_file

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

user_language = {}

languages = {
    '1': 'Hindi',
    '2': 'Tamil',
    '3': 'Telugu',
    '4': 'Bengali',
    '5': 'English'
}

os.makedirs('uploads', exist_ok=True)

@app.route('/')
def home():
    return "Hello World! Server is working!"

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').strip().lower()
    from_number = request.values.get('From', '')
    media_url = request.values.get('MediaUrl0', '')
    resp = MessagingResponse()
    msg = resp.message()

    if from_number not in user_language:
        if incoming_msg in languages:
            user_language[from_number] = languages[incoming_msg]
            msg.body(f"You selected {user_language[from_number]} ✅\n\nReply with:\n1️⃣ Check Market Prices\n2️⃣ Find Buyers Nearby\n3️⃣ Get Selling Advice\n4️⃣ Contact Support")
        else:
            msg.body("🙏 Welcome to Market-Connect!\nChoose a language to continue:\n1. हिन्दी\n2. தமிழ்\n3. తెలుగు\n4. বাংলা\n5. English")
    else:
        if incoming_msg == '1' or media_url:
            if media_url:
                filename = download_image(media_url, from_number)
                if filename:
                    try:
                        image = Image.open(filename)
                        text = pytesseract.image_to_string(image)
                        recognized_product = recognize_product(text)
                        msg.body(f"📸 Product Identified: {recognized_product}")
                    except Exception:
                        msg.body("❌ Failed to process the image.")
                    finally:
                        remove_file(filename)
                else:
                    msg.body("❌ Failed to download the image.")
            else:
                msg.body("📈 Send the product name (e.g., 'Tomato') or upload a product photo 📸.")
        elif incoming_msg == '2':
            msg.body("🤝 Send the product name to find nearby buyers.")
        elif incoming_msg == '3':
            msg.body("💡 Selling Advice:\n- Best Day: Tuesday\n- Tip: Organic products have high demand.\n- Prices expected to rise next week! 📈")
        elif incoming_msg == '4':
            msg.body("📞 Contact Support:\nSend your message and our team will assist you.")
        elif incoming_msg in ['menu', 'main']:
            msg.body("🏠 Main Menu:\n1️⃣ Check Market Prices\n2️⃣ Find Buyers Nearby\n3️⃣ Get Selling Advice\n4️⃣ Contact Support")
        else:
            msg.body("❓ Sorry, I didn't understand.\nReply with 'menu' to go back to main options.")

    return str(resp)

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo uploaded'}), 400
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filepath = os.path.join('uploads', file.filename)
    file.save(filepath)

    try:
        image = Image.open(filepath)
        text = pytesseract.image_to_string(image)
    except Exception as e:
        remove_file(filepath)
        return jsonify({'error': 'Failed to process image', 'details': str(e)}), 500

    remove_file(filepath)
    recognized_product = recognize_product(text)

    return jsonify({'recognized_product': recognized_product, 'recognized_text': text})

@app.route('/mandi-prices', methods=['GET'])
def mandi_prices():
    products = Product.query.all()
    prices = {}
    for product in products:
        prices[product.name] = {
            'id': product.id,
            'price': product.price,
            'stock_quantity': product.stock_quantity
        }
    return jsonify(prices)

@app.route('/mandi-prices', methods=['POST'])
def add_product():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    stock_quantity = data.get('stock_quantity', 0)

    if not name or price is None:
        return jsonify({'error': 'Name and price are required'}), 400

    existing_product = Product.query.filter_by(name=name).first()
    if existing_product:
        return jsonify({'error': 'Product already exists'}), 400

    new_product = Product(name=name, price=price, stock_quantity=stock_quantity)
    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message': 'Product added successfully', 'id': new_product.id})

@app.route('/mandi-prices/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()
    price = data.get('price')
    stock_quantity = data.get('stock_quantity')

    if price is not None:
        product.price = price
    if stock_quantity is not None:
        product.stock_quantity = stock_quantity

    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})

@app.route('/mandi-prices/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})

@app.route('/buyers')
def get_buyers():
    buyers = Buyer.query.all()
    return jsonify([{ 'name': b.name, 'location': b.location, 'type': b.buyer_type, 'contact': b.contact } for b in buyers])

if __name__ == "__main__":
    app.run(debug=True)
