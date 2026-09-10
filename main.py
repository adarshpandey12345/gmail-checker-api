from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "zomii388jkamjfp16ni1hqkpivw6qj7j"

@app.route('/')
def home():
    return jsonify({"status": "active"})

@app.route('/verify', methods=['GET'])
def verify():
    email = request.args.get('email', '').strip().lower()
    if not email:
        return jsonify({"valid": False, "reason": "No email provided"}), 400

    # Gamalogic direct endpoint call
    url = f"https://api.gamalogic.com/email/{email}?apikey={API_KEY}"
    
    try:
        res = requests.get(url, timeout=10)
        return jsonify({
            "status_code": res.status_code,
            "raw_response": res.json() if res.headers.get('content-type') == 'application/json' else res.text
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
