from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "active"})

@app.route('/verify', methods=['GET'])
def verify_gmail():
    email = request.args.get('email', '').strip().lower()
    if not email or not email.endswith('@gmail.com'):
        return jsonify({"valid": False, "reason": "Invalid email"}), 400

    try:
        session = requests.Session()
        url = "https://accounts.google.com/_/common/account/lookup"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://accounts.google.com",
            "Referer": "https://accounts.google.com/signin/v2/identifier",
            "X-Same-Domain": "1"
        }
        data = {
            "f.req": json.dumps([email, "identifiertoken", True, True])
        }

        resp = session.post(url, data=data, headers=headers, timeout=10)
        
        return jsonify({
            "status_code": resp.status_code,
            "raw_response": resp.text[:500]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
