from flask import Flask, request, jsonify
import dns.resolver
import smtplib

app = Flask(__name__)

@app.route('/verify', methods=['GET'])
def verify_gmail():
    email = request.args.get('email', '').strip().lower()
    
    if not email or not email.endswith('@gmail.com'):
        return jsonify({"valid": False, "reason": "Not a Gmail address"}), 400

    try:
        # 1. Resolve Google's primary MX server
        records = dns.resolver.resolve('gmail.com', 'MX')
        mx_host = str(records[0].exchange)

        # 2. Connect to Google's mail server on Port 25
        server = smtplib.SMTP(timeout=8)
        server.connect(mx_host, 25)
        server.helo("gmail-checker.local")
        server.mail("check@gmail-checker.local")
        
        # 3. Test recipient existence
        code, _ = server.rcpt(email)
        server.quit()

        # Google returns 250 if mailbox exists, 550 if it doesn't
        if code == 250:
            return jsonify({"valid": True, "email": email})
        else:
            return jsonify({"valid": False, "email": email, "reason": "Mailbox does not exist"})

    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
      
