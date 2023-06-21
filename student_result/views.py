from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.serializers import serialize
from .models import Session
import pandas as pd
import json

def home(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "login successful!")
        else:
            messages.error(request, "problem with login!")
        return redirect('home')
    else:
        return render(request, 'home.html', {})

def user_logout(request):
    logout(request)
    messages.success(request, "successfully logged out!")
    return redirect('home')

def semester(request, session_id, semester_id):
    return render(request, 'semester.html', {'session_id' : session_id, 'semester_id' : semester_id})

def add_session(request):
    if request.method == 'POST':
        year = request.POST['year']
        name = request.POST['name']
        file = request.FILES['upload_file']
        df = pd.read_excel(file)
        course_list = []
        for i in range(0, df.shape[0]):
            session_info = {}
            session_info['code'] = df.iloc[i]['Code']
            session_info['title'] = df.iloc[i]['Title']
            session_info['credit'] = df.iloc[i]['Credit']
            course_list.append(session_info)
        new_session = Session()
        new_session.year = year
        new_session.name = name
        new_session.courses = json.dumps(course_list, indent=4)
        new_session.save()
    return render(request, 'add_session.html', {})

def view_session(request, year):
    session = Session.objects.get(year=year)
    name = session.name
    courses = json.loads(session.courses)
    return render(request, 'view_session.html', {'year' : year, 'name' : name, 'courses' : courses})


def lg_cal(n):
        if (n < 2.00):
            return "F"
        elif (n < 2.25):
            return "C-"
        elif (n < 2.50):
            return "C"
        elif (n < 2.75):
            return "C+"
        elif (n < 3.00):
            return "B-"
        elif (n < 3.25):
            return "B"
        elif (n < 3.50):
            return "B+"
        elif (n < 3.75):
            return "A-"
        elif (n < 4.00):
            return "A"
        else:
            return "A+"


def gen (df, reg, credit_list, title_list):
    sem_full = []
    sem_final = {}
    idx = df.columns
    df1 = df.loc[df[idx[1]] == reg]
    name = df1[idx[2]].values[0]

    # 1st semester
    sem_code = []
    sem_lg = []
    sem_gp = []
    for i in range(1, len(idx)):
        raw = idx[i].split("_")
        if raw[0] != 'GP':
            continue
        if (str(df1[idx[i]].values[0]) == 'nan'):
            continue
        st = raw[1]
        a = ""
        b = ""
        for c in st:
            if c >= 'A' and c <= 'Z':
                a = a + c
            elif c >= '0' and c <= '9':
                b = b + c
        st1 = a + " " + b
        # print(st1)
        sem_code.append(st1)
        sem_gp.append(df1[idx[i]].values[0])
        sem_lg.append(df1[idx[i + 1]].values[0])

        # sem_cr.append(df1[idx[i + 2]].values[0])
    sem_final['cr_cur'] = (df1['Credit'].values[0])
    sem_final['gp_cur'] = (df1['GPA'].values[0])
    sem_final['lg_cur'] = (lg_cal(df1['GPA'].values[0]))
    sem_final['cr_com'] = (df1['CCredit'].values[0])
    sem_final['gp_com'] = (df1['CGPA'].values[0])
    sem_final['lg_com'] = (lg_cal(df1['CGPA'].values[0]))
    # print(sem_code, sem_gp, sem_lg, sem_cr, sem_final)
    for i in range(0, len(sem_code)):
        dict = {}
        dict['code'] = sem_code[i]
        if sem_code[i] in title_list:
            dict['title'] = title_list[sem_code[i]]
        else: 
            dict['title'] = "nothing"
        dict['gp'] = sem_gp[i]
        dict['lg'] = sem_lg[i]
        if sem_code[i] in credit_list:
            dict['cr'] = credit_list[sem_code[i]]
        else:
            dict['cr'] = "nan"
        sem_full.append(dict)
    ret = {}
    ret['sem_full'] = sem_full
    ret['sem_final'] = sem_final
    ret['name'] = name
    return ret

