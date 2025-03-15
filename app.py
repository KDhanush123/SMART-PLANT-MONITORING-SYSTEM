 
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# In-memory storage for received data
received_data = {}

@app.route('/update', methods=['POST'])
def update_data():
    global received_data
    received_data = request.json
    print("Received data:", received_data)
    return jsonify({"status": "success", "data": received_data})

@app.route('/get_data', methods=['GET'])
def get_data():
    global received_data
    print("Sending data:", received_data)
    return jsonify(received_data)

@app.route('/view')
def view():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888)