from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "active"})

@app.route('/verify', methods=['GET'])
def verify_gmail():
    email = request.args.get('email', '').strip().lower()

    if not email or not email.endswith('@gmail.com'):
        return jsonify({"valid": False, "reason": "Invalid email"}), 400

    try:
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "*/*"
        }
        
        # Test endpoint
        url = f"https://mail.google.com/mail/gxlu?email={email}"
        res = session.get(url, headers=headers, timeout=10)
        
        # Returns raw status, cookies, and body preview for debugging
        return jsonify({
            "email": email,
            "status_code": res.status_code,
            "cookies": dict(res.cookies),
            "headers": dict(res.headers),
            "sample_body": res.text[:300]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
        
