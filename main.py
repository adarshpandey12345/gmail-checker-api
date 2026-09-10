
from flask import Flask, request, jsonify
import requests
import json
import re

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "active", "service": "Gmail Checker API"})

@app.route('/verify', methods=['GET'])
def verify_gmail():
    email = request.args.get('email', '').strip().lower()

    if not email or not email.endswith('@gmail.com'):
        return jsonify({"valid": False, "reason": "Invalid format. Must end with @gmail.com"}), 400

    username = email.replace('@gmail.com', '')
    if len(username) < 6 or len(username) > 30:
        return jsonify({"valid": False, "reason": "Gmail username must be 6 to 30 characters"}), 200

    try:
        session = requests.Session()
        
        # 1. First GET request to fetch Google's active cookies and session tokens
        init_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        init_res = session.get("https://accounts.google.com/signin/v2/identifier?flowName=GlifWebSignIn&flowEntry=ServiceLogin", headers=init_headers, timeout=10)
        
        # Extract dynamic azt/f.req tokens from page source if available
        azt_match = re.search(r'"AZT":"([^"]+)"', init_res.text)
        azt = azt_match.group(1) if azt_match else "AFoagUUt6N_WJ1jK"

        # 2. Check via Google lookup RPC
        post_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Google-Accounts-XSRF": "1",
            "Accept": "*/*",
            "Referer": "https://accounts.google.com/"
        }

        lookup_url = "https://accounts.google.com/_/signin/sl/lookup?hl=en"
        data = {
            "f.req": json.dumps([email, []]),
            "azt": azt
        }

        resp = session.post(lookup_url, data=data, headers=post_headers, timeout=10)
        text = resp.text

        # 3. Google clear indicators
        # Agar user bilkul exist nahi karta:
        if "Couldn't find your Google Account" in text or '["e",2,null,null,null,-10001' in text:
            return jsonify({"valid": False, "email": email, "reason": "Account does not exist on Google"})
        
        # Agar Google ne user identify kar liya ya password prompt trigger kiya:
        if "IN_USE" in text or email in text or '["e",2,null,null,null,null' in text or 'password' in text.lower():
            return jsonify({"valid": True, "email": email, "status": "Account exists on Google"})

        # Agar Google verification block/challenge kare, safe check:
        if resp.status_code == 200 and len(text) > 50:
            return jsonify({"valid": True, "email": email, "status": "Account detected"})

        return jsonify({"valid": False, "email": email, "reason": "Account does not exist on Google"})

    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
        
