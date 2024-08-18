from flask import Flask, render_template, request, jsonify, session
import pandas as pd
from get_recommendation import get_recommendations
import numpy as np
import os
from dotenv import load_dotenv
from data_preprocess import  load_services_pickle
import joblib
import json

app = Flask(__name__)

load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


DATA_PATH = os.environ.get('DATA_PATH')
TEMP_DATA = os.environ.get('TEMP_DATA')


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "OK"}), 200
    

def extract_elements(elements : list, is_service = False) -> set:
    elements_set = list()
    for element in elements:
        for s in str(element).split(','):
            s = s.lower().strip()
            if s == 'nan':
                continue
            if s != '':
                elements_set.append(s)
    
    return sorted(set(elements_set))

@app.route('/')
def home():
    data = pd.read_excel("./Data/Kampala & Wakiso.xlsx")
    services_dict = joblib.load("./Data/services_dict.pkl")
    services = data['cleaned services'].values
    print(services_dict)
    services_set = extract_elements(services, True)

    return render_template('home.html', services=services_set, services_dict=services_dict)

@app.route('/get_recommendations', methods=['POST'])
def get_recommendation():
    data = request.get_json()
    services = data.get('services', [])
    locations = data.get('location', [])
    latitude = float(data.get('latitude', 0))
    longitude = float(data.get('longitude', 0))
    payment = data.get('payment', '')
    care_system = data.get('care', '')
    date = data.get('date', [])
    approach = data.get('approach', '')

    
    print(services, locations, payment)

    recommendation = get_recommendations(services_str=",".join(services), 
                                         latitude=latitude, longitude=longitude, payment_str=payment, op_day_str=",".join(date), care_system=care_system, approach=approach)
    
    recommendation = recommendation.sort_values("rating", ascending=False)
    hospital_ids = recommendation['hospital Id'].values.tolist()
    hospital_names = recommendation['facility_name'].values.tolist()
    Services = recommendation['services'].values.tolist()
    Location = recommendation['Subcounty'].values.tolist()
    Care_system = recommendation['care_system'].values.tolist()
    Rating = recommendation['rating'].values.tolist()
    Operation_Time = recommendation['operating_hours'].values.tolist()
    Latitude = recommendation['latitude'].values.tolist()
    Longitude = recommendation['longitude'].values.tolist()
    Payment = recommendation['mode of payment'].values.tolist()

    data_json =  json.dumps({'status': 'success', 'hospital_ids' : hospital_ids, 'hospital names' : hospital_names, 'Payment' : Payment,
                     'services' : Services, 'Location' : Location, 'rating' : Rating, 'Care system' : Care_system,
                     'operation_time' : Operation_Time, 'Latitude' : Latitude, 'Longitude' : Longitude})
    
    print(data_json)
    return data_json


def get_data(path = DATA_PATH) -> list:
    hospital_data = pd.read_csv(path)
    hospitals = []

    for id, hospital in hospital_data.iterrows():
        hospitals.append(hospital)

    return hospitals

if __name__ == '__main__':
    app.run(debug=True, port=4000)
