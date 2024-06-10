import pandas as pd
import numpy as np
from data_preprocess import gen_matrix_op_time, generate_Factorized_Matrix, encode_care_system, get_matrix, get_opday_matrix
from recommendation_system_algorithms import get_recommendation_filtered_services

def get_recommendations(services : str, location : str, payment : str, rating : float, op_day : str , care_system : str):
    hospital_data = pd.read_csv("./Data/Hospital Data - Hospital.csv")
    service_matrix, service_bow = generate_Factorized_Matrix(hospital_data, 'Services')
    location_matrix, location_bow = generate_Factorized_Matrix(hospital_data, 'Location')
    print(location_matrix[-1], location_bow)
    payment_matrix, payment_bow = generate_Factorized_Matrix(hospital_data, 'Payment')
    operating_time_matrix = hospital_data['Operating Time'].apply(gen_matrix_op_time).values
    care_system_full = hospital_data['Care system'].apply(lambda x: encode_care_system(str(x)))
    ratings_full = hospital_data['rating'].fillna(0).values

    care_system_rating = np.concatenate([care_system_full.values.reshape(-1, 1), ratings_full.reshape(-1, 1)], axis = 1)
    Merged_data = np.concatenate([service_matrix, location_matrix, np.array(list(operating_time_matrix)), payment_matrix], axis =1)
    Full_data = np.concatenate([Merged_data, care_system_rating], axis =1)
    print(payment_bow)

    service = get_matrix(services.lower(), ',', service_bow)
    location = get_matrix(location.lower(), ',', location_bow)


    op = get_opday_matrix(op_day)
    payment = get_matrix(payment.lower(), ',', payment_bow)
    care_s = np.array([encode_care_system(care_system)])

    recommendation = get_recommendation_filtered_services(service=service, location=location, 
                                                          op_day=op, payment=payment, care_s=care_s,
                                                            rating=rating,Full_data=Full_data, hospital_data=hospital_data)
    print(recommendation.to_json())
    return recommendation.to_json()


