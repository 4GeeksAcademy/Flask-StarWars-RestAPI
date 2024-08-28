import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User, People, Planet, FavoritePlanet, FavoritePeople
from utils import APIException

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://") if db_url else "sqlite:///tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

# Error Handler
@app.errorhandler(Exception)
def handle_exception(error):
    response = {
        "error": str(error)
    }
    status_code = 500
    if isinstance(error, APIException):
        response = error.to_dict()
        status_code = error.status_code
    return jsonify(response), status_code

# Root endpoint for sitemap
@app.route('/')
def sitemap():
    return jsonify({"msg": "API is working!"})

# People Routes
@app.route('/people', methods=['GET'])
def get_people_all():
    people = People.query.all()
    return jsonify({"people": [person.serialize() for person in people]})

@app.route('/people/<int:people_id>', methods=['GET'])
def get_people(people_id):
    person = People.query.get(people_id)
    if person:
        return jsonify({"person": person.serialize()})
    return jsonify({'error': "Person not found"}), 404

# Planets Routes
@app.route('/planets', methods=['GET'])
def get_planets_all():
    planets = Planet.query.all()
    return jsonify({"planets": [planet.serialize() for planet in planets]})

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify({"planet": planet.serialize()})
    return jsonify({'error': "Planet not found"}), 404

# Users Routes
@app.route('/users', methods=['GET'])
def get_users_all():
    users = User.query.all()
    return jsonify({"users": [user.serialize() for user in users]})

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': "User ID is required!"}), 400
    
    favorites_planets = FavoritePlanet.query.filter_by(user_id=user_id).all()
    favorites_people = FavoritePeople.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'favorites_planets': [fp.serialize() for fp in favorites_planets],
        'favorites_people': [fp.serialize() for fp in favorites_people]
    })

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': "User ID is required!"}), 400
    
    if FavoritePlanet.query.filter_by(user_id=user_id, planet_id=planet_id).first():
        return jsonify({'error': "Planet already in favorites"}), 400

    favorite = FavoritePlanet(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': "User ID is required!"}), 400
    
    if FavoritePeople.query.filter_by(user_id=user_id, people_id=people_id).first():
        return jsonify({'error': "Person already in favorites"}), 400

    favorite = FavoritePeople(user_id=user_id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': "User ID is required!"}), 400
    
    favorite = FavoritePlanet.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'message': "Favorite planet deleted!"}), 200
    return jsonify({'error': "Favorite planet not found!"}), 404

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': "User ID is required!"}), 400
    
    favorite = FavoritePeople.query.filter_by(user_id=user_id, people_id=people_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'message': "Favorite person deleted!"}), 200
    return jsonify({'error': "Favorite person not found!"}), 404

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)

