from flask import Flask, render_template, request, jsonify, session
import pandas as pd
from get_recommendation import get_recommendations
import numpy as np
from config import SECRET_KEY, DATABASE_URI, JWT_SECRET_KEY, HOST, GMAIL_PASSWORD, GMAIL_USERNAME, DATA_PATH, TEMP_DATA, ADMIN_ID
from flask_mail import Mail, Message 
from flask_jwt_extended import JWTManager, create_access_token
from db import db
from datetime import timedelta
import jwt as JWT
from flask_bcrypt import Bcrypt 
app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = GMAIL_USERNAME
app.config['MAIL_PASSWORD'] = GMAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


db.init_app(app)
mail = Mail(app)
jwt = JWTManager(app)
bcrpy = Bcrypt(app)

from models.userModel import User

# with app.app_context():
#     db.drop_all()
#     db.create_all()

def is_authenticated():
    try:
        user_token = session.get('user_token')
        if user_token is not None:
            decoded_jwt = JWT.decode(user_token, JWT_SECRET_KEY, ['HS256'])
            user_id = int(decoded_jwt['sub'])
            user = User.query.filter_by(id=user_id).first()
            if user:
                is_admin = is_user_admin(user.id)
                return True, is_admin
    
    except Exception:
        return False, None
    
    return False, None

def is_user_admin(user_id):
    if user_id == ADMIN_ID:
        return True
    
    return False

def extract_elements(elements : list) -> set:
    elements_set = set()
    for element in elements:
        for s in str(element).split(','):
            s = s.lower().strip()
            if s == 'nan':
                continue
            if s != '':
                elements_set.add(s)
    
    return sorted(elements_set)

@app.route('/')
def home():
    data = pd.read_csv("./Data/Hospital Data - Hospital.csv")
    services = data['Services'].values
    locations = data['Location'].values
    locations_set = extract_elements(np.append(['Any Location'], locations))
    services_set = extract_elements(services)

    return render_template('home.html', services=services_set, locations=locations_set)

@app.route('/review_data', methods=['GET', 'POST'])
def review_data():
    auth = is_authenticated()
    if not auth[0]:
        return render_template('contribute.html')
    
    if not auth[1]:
        return render_template('contribute.html')
    
    temp_data = get_data(TEMP_DATA)

    if request.method == 'POST':
        id = int(request.form['hospital_id'])
        action = request.form['Action']

        if action == 'approve':
            hospital_data = pd.read_csv(DATA_PATH)
            temp_data = pd.read_csv(TEMP_DATA)

            hospital = temp_data.iloc[id]
            print(hospital)
            if str(hospital['Hospital Id']) in [None, np.nan, 'nan', 'NaN']:
                print(hospital['Hospital Id'])
                # Concatenate the data
                index = len(hospital_data) + 1
                hospital['Hospital Id'] = index
                hospital_data = pd.concat([hospital_data, hospital.to_frame().T],axis = 0, ignore_index=True)
                hospital_data.to_csv(DATA_PATH, index=False)

            else:
                print("heheh")
                hospital_data[hospital_data['Hospital Id'] == hospital['Hospital Id']] = hospital
                hospital_data.to_csv(DATA_PATH, index=False)
            
            temp_data = temp_data.drop(id)
            temp_data.to_csv(TEMP_DATA, index=False)
        
        if action == 'decline':
            temp_data = pd.read_csv(TEMP_DATA)
            temp_data = temp_data.drop(id)
            temp_data.to_csv(TEMP_DATA, index=False)

        temp_data = get_data(TEMP_DATA)

    return render_template('review_data.html', hospitals=temp_data, authenticated = True)


@app.route('/edit_hospital', methods=['POST'])
def edit_hospital():
    if not is_authenticated()[0]:
        return render_template('edit_hospital.html', authenticated = False)
    
    hospital_id = int(request.form['hospital_id'])
    print(hospital_id)
    hospital_data = pd.read_csv(DATA_PATH)
    hospital = hospital_data.iloc[hospital_id]
    
    return render_template('edit_hospital.html', hospital=hospital, authenticated = True)

@app.route('/record_data', methods=['GET'])
def record_data():
    if not is_authenticated()[0]:
        return render_template('record_data.html', authenticated = False)
    
    return render_template('record_data.html', authenticated = True)

