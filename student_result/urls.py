from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.user_logout, name='logout'),
    path('semester/<slug:session_id>/<int:semester_id>/', views.semester, name='semester'),
    path('add_session/', views.add_session, name = 'add_session'),
    path('view_session/<slug:year>/', views.view_session, name='view_session'),
    path('add_result/<slug:session>/<int:semester>/', views.add_result, name='add_result'),
    path('student/', views.student, name='student'),
    path('result/<slug:session>/<int:semester>/', views.result, name='result'),
    path('teacher/', views.teacher, name='teacher'),
    path('teacher/<int:result_id>/', views.teacher_result, name='teacher_result'),
    path('delete_result/', views.delete_result, name='delete_result'),
    path('delete_results/', views.delete_results, name='delete_results'),
    
]
