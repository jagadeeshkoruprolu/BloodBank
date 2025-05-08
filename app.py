from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'secret123'
DATA_FILE = 'blood_data.json'

def send_confirmation_email(user_email, name, mobile, address, blood_group, quantity):
    sender_email = "k.jagadeesh9949@gmail.com"
    sender_password = "oiapivduuitxghxz"
    admin_email = "k.jagadeesh9949@gmail.com"

    subject = "Blood Request Confirmation"
    body = f"""
    Hello {name},

    Your request for {quantity} unit(s) of {blood_group} blood has been received successfully.

    Mobile: {mobile}
    Address: {address}

    Thank you,
    Hospital Blood Bank Team
    """

    admin_body = f"""
    New blood request received:

    Name: {name}
    Email: {user_email}
    Mobile: {mobile}
    Address: {address}
    Blood Group: {blood_group}
    Quantity: {quantity}
    """

    msg_user = MIMEMultipart()
    msg_user['From'] = sender_email
    msg_user['To'] = user_email
    msg_user['Subject'] = subject
    msg_user.attach(MIMEText(body, 'plain'))

    msg_admin = MIMEMultipart()
    msg_admin['From'] = sender_email
    msg_admin['To'] = admin_email
    msg_admin['Subject'] = "New Blood Request Alert"
    msg_admin.attach(MIMEText(admin_body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg_user)
        server.send_message(msg_admin)
        server.quit()
    except Exception as e:
        print(f"Email error: {e}")

@app.route('/')
def home():
    with open(DATA_FILE, 'r') as file:
        data = json.load(file)
    return render_template('index.html', blood_data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['user'] = 'admin'
            return redirect(url_for('dashboard'))
        flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if session.get('user') != 'admin':
        return redirect(url_for('login'))

    with open(DATA_FILE, 'r') as file:
        data = json.load(file)

    if request.method == 'POST':
        for group in data:
            data[group] = int(request.form[group])
        with open(DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4)
        flash('Stock updated!')

    return render_template('dashboard.html', blood_data=data)

@app.route('/request', methods=['GET', 'POST'])
def request_blood():
    with open(DATA_FILE, 'r') as file:
        blood_data = json.load(file)

    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        address = request.form['address']
        group = request.form['blood_group']
        qty = int(request.form['quantity'])
        user_email = request.form['email']

        if blood_data.get(group, 0) >= qty:
            blood_data[group] -= qty
            with open(DATA_FILE, 'w') as file:
                json.dump(blood_data, file, indent=4)

            flash('Request successful!')

            if user_email:
                send_confirmation_email(user_email, name, mobile, address, group, qty)
        else:
            flash('Not enough stock!')

    return render_template('request_blood.html', blood_data=blood_data)

if __name__ == '__main__':
    app.run(debug=True)


# k.jagadeesh9949@gmail.com
# oiapivduuitxghxz
# pip install flask