@app.route('/add_hospital', methods=['POST'])
def add_hospital():
    auth = is_authenticated()
    if not auth[0]:
        return render_template('show_data.html', authenticated = False, is_admin = auth[1])
    
    try:
        hospital_id = int(request.form['id'])
    except:
        hospital_id = None

    hospital_name = request.form['hospitalName']
    location = request.form['location']
    services = request.form['services']
    rating = request.form['rating']
    care_system = request.form['careSystem']
    operating_time = request.form['operatingTime']
    payment = request.form['payment']
    cordinates = request.form['coordinates']
    phone = request.form['phone']
    website = request.form['website']
    h_type = request.form['type']

    try:
        temp_data = pd.read_csv(TEMP_DATA)
    
    except FileNotFoundError:
        temp_data = pd.DataFrame(columns=[
            "Hospital Id", "Hospital Name", "rating", "Care system", "Services", "Operating Time", 
            "Location", "Payment", "Cordinates", "Type", "Beds", "phone", "website"									
        ])
    
    temp_data = pd.concat(
        [temp_data, pd.DataFrame({
            "Hospital Id": hospital_id,
            "Hospital Name": hospital_name,
            "rating": rating,
            "Care system": care_system,
            "Services": services,
            "Operating Time": operating_time,
            "Location": location,
            "Payment": payment,
            "Cordinates": cordinates,
            "Type": h_type,
            "Beds": 0,
            "phone": phone,
            "website": website
        }, index=[0])],ignore_index=True
    )

    temp_data.to_csv(TEMP_DATA, index=False)
    hospitals = get_data()

    return render_template("show_data.html", is_admin = auth[1], hospitals=hospitals, authenticated = True, message = "Contribution recorded successfully, Our team is going to review, Thank you !")

@app.route('/get_recommendations', methods=['POST'])
def get_recommendation():
    data = request.get_json()
    services = data.get('services', [])
    locations = data.get('location', [])
    payment = data.get('payment', '')
    care_system = data.get('care', '')
    rating = data.get('rating', '')
    date = data.get('date', [])
    print(services, locations, payment)

    recommendation = get_recommendations(services=",".join(services), 
                                         location=",".join(locations), payment=payment, rating=rating, op_day=",".join(date), care_system=care_system)
    return jsonify({'status': 'success', 'recommendations': recommendation})


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')


def get_data(path = DATA_PATH) -> list:
    hospital_data = pd.read_csv(path)
    hospitals = []

    for id, hospital in hospital_data.iterrows():
        hospitals.append(hospital)

    return hospitals

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email = email).first()
        if user and bcrpy.check_password_hash(user.password, password):
            token = create_access_token(identity=str(user.id))
            session['user_token'] = token

            hospitals = get_data()
            return render_template('show_data.html', hospitals = hospitals, authenticated = True, is_admin = is_user_admin(user.id))
        else:
            return render_template('contribute.html', error = "Invalid Email or Password")

    return render_template('contribute.html', authenticated=False)

@app.route('/verify', methods=['GET'])
def verify_token():
    token = request.args.get('token')
    try:
        decoded_jwt = JWT.decode(token, JWT_SECRET_KEY, ['HS256'])
        user_id = int(decoded_jwt['sub'])

        user = User.query.filter_by(id=user_id).first()
        user.status = 1
        db.session.commit()
        return jsonify({
            "response" : "success"
        })
    except Exception as e:
        print(e)
        return jsonify({
            "response" : "Invalid token"
        }
        )

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        expires = timedelta(seconds=300)
        
        if password != confirm_password:
            return render_template('register.html', error = "Password mismatch")
        
        user = User.query.filter_by(email = email).first()
        if user:
            if user.status == 1:
                return render_template('register.html', error = "Email already exists")
        
            elif user.status == 0:
                send_email(user.username, user.email, user, expires)
                return render_template('register.html', error = "User isn't verified yet, check your email")


        try:
            password = bcrpy.generate_password_hash(password).decode('utf8')
            user = User(username = username, email = email, password = password)
            db.session.add(user)
            db.session.commit()

            send_email(username, email, user, expires)

            return render_template('register.html', message = "Registration successful, Check your email to verify your registration")
        
        except Exception as e:
            print(e)
            return render_template('register.html', error = "Registration Failed")

    else:
        return render_template('register.html', error = None)

def send_email(username, email, user, expires):
    token = create_access_token(identity=str(user.id), expires_delta=expires)
    message_title = "Registration"
    message = f"{HOST}verify?token={token}"
    sender = "noreply@app.com"
    msg = Message(message_title,sender= sender, recipients=[email])

    data = {
                'name' : username,
                'link' : message
            }

    msg.html = render_template('verify.html', data = data)
    mail.send(msg)

if __name__ == '__main__':
    app.run(debug=True)
