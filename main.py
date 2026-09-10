from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Active Gamalogic API Key
GAMALOGIC_KEYS = [
    "zomii388jkamjfp16ni1hqkpivw6qj7j"
]

current_key_index = 0
usage_counter = 2  # Offset by the 2 credits already used

def verify_with_gamalogic(email, api_key):
    global usage_counter
    url = f"https://api.gamalogic.com/email/{email}?apikey={api_key}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Extract verification block
        results = data.get("gamalogic_email_verification", {})
        if not results:
            results = data

        # Check for credit or quota exhaustion
        msg = str(results.get("message", "")).lower()
        if "credits" in msg or "quota" in msg or response.status_code in [402, 429]:
            return None, "Quota exhausted"

        usage_counter += 1
        
        # Gamalogic deliverability status mapping
        status = str(results.get("status", "")).lower()
        is_deliverable = str(results.get("is_deliverable", "")).lower()
        
        is_valid = (
            status in ["deliverable", "valid"] or 
            is_deliverable == "true" or 
            results.get("is_valid") is True
        )
        
        return is_valid, results
    except Exception as e:
        return None, str(e)

@app.route('/')
def home():
    return jsonify({
        "status": "active",
        "service": "Gamalogic Verification Engine",
        "used_credits": usage_counter,
        "remaining_estimated": max(0, 500 - usage_counter)
    })

@app.route('/verify', methods=['GET'])
def verify():
    global current_key_index, usage_counter
    email = request.args.get('email', '').strip().lower()

    if not email or not email.endswith('@gmail.com'):
        return jsonify({"valid": False, "reason": "Invalid email format. Must end with @gmail.com"}), 400

    username = email.replace('@gmail.com', '')
    if len(username) < 6 or len(username) > 30:
        return jsonify({"valid": False, "reason": "Gmail username must be between 6 and 30 characters"}), 200

    active_key = GAMALOGIC_KEYS[current_key_index]
    is_valid, result = verify_with_gamalogic(email, active_key)

    if is_valid is not None:
        return jsonify({
            "valid": is_valid,
            "email": email,
            "status": "Verified" if is_valid else "Mailbox does not exist",
            "credits_used": usage_counter
        })

    return jsonify({"valid": False, "reason": "API credit limit reached or upstream error"}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
        
