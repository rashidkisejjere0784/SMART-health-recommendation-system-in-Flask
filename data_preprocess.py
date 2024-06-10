import pandas as pd
import numpy as np
import re

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
def generate_Factorized_Matrix(data, column):
  bow = set()
  for i, element in enumerate(data[column].values):
    element = re.sub('\.', ',', str(element))
    values = element.split(',')
    for value in values:
        if value == '':
            continue
        value = value.strip().lower()
        bow.add(value)

  bow = sorted(bow)

  Matrix = np.zeros((len(data), len(bow)))
  for i, element in enumerate(data[column].values):
    element = str(element)
    element = re.sub('\.', ',', element)
    words = element.split(',')
    for word in words:
      try:
        word = word.strip().lower()
        index = list(bow).index(word)
        Matrix[i, index] = 1
      except:
        continue

  return Matrix, bow

