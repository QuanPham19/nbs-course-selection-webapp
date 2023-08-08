from flask import Blueprint, render_template, request
from .wrangle import get_course_table

df = get_course_table()
df.drop(columns=['ID1','ID2','Done before','Interest level'], inplace=True)
table_html = df.to_html(classes='table table-bordered table-striped', index=False)

views = Blueprint('views', __name__)
@views.route('/all', methods=['GET', 'POST'])
def home():
    return render_template('all.html', tables=[df.to_html(classes='data', header="true")])

