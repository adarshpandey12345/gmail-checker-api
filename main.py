from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Abstract Email Reputation API Key
API_KEY = "3683f20faf2b4cfdaf683c8616a9b226"

@app.route('/')
def home():
    return jsonify({"status": "active", "service": "Automated Gmail Verification Engine"})

@app.route('/verify', methods=['GET'])
def verify():
    email = request.args.get('email', '').strip().lower()

    if not email or not email.endswith('@gmail.com'):
        return jsonify({"valid": False, "reason": "Invalid email format. Must end with @gmail.com"}), 400

    username = email.replace('@gmail.com', '')
    if len(username) < 6 or len(username) > 30:
        return jsonify({"valid": False, "reason": "Gmail username must be between 6 and 30 characters"}), 200

    try:
        url = f"https://emailreputation.abstractapi.com/v1/?api_key={API_KEY}&email={email}"
        response = requests.get(url, timeout=12)

        if response.status_code == 200:
            data = response.json()
            
            deliverability = data.get("email_deliverability", {})
            status = deliverability.get("status", "").lower()
            status_detail = deliverability.get("status_detail", "").lower()
            is_smtp_valid = deliverability.get("is_smtp_valid", False)

            # Verification rule based on Abstract's deliverability output
            if status == "deliverable" and (status_detail == "valid_email" or is_smtp_valid):
                return jsonify({
                    "valid": True,
                    "email": email,
                    "status": "Account verified and deliverable"
                })
            else:
                return jsonify({
                    "valid": False,
                    "email": email,
                    "reason": "Mailbox does not exist or cannot receive emails"
                })

        # In case of quota exhaustion (HTTP 429) or upstream error
        return jsonify({
            "valid": False, 
            "error": f"Upstream error ({response.status_code})"
        }), 502

    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
            
