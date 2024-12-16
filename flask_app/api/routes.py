from flask import jsonify
from . import api_bp


@api_bp.route('/data')
def get_data():
    return jsonify({"message": "This is an API route."})

