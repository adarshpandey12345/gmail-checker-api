from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "active", "service": "Automated Gmail Verification API"})

@app.route('/verify', methods=['GET'])
def verify_gmail():
    email = request.args.get('email', '').strip().lower()

    if not email or not email.endswith('@gmail.com'):
        return jsonify({"valid": False, "reason": "Invalid email format. Must end with @gmail.com"}), 400

    username = email.replace('@gmail.com', '')
    if len(username) < 6 or len(username) > 30:
        return jsonify({"valid": False, "reason": "Gmail username must be between 6 and 30 characters"}), 200

    try:
        # Public deliverability verification gateway
        api_url = f"https://api.eva.pingutil.com/email?email={email}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        resp = requests.get(api_url, headers=headers, timeout=12)

        if resp.status_code == 200:
            data = resp.json().get("data", {})
            deliverable = data.get("deliverable", False)
            gibberish = data.get("gibberish", False)

            if deliverable and not gibberish:
                return jsonify({
                    "valid": True,
                    "email": email,
                    "status": "Account verified"
                })
            else:
                return jsonify({
                    "valid": False,
                    "email": email,
                    "reason": "Account does not exist on mail servers"
                })

        # Fallback check
        return jsonify({"valid": False, "email": email, "reason": "Verification service unavailable"}), 502

    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
            
