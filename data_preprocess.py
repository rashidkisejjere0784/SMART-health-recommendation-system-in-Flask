import pandas as pd
import numpy as np
import re
import pickle

def load_services_pickle():
    with open('Data/medical_services.pickle', 'rb') as f:
        medical_services = pickle.load(f)
    return medical_services

def find_service_category(service):
    medical_services = load_services_pickle()
    categories = [category for category, services in medical_services.items() if service in services]
    return categories if categories else None

def get_matrix(value, split_by, bow, is_op = False):
    matrix = np.zeros(len(bow))
    try:
        elements =[element.strip() for element in value.split(split_by) if element.strip() != '']

    except:
        elements = [value]

    for i, word in enumerate(bow):
        if word in elements:
            matrix[i] = 1

    return matrix

def get_opday_matrix(days : str):
    day_dict = {
                     "Monday" : 0,
                    "Tuesday" : 1,
                    "Wednesday" : 2,
                    "Thursday"  : 3,
                    "Friday"  : 4,
                    "Saturday" : 5,
                    "Sunday"  : 6
                }
    try:
        days = [day.strip() for day in days.split(',')]

    except:
        days = [days.strip()]

    Matrix = np.zeros(7)
    for day in days:
        index = day_dict.get(day, None)
        if index is not None:
            Matrix[index] = 1

    return Matrix

def gen_matrix_op_time(op_time : str):
    days_vector = np.zeros(7)
    op_time = str(op_time)
    try:
        splitted = [value.strip() for value in op_time.split(',') if value.strip() != '']
    except:
        splitted = [op_time.strip()]

    if len(splitted) < 7:
        splitted = splitted + [0 for i in range(7 - len(splitted))]

    for i, value in enumerate(splitted):
        if value == 0 or value.lower() in ['closed', 'unknown']:
            continue

        days_vector[i] = 1

    return days_vector

def encode_care_system(care_system: str) -> int:
    if care_system == "Public":
        return 1

    if care_system == "Private":
        return 2

    else:
        return 0


# Create Matrix Factorization
def generate_Factorized_Matrix(data, column, is_service = False):
  bow = list()
  data_cat = []
  for i, element in enumerate(data[column].values):
    element = re.sub('\.', ',', str(element))
    values = element.split(',')
    cats = set()
    for value in values:
        if value == '':
            continue
        value = value.strip().lower()
        if is_service:
            categories = find_service_category(value)
            bow.extend(categories)
            for cat in categories:
                cats.add(cat)

        else:
            bow.append(value)
    
    data_cat.append(list(cats))

  bow = sorted(set(bow))

  Matrix = np.zeros((len(data), len(bow)))
  for i, element in enumerate(data[column].values):
    element = str(element)
    element = re.sub('\.', ',', element)
    words = element.split(',')
    for word in words:
      try:
        word = word.strip().lower()
        if is_service:
            categories = find_service_category(word)
            for category in categories:
                index = list(bow).index(category)
                Matrix[i, index] = 1
        else:
            index = list(bow).index(word)
            Matrix[i, index] = 1
      except:
        continue

  return Matrix, bow, data_cat

