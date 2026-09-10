from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "active", "service": "Gmail Checker API"})

@app.route('/verify', methods=['GET'])
def verify_gmail():
    email = request.args.get('email', '').strip().lower()

    if not email or not email.endswith('@gmail.com'):
        return jsonify({"valid": False, "reason": "Invalid email format. Must end with @gmail.com"}), 400

    username = email.replace('@gmail.com', '')
    if len(username) < 6 or len(username) > 30:
        return jsonify({"valid": False, "reason": "Gmail username must be 6 to 30 characters"}), 200

    try:
        session = requests.Session()
        
        # Public identity check payload used by Android/Chrome Webview
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
        body = resp.text

        # If Google rejects account existence
        if "IN_USE" in body and "false" in body.lower():
            return jsonify({"valid": False, "email": email, "reason": "Account does not exist on Google"})

        if "Couldn't find your Google Account" in body or "NO_SUCH_USER" in body:
            return jsonify({"valid": False, "email": email, "reason": "Account does not exist on Google"})

        # If Google identifies the user profile or accepts the identifier
        if "IDENTIFIER" in body or email in body or "true" in body.lower():
            return jsonify({"valid": True, "email": email, "status": "Account exists on Google"})

        return jsonify({"valid": False, "email": email, "reason": "Account does not exist on Google"})

    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
                           
