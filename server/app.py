#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)

    if restaurant:
        restaurant_data = {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'restaurant_pizzas': [
                {
                    'id': rp.id,
                    'price': rp.price,
                    'pizza': {
                        'id': rp.pizza.id,
                        'name': rp.pizza.name,
                        'ingredients': rp.pizza.ingredients
                    }
                }
                for rp in restaurant.restaurant_pizzas
            ]
        }
        return jsonify(restaurant_data), 200
    else:
        return jsonify({"error": "Restaurant not found"}), 404

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else:
        return jsonify({"error": "Restaurant not found"}), 404


@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])

@app.route('/restaurant_pizzas', methods=['GET', 'POST'])
def restaurant_pizzas():
    if request.method == 'GET':
        restaurant_pizzas = RestaurantPizza.query.all()
        return jsonify([rp.to_dict() for rp in restaurant_pizzas]), 200

    data = request.get_json()
    try:
        # Validate and retrieve associated Pizza and Restaurant
        pizza = Pizza.query.get(data.get('pizza_id'))
        restaurant = Restaurant.query.get(data.get('restaurant_id'))

        if not pizza or not restaurant:
            return jsonify({"errors": ["Pizza or Restaurant not found"]}), 404

        #validate price
        price = data.get('price')
        if not (1 <= price <= 30):
            return jsonify({"errors": ["Price must be between 1 and 30"]}), 400

        new_restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza.id,
            restaurant_id=restaurant.id
        )

        db.session.add(new_restaurant_pizza)
        db.session.commit()

        return jsonify(new_restaurant_pizza.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 500


if __name__ == '__main__':
    app.run(port=5555, debug=True)



