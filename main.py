from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "active", "message": "Gmail Checker API is running!"})

@app.route('/verify', methods=['GET'])
def verify_gmail():
    email = request.args.get('email', '').strip().lower()

    if not email or not email.endswith('@gmail.com'):
        return jsonify({"valid": False, "reason": "Invalid email format. Must be @gmail.com"}), 400

    username = email.replace('@gmail.com', '')

    # Basic Gmail syntax rules check
    if len(username) < 6 or len(username) > 30:
        return jsonify({"valid": False, "reason": "Gmail username must be 6 to 30 characters"}), 200

    try:
        # Google Public Validation Endpoint (Works over HTTPS Port 443)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        check_url = f"https://mail.google.com/mail/gxlu?email={email}"
        response = requests.get(check_url, headers=headers, timeout=10)

        # Google sets a 'COMPASS' cookie only if the account exists
        cookies = response.headers.get('Set-Cookie', '')

        if 'COMPASS=' in cookies:
            return jsonify({
                "valid": True,
                "email": email,
                "status": "Account exists on Google"
            })
        else:
            return jsonify({
                "valid": False,
                "email": email,
                "reason": "Account does not exist on Google"
            })

    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
        
