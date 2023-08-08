import requests
import re
import numpy as np
import pandas as pd
import random
from rsome import ro
from rsome import grb_solver as grb
from math import sqrt
from bs4 import BeautifulSoup

all_programme = {'ACC': 'Accountancy', 'BUS': 'Business',
                 'ACBS': 'Accountancy & Business', 'ACDA': 'Accountancy & Data Science and Artificial Intelligence',
                 'ACFA': 'Accountancy with 2nd Specialisation in Predictive & Forensic Analytics',
                 'ACSC': 'Accountancy with Minor in Strategic Communication',
                 'ADDA': 'Accountancy with Minor in Digitalisation and Data Analytics',
                 'BCE': 'Business & Computer Engineering', 'BCG': 'Business & Computing',
                 'BUSC': 'Business with Minor in Strategic Communication',
                 'CBC': 'Chemistry and Biological Chemistry with Second Major in Business',
                 'CSBU': 'Communication Studies with Second Major in Business',
                 'ECBU': 'Economics with Second Major in Business', 'EGBM': 'Engineering with Second Major in Business',
                 'MATH': 'Mathematical Sciences', 'MS': 'Maritime Studies',
                 'MSB': 'Maritime Studies with Second Major in Business'}

bus_specialisation = {'ACS': 'Actuarial Science', 'AWM': 'Applied Wealth Management', 'BA': 'Business Analytics',
                      'BAF': 'Banking & Finance', 'PBL': 'Platform-Based Learning', 'ITP': 'International Trading',
                      'HRC': 'Human Resource Consulting', 'MKG': 'Marketing', 'RA': 'Risk Analytics',
                      'RMI': 'Risk Management & Insurance'}
null = {'[NIL]': None}
replace_dict = {'Sem 1 & Sem 2': '1,2', 'Sem 1': '1', 'Sem 2': '2'}
grammar_error = {'Mutuallly exclusive with': 'Mutually exclusive with', 'Pre-req: ': '', 'Co-req: ': '', 'Co-Req: ': ''}


def clean_symbols(text):
    cleaned_text = re.sub('[^a-zA-Z0-9\s]', '', text)  # Remove non-alphanumeric characters except whitespace
    return cleaned_text


def generate_random():
    return random.randint(1, 5)


def get_course_table(url="http://web.nbs.ntu.edu.sg/undergrad/common/contents/courselist.asp"):
    response = requests.get(url)
    if response.status_code != 200:
        print('Failed to retrieve the webpage content.')

    # Construct dataframe
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.select('table.style9')
    df_list = pd.read_html(str(table[0]), header=0)
    df = df_list[1].drop(0)

    # Clean dataframe
    df['Course Number'] = df.index - 1
    df.columns = ['Course Code', 'Name', 'AUs', 'Pre-requisites', 'Core', 'MPE', 'BDE', 'GER-PE', 'Semester Offered',
                  'Course Number']
    df['Course Code'] = df['Course Code'].apply(clean_symbols).str[:6]

    df['Semester Offered'] = df['Semester Offered'].replace(replace_dict, regex=True)
    df['Related Courses'] = df['Pre-requisites']
    df['Pre-requisites'] = df['Pre-requisites'].replace(grammar_error, regex=True).str.replace(r'Year \d+ standing', '',
                                                                                               regex=True)

    df[['Pre-requisite', 'Mutually exclusive with']] = df['Pre-requisites'].str.replace(',', '').str.split(
        'Mutually exclusive with', expand=True)
    df['Pre-requisite'] = df['Pre-requisite'].str.strip().str.split(' or ').map(
        lambda x: None if x in (['NIL'], [''], ['NIL However proficiency in English is essential']) else x)
    df['Pre-requisite'] = df['Pre-requisite'].map(
        lambda x: [re.split(r'\s&\s|\s', course) for course in x] if x else [])
    df['Mutually exclusive with'] = df['Mutually exclusive with'].str.strip().str.split(' ')

    prerequisite_map = {course: no for no, course in enumerate(df['Course Code'])}
    df['ID1'] = df['Pre-requisite'].apply(
        lambda x: [[prerequisite_map[element] for element in course if element in prerequisite_map] for course in x])
    df['ID1'] = df['ID1'].apply(lambda x: [lst for lst in x if lst])
    df['ID2'] = df['Mutually exclusive with'].apply(
        lambda x: [prerequisite_map[course] for course in x if course in prerequisite_map] if x else [])
    df['Pre-requisite'] = df['Pre-requisite'].apply(lambda x: x if x else None)

    df.drop(columns=['Pre-requisites', 'GER-PE', 'Pre-requisite', 'Mutually exclusive with'], inplace=True)
    df = df[['Course Number', 'Course Code', 'Name', 'AUs', 'Related Courses', 'Core', 'MPE', 'BDE', 'ID1', 'ID2',
             'Semester Offered']]
    df['Done before'] = 0
    df['Interest level'] = 0

    return df

