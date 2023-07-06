import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Session, Exam, Semester, Student, Result
import pandas as pd
import json
import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            print('hi')
            return redirect('teacher')
        else:
            return redirect('student')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "login successful!")
            return redirect('home')
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
        return redirect('add_session')
    session_obj = Session.objects.all()
    return render(request, 'add_session.html', {'sessions' : session_obj})

def view_session(request, year):
    if request.user.is_authenticated and request.user.is_superuser:
        session = Session.objects.get(year=year)
        name = session.name
        courses = json.loads(session.courses)
        student_obj = Student.objects.filter(session=session)
        context = {}
        context['year'] = year
        context['name'] = name
        context['courses'] = courses
        context['students'] = student_obj
        return render(request, 'view_session.html', context)
    else:
      return redirect('home')


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
    df1 = df.loc[df[idx[1]] == int(reg)]
    if (df1.empty):
        return "nothing"
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

def add_result(request, session, semester):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            session_obj = Session.objects.get(year=session)
            semester_obj = Semester.objects.get(id=semester)
            exam = Exam.objects.get(session=session_obj, semester=semester_obj)

            courses = json.loads(session_obj.courses)
            title_list = {}
            credit_list = {}
            for course in courses:
                title_list[course['code']] = course['title']
                credit_list[course['code']] = course['credit']
            
            if request.method == 'POST':
                file = request.FILES['upload_file']
                df = pd.read_excel(file)
                cols = df.columns
                regis = list(df[cols[1]])
                for i in regis:
                    try:
                        ret = gen(df=df, reg=i, credit_list=credit_list, title_list=title_list)
                    except:
                        messages.error("problem with parsing file")
                        pass
                    try:
                        result = Result()
                        result.regi = i
                        result.exam = exam
                        ret['held'] = exam.held
                        result.result = json.dumps(ret, indent=4, cls=NpEncoder)
                        result.save()
                    except:
                        messages.erro(request, "error uploading resutl")
                        pass
        except:
            messages.error(request, "No exam found add an exam first")
            return redirect('teacher')
        try:
            exam_obj = Exam.objects.get(semester=semester_obj, session=session_obj)
            result_obj = Result.objects.filter(exam=exam_obj)
            results = []
            for i in result_obj:
                individual = {}
                try:
                    student_obj = Student.objects.get(regi=i.regi)
                    individual['student'] = student_obj
                except:
                    pass
                individual['regi'] = i.regi
                individual['result_id'] = i.id
                results.append(individual)
            context = {}
            context['status'] = 2
            context['results'] = results
            context['session'] = session
            context['semester'] = semester_obj.name
            context['exam_id'] = exam_obj.id
            return render(request, 'add_result.html', context)
        except:
            return render(request, 'add_result.html', {'status' : 1})
        # return render(request, 'add_result.html', {})
    else:
        messages.error(request, "You must be a teacher")
        return redirect('home')


