import pandas as pd
import numpy as np
from data_preprocess import gen_matrix_op_time, generate_Factorized_Matrix, encode_care_system, get_matrix, get_opday_matrix, find_service_category
from recommendation_system_algorithms import get_recommendation_filtered_services, get_recommendation_CBR

def convert_services_to_cateogories(services : str):
    services_list = services.split(',')
    service_categories = []
    for service in services_list:
        if service.lower().strip() == '':
           continue
        service_categories.extend(find_service_category(service.lower().strip()))
    return ", ".join(list(set(service_categories)))
   

def get_recommendations(services_str : str, location_str : str, payment_str : str, rating : float, op_day_str : str , care_system : str, approach : str):
    hospital_data = pd.read_excel("./Data/Hospital Data - Hospital.xlsx")
    service_matrix, service_bow, service_cats = generate_Factorized_Matrix(hospital_data, 'Services', is_service=True)
    location_matrix, location_bow, _ = generate_Factorized_Matrix(hospital_data, 'Location')
    payment_matrix, payment_bow, _ = generate_Factorized_Matrix(hospital_data, 'Payment')
    operating_time_matrix = hospital_data['Operating Time'].apply(gen_matrix_op_time).values
    care_system_full = hospital_data['Care system'].apply(lambda x: encode_care_system(str(x)))
    ratings_full = hospital_data['rating'].fillna(0).values

    care_system_rating = np.concatenate([care_system_full.values.reshape(-1, 1), ratings_full.reshape(-1, 1)], axis = 1)
    Merged_data = np.concatenate([service_matrix, location_matrix, np.array(list(operating_time_matrix)), payment_matrix], axis =1)
    Full_data = np.concatenate([Merged_data, care_system_rating], axis =1)

    service = get_matrix(services_str, ',', service_bow)
    location = get_matrix(location_str.lower(), ',', location_bow)

    op = get_opday_matrix(op_day_str)
    payment = get_matrix(payment_str.lower(), ',', payment_bow)
    care_s = np.array([encode_care_system(care_system)])

    hospital_data['condensed services'] = service_cats
    hospital_data['condensed services'] = hospital_data['condensed services'].apply(lambda x: ", ".join(x))
    hospital_data.to_excel("Data/Cleaned data.xlsx")

    if approach == "Content Based Filtering":
      # recommendation based on Content Based Filtering
      recommendation = get_recommendation_filtered_services(service=service, location=location, 
                                                          op_day=op, payment=payment, care_s=care_s,
                                                            rating=rating,Full_data=Full_data, hospital_data=hospital_data)
    else:
       # recommendation is Cased Based Reasoning

      query_df = pd.DataFrame(columns=hospital_data.columns)
      full_data_df = hospital_data.copy()
      full_data_df['Services'] = full_data_df['Services'].apply(convert_services_to_cateogories)

      query_df["Services"] = [services_str]
      query_df["Location"] = [location_str]
      query_df["Operating Time"] = [op_day_str]
      query_df["Payment"] = [payment_str]
      query_df["Care system"] = [care_system]
      query_df["rating"] = [float(rating)]

      indicies = get_recommendation_CBR(full_data_df, query_df)
      recommendation = hospital_data.iloc[indicies]


    return recommendation.to_json()


