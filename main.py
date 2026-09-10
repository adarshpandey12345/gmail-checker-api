from flask import Flask, request, jsonify
import requests
import re
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
        
        # 1. Google initialization headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://accounts.google.com",
            "Referer": "https://accounts.google.com/signin/v2/identifier"
        }

        # 2. Google Internal Lookup Request
        lookup_url = "https://accounts.google.com/_/signin/sl/lookup"
        payload = {
            "f.req": json.dumps([email, []]),
            "azt": "AFoagUUt6N_WJ1jK"
        }

        resp = session.post(lookup_url, data=payload, headers=headers, timeout=10)
        body = resp.text

        # 3. Validation Logic based on Google's internal lookup response
        # Agar account exist NAHI karta to Google response me IN_USE:false ya error code deta hai
        if "IN_USE" in body and "false" in body.lower():
            return jsonify({"valid": False, "email": email, "reason": "Account does not exist on Google"})

        if "Couldn't find your Google Account" in body or "identifier-not-found" in body:
            return jsonify({"valid": False, "email": email, "reason": "Account does not exist on Google"})

        # Agar Google ne identifier successfully lookup kiya
        if email in body or "ACCOUNT_CHOOSER" in body or "lookup" in body:
            return jsonify({"valid": True, "email": email, "status": "Account exists on Google"})

        # Fallback check
        return jsonify({"valid": False, "email": email, "reason": "Could not verify account status"})

    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
        
