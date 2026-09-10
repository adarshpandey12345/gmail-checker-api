from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Aapki Email Reputation API Key
API_KEY = "3683f20faf2b4cfdaf683c8616a9b226"

@app.route('/')
def home():
    return jsonify({"status": "active", "service": "Abstract Email Reputation API"})

@app.route('/verify', methods=['GET'])
def verify():
    email = request.args.get('email', '').strip().lower()

    if not email or not email.endswith('@gmail.com'):
        return jsonify({"valid": False, "reason": "Invalid email format. Must end with @gmail.com"}), 400

    username = email.replace('@gmail.com', '')
    if len(username) < 6 or len(username) > 30:
        return jsonify({"valid": False, "reason": "Gmail username must be between 6 and 30 characters"}), 200

    try:
        # Abstract Email Reputation official endpoint
        url = f"https://emailreputation.abstractapi.com/v1/?api_key={API_KEY}&email={email}"
        response = requests.get(url, timeout=12)

        if response.status_code == 200:
            data = response.json()
            
            # Reputation API me deliverability status check
            status = str(data.get("status", "")).lower()
            deliverability = str(data.get("deliverability", "")).lower()
            quality_score = data.get("quality_score", 0)

            # Agar email active/deliverable hai
            if status in ["valid", "deliverable"] or deliverability == "deliverable" or quality_score > 0.4:
                return jsonify({
                    "valid": True,
                    "email": email,
                    "status": "Verified and deliverable"
                })
            else:
                return jsonify({
                    "valid": False,
                    "email": email,
                    "reason": "Mailbox does not exist or invalid"
                })

        return jsonify({"valid": False, "error": f"API error: {response.status_code}", "detail": response.text}), 502

    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
            
