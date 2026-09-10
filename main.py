from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

ABSTRACT_KEY = "3683f20faf2b4cfdaf683c8616a9b226"

@app.route('/')
def home():
    return jsonify({"status": "active", "service": "Email Verification API"})

@app.route('/verify', methods=['GET'])
def verify():
    email = request.args.get('email', '').strip().lower()

    if not email or not email.endswith('@gmail.com'):
        return jsonify({"valid": False, "reason": "Invalid email format. Must end with @gmail.com"}), 400

    username = email.replace('@gmail.com', '')
    if len(username) < 6 or len(username) > 30:
        return jsonify({"valid": False, "reason": "Gmail username must be between 6 and 30 characters"}), 200

    try:
        # AbstractAPI official endpoint
        url = f"https://emailvalidation.abstractapi.com/v1/?api_key={ABSTRACT_KEY}&email={email}"
        response = requests.get(url, timeout=12)

        if response.status_code == 200:
            data = response.json()
            deliverability = data.get("deliverability", "")
            is_valid_format = data.get("is_valid_format", {}).get("value", False)
            is_smtp_valid = data.get("is_smtp_valid", {}).get("value", False)

            # Check if email exists and can receive mails
            if deliverability == "DELIVERABLE" or (is_valid_format and is_smtp_valid):
                return jsonify({
                    "valid": True,
                    "email": email,
                    "status": "Account exists and deliverable"
                })
            else:
                return jsonify({
                    "valid": False,
                    "email": email,
                    "reason": "Mailbox does not exist or undeliverable"
                })

        return jsonify({"valid": False, "error": f"API error: {response.status_code}"}), 502

    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
            
