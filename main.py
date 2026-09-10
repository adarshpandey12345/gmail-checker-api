from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "3683f20faf2b4cfdaf683c8616a9b226"

@app.route('/')
def home():
    return jsonify({"status": "active"})

@app.route('/verify', methods=['GET'])
def verify():
    email = request.args.get('email', '').strip().lower()

    if not email:
        return jsonify({"error": "No email provided"}), 400

    try:
        url = f"https://emailreputation.abstractapi.com/v1/?api_key={API_KEY}&email={email}"
        response = requests.get(url, timeout=12)

        return jsonify({
            "status_code": response.status_code,
            "raw_data": response.json()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
