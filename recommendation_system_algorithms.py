import numpy as np
from numpy.linalg import norm


def calculate_cosine_similarity(point, Full_data ,hospital_data, n=3):
    cosine_similarities = np.dot(Full_data, point.T) / (norm(Full_data, axis=1)[:, np.newaxis] * norm(point))
    top_choices = np.argsort(cosine_similarities.flatten())[-n:][::-1]
    top_names = hospital_data.iloc[top_choices]
    return top_names, top_choices

def get_recommendation_filtered_services(service, location, op_day, care_s, payment, rating, Full_data, hospital_data):
    print(service)
    full_data_services = Full_data[:, :len(service)]
    
    top_choices = calculate_cosine_similarity(np.array([service]),full_data_services, hospital_data=hospital_data, n = 4)[1]

    filtered_data = Full_data[top_choices]
    print(hospital_data.iloc[top_choices])

    final_vector  = np.concatenate([
        [location], [op_day], [payment], care_s.reshape(-1, 1), np.array([rating]).reshape(-1, 1)
    ], axis = 1)

    final_vector = final_vector.astype(np.float64)
    print(filtered_data[:, len(service):])
    print(final_vector)

    Final_choices = calculate_cosine_similarity(final_vector, filtered_data[:, len(service):], hospital_data=hospital_data)[1]
    top_choices = top_choices[Final_choices]

    return hospital_data.iloc[top_choices]