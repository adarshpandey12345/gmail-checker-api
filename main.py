from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "active", "service": "Gmail Verification API"})

@app.route('/verify', methods=['GET'])
def verify_gmail():
    email = request.args.get('email', '').strip().lower()

    if not email or not email.endswith('@gmail.com'):
        return jsonify({"valid": False, "reason": "Invalid email format. Must end with @gmail.com"}), 400

    username = email.replace('@gmail.com', '')
    if len(username) < 6 or len(username) > 30:
        return jsonify({"valid": False, "reason": "Gmail username must be between 6 and 30 characters"}), 200

    try:
        # Google Android device setup check endpoint
        url = "https://android.clients.google.com/setup/checkin"
        
        # Public identity verification endpoint used by Chrome/Android setup
        verify_url = f"https://mail.google.com/mail/feed/atom/"
        
        # Test recipient status against Google's public accounts API
        headers = {
            "User-Agent": "Google-HTTP-Java-Client/1.25.0 (gzip)",
            "Accept": "application/json"
        }

        # Query Google's public account lookup gateway
        lookup_url = "https://accounts.google.com/_/common/account/lookup"
        post_data = {
            "f.req": f'["{email}"]'
        }
        
        req_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Referer": "https://accounts.google.com/"
        }

        resp = requests.post(lookup_url, data=post_data, headers=req_headers, timeout=10)
        body = resp.text

        # Analyze response indicators
        if "Couldn't find your Google Account" in body or '"e",-10001' in body:
            return jsonify({"valid": False, "email": email, "reason": "Account does not exist on Google"})

        if "IN_USE" in body or email in body or resp.status_code == 200 and len(body) > 30:
            return jsonify({"valid": True, "email": email, "status": "Account exists on Google"})

        return jsonify({"valid": False, "email": email, "reason": "Account does not exist on Google"})

    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
        
