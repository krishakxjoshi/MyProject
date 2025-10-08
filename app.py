from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flash messages


@app.route("/shop")
def shop():
    return render_template("shop.html")

@app.route("/account")
def account():
    return render_template("account.html")
 
@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/cart")
def cart():
    return render_template("cart.html")


# -------------------- HOME ROUTE --------------------


@app.route("/")
def index():
    return render_template("index.html")

# -------------------- LOGIN ROUTE --------------------
@app.route("/login")
def login():
    return render_template("login.html")

# -------------------- SIGNUP ROUTE --------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Send OTP email
        send_otp_email(email, otp)

        # Save OTP in DB
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO users (email, otp, verified) VALUES (?, ?, 0)",
            (email, otp),
        )
        conn.commit()
        conn.close()

        flash("OTP sent to your email! Check your inbox.")
        return redirect(url_for("verify", email=email))

    return render_template("signup.html")


# -------------------- VERIFY ROUTE --------------------
@app.route("/verify/<email>", methods=["GET", "POST"])
def verify(email):
    if request.method == "POST":
        entered_otp = request.form["otp"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT otp FROM users WHERE email=?", (email,))
        result = cursor.fetchone()

        if result and result[0] == entered_otp:
            cursor.execute("UPDATE users SET verified=1 WHERE email=?", (email,))
            conn.commit()
            conn.close()
            flash("Email verified successfully! 🎉")
            return redirect(url_for("login"))
        else:
            conn.close()
            flash("Invalid OTP. Try again.")

    return render_template("verify.html", email=email)


# -------------------- AJAX VERIFY ROUTE --------------------
@app.route("/verify_ajax/<email>", methods=["POST"])
def verify_ajax(email):
    data = request.get_json()
    entered_otp = data.get("otp")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT otp FROM users WHERE email=?", (email,))
    result = cursor.fetchone()

    if result and result[0] == entered_otp:
        cursor.execute("UPDATE users SET verified=1 WHERE email=?", (email,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "OTP verified successfully!"})
    else:
        conn.close()
        return jsonify({"success": False, "message": "Invalid OTP. Try again."})


# -------------------- SEND OTP EMAIL --------------------
def send_otp_email(to_email, otp_value):
    sender_email = "krishakjoshi@gmail.com"  # Your Gmail
    app_password = "cqgqzjggasupagjd"        # Your App Password

    html_content = f"""
    <html>
      <body style="background: radial-gradient(circle at bottom right, #141e30, #243b55); 
                   font-family: Poppins, sans-serif; color: #fff; text-align:center; padding: 40px;">
        <h1 style="font-size: 40px; font-weight:bold; color:black;">DHYANI TRACKS</h1>
        <p style="font-size: 20px; margin-top:40px;">Your OTP is:</p>
        <div style="font-size:48px; font-weight:bold; margin: 20px auto; 
                    padding: 20px; background: rgba(255,255,255,0.2); border-radius:15px; 
                    display:inline-block;">{otp_value}</div>
        <p style="margin-top:40px; font-size:14px; color:#ccc;">Do not share this OTP with anyone.</p>
      </body>
    </html>
    """

    msg = MIMEText(html_content, "html")
    msg['Subject'] = "Your OTP Verification Code"
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        print(f"OTP sent to {to_email}")
    except Exception:
        import traceback
        print("Error sending OTP:")
        traceback.print_exc()


# -------------------- MAIN --------------------
if __name__ == "__main__":
    app.run(debug=True)
