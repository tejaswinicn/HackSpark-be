from flask import Flask, request, jsonify
from flask_cors import CORS
from bson.objectid import ObjectId
from db.connection import init_db
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize MongoDB
db = init_db()
users_collection = db['users']

# Convert MongoDB document to JSON serializable
def serialize_user(user):
    return {
        "_id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "age": user["age"]
    }

# GET all users
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        users = list(users_collection.find())
        return jsonify([serialize_user(user) for user in users]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch users', 'details': str(e)}), 500

# POST create user
@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        new_user = users_collection.insert_one(data)
        created_user = users_collection.find_one({"_id": new_user.inserted_id})
        return jsonify({'message': 'User created', 'user': serialize_user(created_user)}), 201
    except Exception as e:
        return jsonify({'error': 'Failed to create user', 'details': str(e)}), 400

# PUT update user
@app.route('/api/users/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.json
        updated_user = users_collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": data},
            return_document=True
        )
        if not updated_user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'message': 'User updated', 'user': serialize_user(updated_user)}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update user', 'details': str(e)}), 400

# DELETE user
@app.route('/api/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        deleted_user = users_collection.find_one_and_delete({"_id": ObjectId(user_id)})
        if not deleted_user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'message': 'User deleted'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to delete user', 'details': str(e)}), 500

# Logging setup
logging.basicConfig(level=logging.INFO)

# Run app
if __name__ == '__main__':
    app.run(debug=True, port=3002)
