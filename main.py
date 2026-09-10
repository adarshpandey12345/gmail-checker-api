from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Primary: Gamalogic (500 credits)
GAMALOGIC_KEY = "zomii388jkamjfp16ni1hqkpivw6qj7j"
gamalogic_usage = 2  # tracking from your 2 initial tests

# Fallback: Abstract Reputation API
ABSTRACT_KEY = "3683f20faf2b4cfdaf683c8616a9b226"

def verify_gamalogic(email):
    global gamalogic_usage
    if gamalogic_usage >= 495:
        return None, "Gamalogic quota limit reached"

    try:
        url = f"https://gamalogic.com/emailvrf/?emailid={email}&apikey={GAMALOGIC_KEY}&speed_rank=0"
        resp = requests.get(url, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            gamalogic_usage += 1
            
            # Check Gamalogic deliverability flags
            # Gamalogic typical response keys: is_deliverable or status
            status = str(data.get("status", "")).lower()
            deliverable = str(data.get("is_deliverable", "")).lower()
            
            if deliverable == "true" or status in ["deliverable", "valid"]:
                return True, "verified"
            return False, "undeliverable"

        return None, f"Gamalogic HTTP {resp.status_code}"
    except Exception as e:
        return None, str(e)

def verify_abstract(email):
    try:
        url = f"https://emailreputation.abstractapi.com/v1/?api_key={ABSTRACT_KEY}&email={email}"
        resp = requests.get(url, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            deliv = data.get("email_deliverability", {})
            status = deliv.get("status", "").lower()
            status_detail = deliv.get("status_detail", "").lower()
            is_smtp = deliv.get("is_smtp_valid", False)

            if status == "deliverable" and (status_detail == "valid_email" or is_smtp):
                return True, "verified"
            return False, "undeliverable"

        return None, f"Abstract HTTP {resp.status_code}"
    except Exception as e:
        return None, str(e)

@app.route('/')
def home():
    return jsonify({
        "status": "active",
        "gamalogic_credits_used": gamalogic_usage,
        "gamalogic_remaining": max(0, 500 - gamalogic_usage)
    })

@app.route('/verify', methods=['GET'])
def verify():
    email = request.args.get('email', '').strip().lower()

    if not email or not email.endswith('@gmail.com'):
        return jsonify({"valid": False, "reason": "Invalid email format. Must end with @gmail.com"}), 400

    username = email.replace('@gmail.com', '')
    if len(username) < 6 or len(username) > 30:
        return jsonify({"valid": False, "reason": "Gmail username must be between 6 and 30 characters"}), 200

    # 1. Try Gamalogic first
    valid, res = verify_gamalogic(email)
    if valid is not None:
        return jsonify({
            "valid": valid,
            "email": email,
            "provider": "gamalogic",
            "status": "Account verified" if valid else "Mailbox does not exist"
        })

    # 2. Seamless fallback to AbstractAPI if Gamalogic fails or hits quota
    valid, res = verify_abstract(email)
    if valid is not None:
        return jsonify({
            "valid": valid,
            "email": email,
            "provider": "abstract",
            "status": "Account verified" if valid else "Mailbox does not exist"
        })

    return jsonify({"valid": False, "reason": "All verification engines unavailable"}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
        
