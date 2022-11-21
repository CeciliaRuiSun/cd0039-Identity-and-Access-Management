import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def get_drinks():
    try:
        drinks = Drink.query.all()

        drink_list = []

        for drink in drinks:
            drink_list.append(drink.short())
        

        return jsonify({
            'success': True,    
            'drinks': drink_list
        })

    except Exception as ex:
        print(ex)
        abort(401)

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    try:
        drinks = Drink.query.all()

        drink_list = []
        for drink in drinks:
            drink_list.append(drink.long())

        return jsonify({
            'success': True,    
            'drinks': drink_list
        })
    
    except:
        abort(401)

@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def add_drink():
    try:
        body = request.get_json()

        new_title = body.get("title", None)
        new_recipe = json.dumps(body.get("recipe", None))
        
        new_drink = Drink(title = new_title, recipe = new_recipe)
        new_drink.insert()

        return jsonify({
            'success': True,    
            'drinks': [new_drink.long()]
        })

    except Exception as ex:
        print(ex)
        abort(401)


@app.route('/drinks/<id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink(id):
    try:
        body = request.get_json()

        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        
        if not drink:
            abort(404)
        
        if new_title:
            drink.title = new_title
        if new_recipe:
            drink.recipe = new_recipe
        
        drink.update()
        
        return jsonify({
            'success': True,    
            'drinks': [drink.long()]
        })

    except Exception as ex:
        print(ex)
        abort(401)

@app.route('/drinks/<id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        
        if not drink:
            abort(404)
        
        drink.delete()
        
        return jsonify({
            'success': True,    
            'drinks': id
        })

    except Exception as ex:
        print(ex)
        abort(401)


# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, 
        "error": 404, 
        "message": "resource not found"}),
        404,
    )

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    return jsonify({
        "success": False,
        "error": ex.status_code,
        'message': ex.error
    }), 401


