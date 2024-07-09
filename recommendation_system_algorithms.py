import numpy as np
from numpy.linalg import norm
import pandas as pd
import intellikit as ik
from sklearn.metrics.pairwise import euclidean_distances

def calculate_cosine_similarity(point, Full_data ,hospital_data, n=3):
    cosine_similarities = np.dot(Full_data, point.T) / (norm(Full_data, axis=1)[:, np.newaxis] * norm(point))
    top_choices = np.argsort(cosine_similarities.flatten())[-n:][::-1]
    top_names = hospital_data.iloc[top_choices]
    return top_names, top_names.index


def get_recommendation_filtered_services(service, lat_lng, op_day, care_s, payment, rating, Full_data, hospital_data):
    print(service)
    full_data_services = Full_data[:, :len(service)]
    
    top_choices = calculate_cosine_similarity(np.array([service]),full_data_services, hospital_data=hospital_data, n = 10)[1]
    print(top_choices)
    filtered_data = Full_data[top_choices]
    print(hospital_data.iloc[top_choices])

    final_vector  = np.concatenate([
        [op_day], [payment], care_s.reshape(-1, 1), np.array([rating]).reshape(-1, 1)
    ], axis = 1)

    final_vector = final_vector.astype(np.float64)

    Final_choices = calculate_cosine_similarity(final_vector, filtered_data[:, len(service):], hospital_data=hospital_data, n = 8)[1]
    print(Final_choices)
    print(lat_lng)
    top_choices = top_choices[Final_choices]

    top_choices_df = hospital_data.loc[top_choices]
    latitude_logitude_full = top_choices_df[['Latitude', 'Longitude']].fillna(0).values

    distance = euclidean_distances(latitude_logitude_full, lat_lng)
    top = np.argsort(distance.flatten())[:8]
    print(distance)
    print(top)
    top_choices = top_choices[top]
    print(top_choices)
    print(hospital_data.iloc[21])

    return hospital_data.iloc[top_choices]

def create_dict(col_dict : dict, col_array : np.ndarray, value) -> dict:
    for val in col_array:
        col_dict[val] = value

    return col_dict

def get_recommendation_CBR(full_data_df : pd.DataFrame, query_df : pd.DataFrame, n = 10):
    columns = full_data_df.columns
    hamming = ik.sim_hamming
    levenshtein = ik.sim_levenshtein
    abs_diff = ik.sim_difference

    # Convert Location, Operating Time, Payment, Care system and services in the full_data_df to str
    for col in ['Location', 'Operating Time', 'Payment', 'Care system', 'Services']:
        full_data_df[col] = full_data_df[col].fillna("UNKNOWN")
    
    print(full_data_df['Location'].unique())
    print(query_df['Location'])

    # Assign Functions
    similarity_functions = {
        'rating': abs_diff,
        'Location': levenshtein,
        'Operating Time': levenshtein,
        'Payment': levenshtein,
        'Care system': levenshtein,
        'Services': levenshtein
    }

    #Assign Weights
    feature_weights = {
        'rating': 1.0,
        'Location': 0.3,
        'Operating Time': 0.2,
        'Payment': 0.2,
        'Care system': 0.2,
        'Services': 7.5
    }

    print(full_data_df['Services'].head())

    return ik.linearRetriever(full_data_df, query_df, similarity_functions, feature_weights, n).index
