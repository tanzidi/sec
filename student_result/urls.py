from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.user_logout, name='logout'),
    path('semester/<slug:session_id>/<int:semester_id>', views.semester, name='semester'),
    path('add_session/', views.add_session, name = 'add_session'),
    path('view_session/<slug:year>', views.view_session, name='view_session'),
    path('add_result/<slug:session>/<int:semester>', views.add_result, name='add_result'),
    path('student/', views.student, name='student'),

]
