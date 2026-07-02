from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

@app.route("/")
def read_root():
    return jsonify({
        "status": "online",
        "message": "Welcome to the Tuition Management Platform API (Flask Setup)"
    })

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "Backend is running"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
