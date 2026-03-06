# flask 기본 
from flask import Flask, request, jsonify

app = Flask(__name__)

# home 홈
@app.route('/')
def home():
    return "<h1>Weather API Server</h1><p>Milestone 2 is Running</p>"

@app.route('/ingest', methods = ['POST'])
def ingest():
    # 쿼리 파라미터 가져오기 
    city = request.args.get('city')
    country = request.args.get('country')
    return jsonify({
        "status": "success",
        "message": f"Data for {city}, {country} are ready to be processed."
    }), 200

## 1. READ all (전체)
@app.route('/observations', methods=['GET'])
def get_all_observations():
    return jsonify({"message": "List of all observations"}), 200

## 3. READ one (일부: 여기서는 id)
@app.route('/observations/<int:id>', methods=['GET'])
def get_observation_by_id(id):
    return jsonify({"message": f"Details for observation {id}"}), 200

## 4. UPDATE
@app.route('/observations/<int:id>', methods=['PUT'])
def update_observation(id):
    return jsonify({"message": f"Observation {id} is updated"}), 200

## 5. DELETE
@app.route('/observations/<int:id>', methods=['DELETE'])
def delete_observation(id):
    return jsonify({"message": f"Observation {id} is deleted"}), 200
