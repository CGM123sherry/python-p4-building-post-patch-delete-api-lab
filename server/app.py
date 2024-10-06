#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(  bakeries,   200  )

@app.route('/bakeries/<int:id>')
def bakery_by_id(id):

    bakery = Bakery.query.filter_by(id=id).first()
    bakery_serialized = bakery.to_dict()
    return make_response ( bakery_serialized, 200  )

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response( baked_goods_by_price_serialized, 200  )
   

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response( most_expensive_serialized,   200  )


# Route to create a new baked good
@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    # Retrieve form data from the request
    name = request.form.get('name')
    price = request.form.get('price')
    bakery_id = request.form.get('bakery_id')

    # Create a new baked good
    new_baked_good = BakedGood(name=name, price=price, bakery_id=bakery_id)

    # Add to the database and commit
    db.session.add(new_baked_good)
    db.session.commit()

    # Return the new baked good as JSON
    return jsonify({
        'id': new_baked_good.id,
        'name': new_baked_good.name,
        'price': new_baked_good.price,
        'bakery_id': new_baked_good.bakery_id
    }), 201


# Route to update the name of a bakery
@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    # Find the bakery by ID
    bakery = Bakery.query.get(id)
    if not bakery:
        return jsonify({'error': 'Bakery not found'}), 404

    # Update the bakery's name from the form data
    name = request.form.get('name')
    if name:
        bakery.name = name

    # Save changes to the database
    db.session.commit()

    # Return the updated bakery as JSON
    return jsonify({
        'id': bakery.id,
        'name': bakery.name
    }), 200


# Route to delete a baked good
@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    # Find the baked good by ID
    baked_good = BakedGood.query.get(id)
    if not baked_good:
        return jsonify({'error': 'Baked good not found'}), 404

    # Delete the baked good from the database
    db.session.delete(baked_good)
    db.session.commit()

    # Return a confirmation message
    return jsonify({'message': f'Baked good with id {id} was successfully deleted'}), 200




if __name__ == '__main__':
    app.run(port=5555, debug=True)