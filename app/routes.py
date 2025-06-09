from flask import Blueprint, request, jsonify
from . import db
from .models import Result

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok"}), 200

@api_bp.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()

    if not data or 'name' not in data or 'score' not in data:
        return jsonify({"error": "Missing 'name' or 'score' in request"}), 400

    try:
        name = data['name']
        score = int(data['score'])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid data format for 'score' or request body"}), 400

    new_result = Result(name=name, score=score)
    db.session.add(new_result)
    db.session.commit()

    return jsonify({"id": new_result.id, "message": "Result submitted successfully"}), 201

@api_bp.route('/results', methods=['GET'])
def get_results():
    results = Result.query.all()
    return jsonify([result.to_dict() for result in results]), 200