def student(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            student_obj = Student()
            student_obj.regi = request.POST['regi']
            student_obj.name = request.POST['name']
            student_obj.email = request.POST['email']
            student_obj.phone = request.POST['phone']
            student_obj.address = request.POST['address']
            if request.POST['hall'] == '1':
                student_obj.hall = True
            else:
                student_obj.hall = False
            session_obj = Session.objects.get(id=request.POST['session'])
            print(session_obj)
            student_obj.session = session_obj
            student_obj.user_id = request.user
            student_obj.save()
        try:
            student = Student.objects.get(user_id=request.user)
            if student :
                semesters = Semester.objects.all()
                results = Result.objects.filter(regi=student.regi)
                # print(results)
                return render(request, 'student.html', {'status' : 1, 'student' : student, 'semesters' : semesters, 'results' : results})
            else:
                sessions = Session.objects.all()
                return render(request, 'student.html', {'status' : 0, 'sessions' : sessions})
        except:
            sessions = Session.objects.all()
            return render(request, 'student.html', {'status' : 0, 'sessions' : sessions})
    messages.error(request, "oops you need to login first!")
    return redirect('home')

def result(request, result_id):
    if request.user.is_authenticated:
        try:
            student_obj = Student.objects.get(user_id = request.user)
            try:
                result_obj = Result.objects.get(id=result_id)
                if result_obj.regi != student_obj.regi:
                    messages.error(request, "Not allowed to see the result!")
                    return redirect('student')
                result_r = result_obj.result
                result = json.loads(result_r)
                context = {}
                context['sem_full'] = result['sem_full']
                context['sem_final'] = result['sem_final']
                context['held'] = result_obj.exam.held
                context['student'] = student_obj
                context['semester'] = result_obj.exam.semester
                # print(context)
                return render(request, 'result.html', context)
            except:
                messages.error(request, "no result found")
                return redirect('student')
        except:
            messages.error(request, "plese register the student first")
            return redirect('student')
    else:
        messages.error(request, "login first")
        return redirect('home')
    
def teacher(request):
    if request.user.is_authenticated and request.user.is_superuser:
        sessions = Session.objects.all()
        semesters = Semester.objects.all()
        if request.method == 'POST':
            session = request.POST['session']
            return render(request, 'teacher.html', {'status' : 1, 'session' : session, 'semesters' : semesters, 'sessions' : sessions}) 
        return render(request, 'teacher.html', {'sessions' : sessions})
    else:
        messages.error(request, "You must be a teacher")
        return redirect('home')

def teacher_result(request, result_id):
    if request.user.is_authenticated and request.user.is_superuser:
        result_obj = Result.objects.get(id=result_id)
        student_obj = Student.objects.filter(regi=result_obj.regi)
        # print(student_obj)
        semester = result_obj.exam.semester.name
        result = json.loads(result_obj.result)
        context = {}
        context['sem_full'] = result['sem_full']
        context['sem_final'] = result['sem_final']
        context['student'] = student_obj
        context['semester'] = semester
        context['semester_id'] = result_obj.exam.semester.id
        context['regi'] = result_obj.regi
        context['result_id'] = result_id
        return render(request, 'teacher_result.html', context)
    else:
        messages.error(request, "You must be a teacher")
        return redirect('home')
    
def delete_result(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'POST':
            obj = Result.objects.get(id=request.POST['result_id'])
            next = "/add_result" + request.POST['next']
            obj.delete()

        return HttpResponseRedirect(next)
    else:
        messages.error(request, "You must be a teacher")
        return redirect('home')

def delete_results(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'POST':
            exam_obj = Exam.objects.get(id=request.POST['exam_id'])
            result_obj = Result.objects.filter(exam=exam_obj)
            result_obj.delete()
            next = request.POST['next']
            return HttpResponseRedirect(next)
    else:
        messages.error(request, "You must be a teacher")
        return redirect('home')
    
def add_exam(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'POST':
            session_obj = Session.objects.get(id=request.POST['session'])
            semester_obj = Semester.objects.get(id=request.POST['semester'])
            exam_obj = Exam()
            exam_obj.session = session_obj
            exam_obj.semester = semester_obj
            exam_obj.held = request.POST['held']
            exam_obj.save()
        session_obj = Session.objects.all()
        semester_obj = Semester.objects.all()
        exam_list = []
        for i in session_obj:
            exam_obj = Exam.objects.filter(session=i)
            exam_indi = {}
            exam_indi['session'] = i.year
            exlist = []
            for j in exam_obj:
                exlist.append(j)
            exam_indi['exams'] = exlist
            exam_list.append(exam_indi)
        context = {}
        context['sessions'] = session_obj
        context['semesters'] = semester_obj
        context['exam_list'] = exam_list
        return render(request, 'add_exam.html', context) 
    else:
        messages.error(request, "You must be a teacher")
        return redirect('home')
def gradesheet(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return render(request, 'gradesheet.html', {})
    else:
        messages.error(request, "You must be a teacher")
        return redirect('home')

def gen_gradesheet(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'POST':
            regi = request.POST['regi']
            # try:
            student_obj = Student.objects.get(regi=regi)
            result_obj = Result.objects.filter(regi=regi)
            
            held = []
            sem_fulls = []
            sem_finals = []
            for i in range(0, 9):
                held.append("##########")
                sem_fulls.append("##########")
                sem_finals.append("##########")
            j = 0
            for res in result_obj:
                held[j] = res.exam.held
                r = json.loads(res.result)
                sem_fulls[j] = (r['sem_full'])
                sem_finals[j] = (r['sem_final'])
                j = j + 1
            print(sem_fulls)
            print(sem_finals)
            x = datetime.datetime.now()
            now = x.strftime("%d") + "-" + x.strftime("%b") + "-" + x.strftime("%y")
            s = str(student_obj.session)
            context = {
                "name" : student_obj.name,
                "reg" : regi,
                "session" : student_obj.session.year,
                "year" : s.split('-')[0],
                "now" : now,
                "h1" : held[0],
                "h2" : held[1], 
                "h3" : held[2], 
                "h4" : held[3], 
                "h5" : held[4], 
                "h6" : held[5],  
                "h7" : held[6],  
                "h8" : held[7], 
                "h8_ex" : held[8],  
                "sem1" : sem_fulls[0],
                "sem1_final" : sem_finals[0],
                "sem2" : sem_fulls[1],
                "sem2_final" : sem_finals[1],
                "sem3" : sem_fulls[2],
                "sem3_final" : sem_finals[2],
                "sem4" : sem_fulls[3],
                "sem4_final" : sem_finals[3],
                "sem5" : sem_fulls[4],
                "sem5_final" : sem_finals[4],
                "sem6" : sem_fulls[5],
                "sem6_final" : sem_finals[5],
                "sem7" : sem_fulls[6],
                "sem7_final" : sem_finals[6],
                "sem8" : sem_fulls[7],
                "sem8_final" : sem_finals[7],
                "sem8_ex" : sem_fulls[8],
                "sem8_ex_final" : sem_finals[8],
            }
            print(context)
            return render(request, 'gen_gradesheet.html', context)
            # except:
                # messages.error(request, "No result found!")
                # return redirect('gradesheet')
        else:
            return redirect('gradesheet')
    else:
        messages.error(request, "You must be a teacher")
        return redirect('home')