import numpy as np
import pandas as pd
from rsome import ro
from rsome import grb_solver as grb

def optimization_model(interest_course, all_course, max_num, max_credit):
    interest_list = interest_course['Course Number'].values
    all_preq_list = all_course['ID1'].values
    credit = np.array(list(map(int, all_course['AUs'].values)))
    d = np.array(all_course['Done before'])
    m = max(all_course['ID1'].apply(lambda x: len(x)).values)
    n = len(all_course)
    a = np.zeros((2, n))
    I = all_course['Interest level'].values
    for j in range(n):
        if all_course['Semester Offered'].values[j] == '1,2':
            a[0][j] = 1
            a[1][j] = 1
        elif all_course['Semester Offered'].values[j] == '1':
            a[0][j] = 1
        else:
            a[1][j] = 1

    model = ro.Model("Course Selection 2.0")
    x = model.dvar((2, n), "B")
    y = model.dvar((m, n), "B")
    z = model.dvar((m, n), "B")

    model.max(x.sum(axis=0) @ I)

    # Semester offered constraint
    model.st(x <= a)

    # Finished course constraint
    model.st(x.sum(axis=0) <= 1 - d)

    # Total course per semester constraint
    for i in range(len(max_num)):
        try:
            max_num[i] = int(max_num[i])
        except Exception as e:
            max_num[i] = 6
    model.st(x[i, :].sum() <= max_num[i] for i in range(2))

    # Total AUs per semester constraint
    for i in range(len(max_credit)):
        try:
            max_credit[i] = int(max_credit[i])
        except Exception as e:
            max_credit[i] = 18
    model.st(x[i, :] @ credit <= max_credit[i] for i in range(2))

    # Interest subset constraint
    model.st(x[:, i].sum() == 0 for i in range(n) if i not in interest_course['Course Number'].values)

    # Pre-requisites Sem 1 constraint
    for i in interest_list:
        if len(all_preq_list[i]) != 0:
            for j in range(3):
                if j in range(len(all_preq_list[i])):
                    model.st(y[j, i] <= sum([d[k] for k in all_preq_list[i][j]]) / len(all_preq_list[i][j]))
                else:
                    model.st(y[j, i] <= 0)
            model.st(x[0, i] <= y[:, i].sum())

    # Pre-requisites Sem 2 constraint
    for i in interest_list:
        if len(all_preq_list[i]) != 0:
            for j in range(3):
                if j in range(len(all_preq_list[i])):
                    model.st(len((all_preq_list)[i][j]) * z[j, i] - sum([x[0, k] for k in all_preq_list[i][j]]) <= sum(
                        [d[k] for k in all_preq_list[i][j]]))
                else:
                    model.st(z[j, i] <= 0)
            model.st(x[1, i] <= z[:, i].sum())

    # Mutually exclusive constraint
    for i in interest_list:
        if len(all_course['ID2'].values[i]) != 0:
            mutual_id = all_course['ID2'].values[i]
            model.st(x[:, i].sum() + sum([x[:, j].sum() for j in mutual_id]) <= 1)

    model.solve(grb)
    print(f'Objective total interest: {model.get()}')
    # print(f'Optimal solution: ')
    # print(x.get())

    print("--------------------------------------------------------------")
    print(f"For the first semester, we will suggest Linda to select courses of total {x.get()[0, :] @ credit} AUs")
    for j in range(n):
        if x.get()[0][j] == 1:
            print(all_course["Course Code"].values[j], all_course["Name"].values[j], ': ', all_course['AUs'].values[j],
                  'AUs')

    print("---------------------------------------------------------------")
    print(f"For the second semester, we will suggest Linda to select courses of total {x.get()[1, :] @ credit} AUs")
    for j in range(n):
        if x.get()[1][j] == 1:
            print(all_course["Course Code"].values[j], all_course["Name"].values[j], ': ', all_course['AUs'].values[j],
                  'AUs')
    return [model.get(), x.get().tolist(), credit.tolist()]