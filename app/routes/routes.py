from flask import Blueprint, jsonify

app = Blueprint('main', __name__)

@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'})

@app.route('/about')
def about():
    return jsonify({'message': 'About page'})


#Ejemplo QUERY JSON field:
# data = Target.query.order_by(Target.product['salesrank'])