from flask import Blueprint, request, jsonify, abort
from .models import db, User
from .app import csrf  # Import the CSRF extension

api = Blueprint('api', __name__, url_prefix='/api/users')
csrf.exempt(api)  # Exempt the entire API blueprint from CSRF protection


@api.route('', methods=['GET'])
def get_users():
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=2, type=int)

    users_query = User.query.paginate(page=page, per_page=limit, error_out=False)
    users = users_query.items

    return jsonify({
        'page': page,
        'limit': limit,
        'total': users_query.total,
        'pages': users_query.pages,
        'data': [{'id': u.id, 'name': u.name} for u in users]
    })


@api.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'name': user.name})


@api.route('', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Missing name'}), 400
    user = User(name=data['name'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'name': user.name}), 201


@api.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Missing name'}), 400
    user.name = data['name']
    db.session.commit()
    return jsonify({'id': user.id, 'name': user.name})


@api.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204