from flask import Blueprint, render_template, request, session, g
from .wrangle import get_course_table
from .filter import filter_course
from .model import optimization_model
from .database import SessionData
from . import db
import pandas as pd
from bs4 import BeautifulSoup

auth = Blueprint('auth', __name__)

df = get_course_table()
df.drop(columns=['ID1','ID2','Done before','Core','MPE','BDE'], inplace=True)
df_interest = df.copy()

@auth.route('/optimize', methods=['GET','POST'])
def optimize():
    if request.method == 'POST':
        if request.headers['Content-Type'] == 'application/json':
            try:
                data = request.get_json()
                table_data = data.get('optimizedContent')
                soup = BeautifulSoup(table_data, 'html.parser')
                tbody_list = soup.find_all('tbody')

                data = []
                for tbody in tbody_list:
                    for row in tbody.find_all('tr'):
                        cols = row.find_all('td')
                        cols = [col.text.strip() for col in cols]
                        data.append(cols)
                columns = ['Course Number', 'Course Code', 'Name', 'Interest level']
                interest_course = pd.DataFrame(data, columns=columns)
                interest_course['Interest level'] = interest_course['Interest level'].apply(lambda x: int(x))
                interest_course['Course Number'] = interest_course['Course Number'].apply(lambda x: int(x))
                session['interest_course'] = interest_course.to_dict(orient='records')
            except Exception as e:
                pass
        else:
            course_done = [request.form.get(f'done{i}') for i in range(1, 11) if request.form.get(f'done{i}')]
            session['course_done'] = course_done
            max_num = [request.form.get(f'maxsem{i}') for i in range(1, 3)]
            session['max_num'] = max_num
            max_credit = [request.form.get(f'maxsem{i}') for i in range(3, 5)]
            session['max_credit'] = max_credit

        course_done = session.get('course_done', [])
        max_num = session.get('max_num', [])
        max_credit = session.get('max_credit', [])
        print(course_done)
        print(max_num)
        print(max_credit)
    return render_template('optimize.html')

@auth.route('/result')
def logout():
    all_course = get_course_table()
    n = len(all_course)
    interest_course = pd.DataFrame(session.get('interest_course', []))
    course_done = session.get('course_done', [])
    max_num = session.get('max_num', [])
    max_credit = session.get('max_credit', [])
    for index, row in interest_course.iterrows():
        course_number = row['Course Number']
        interest_level = row['Interest level']
        all_course.loc[all_course['Course Number'] == course_number, 'Interest level'] = interest_level
    all_course.loc[df['Course Code'].isin(course_done), 'Done before'] = 1

    result = optimization_model(interest_course, all_course, max_num, max_credit)
    objective = round(result[0], 1)
    solution = result[1]
    credit = result[2]
    total = sum(sum(solution,[]))
    count1 = sum(solution[0])
    count2 = sum(solution[1])
    credit1 = sum([x * y for x, y in zip(solution[0], credit)])
    credit2 = sum([x * y for x, y in zip(solution[1], credit)])

    detail1 = [[all_course["Course Number"].values[j], all_course["Course Code"].values[j], all_course["Name"].values[j],
               all_course['AUs'].values[j], all_course['Interest level'].values[j]] for j in range(n) if
              solution[0][j] == 1]
    detail2 = [[all_course["Course Number"].values[j], all_course["Course Code"].values[j], all_course["Name"].values[j],
                all_course['AUs'].values[j], all_course['Interest level'].values[j]] for j in range(n) if
               solution[1][j] == 1]
    columns = ['Course Number','Course Code', 'Name', 'AUs', 'Interest level']
    table1 = pd.DataFrame(detail1, columns=columns)
    table1.index = table1.index + 1
    table1 = table1.to_html(classes='data', header="true")
    table2 = pd.DataFrame(detail2, columns=columns)
    table2.index = table2.index + 1
    table2 = table2.to_html(classes='data', header="true")

    return render_template('output.html', objective=objective, total=total, count1=count1, credit1=credit1,
                           count2=count2, credit2=credit2, table1=table1, table2=table2)

@auth.route('/', methods=['GET', 'POST'])
def select():
    df_copy = df.copy()

    if request.method == 'POST':
        coursecode = request.form.get('coursecode')
        coursename = request.form.get('coursename')
        credit = request.form.get('credit')
        prerequisite = request.form.get('prerequisite')
        semester = request.form.get('semester')

        print(coursecode)

        df_filtered = filter_course(df_copy, coursecode, coursename, credit, prerequisite, semester)
        global df_interest
        df_interest = df_filtered

    else:
        df_filtered = df_copy
    df_filtered['Selection'] = '<button type="button" id="myButton" onclick="copyRow(this)">Select</button>'

    return render_template('select.html', tables=[df_filtered.to_html(classes='data', header="true", escape=False)])


