from flask import Flask

app = Flask(__name__)

# home 홈 <전체관리용>
@app.route('/')
def home():
    return "<h1>Weather API Server</h1><p>Milestone 2 is Running</p>"

# 1. READ (전체)
@app.route('/weather', methods=['GET'])
def get_all_weather():
    return "List of all weather records."


# 2. READ (상세내용)
@app.route('/weather/<int:id>', methods=['GET'])
def get_weather(id):
    return f"Details for weather record {id}"

# 3. CREATE
@app.route('/weather', methods=['POST'])
def create_weather():
    return "Weather record created.", 201


# 4. UPDATE
@app.route('/weather/<int:id>', methods=['PUT', 'POST'])
def update_weather(id):
    return f"Weather record {id} updated."

# 5. DELETE
@app.route('/weather/<int:id>/delete', methods=['POST'])
def delete_weather(id):
    return f"Weather record {id} deleted."


if __name__ == '__main__':
    app.run(debug=True)
    