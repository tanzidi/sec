from django.db import models
from django.contrib.auth.models import User

class Session(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    year = models.CharField(max_length=10)
    name = models.CharField(max_length=20)
    courses = models.TextField()
    def __str__(self):
        return(f"{self.year} {self.name}")

class Student(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    regi = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    hall = models.BooleanField(default=False)
    session = models.ForeignKey(Session, null=True, on_delete=models.CASCADE) 
    # on_delete=models.CASCADE means when a reference is detelted it will delete the related data also
    def __str__(self):
        return(self.name)
    
class Semester(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    def __str__(self):
        return(self.name)
    
class Exam(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(Session, null=True, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, null=True, on_delete=models.CASCADE)
    held = models.CharField(max_length=20)
    def __str__(self):
        return(f"{self.semester} {self.held}")
    
class Result(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(Student, null=True, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, null=True, on_delete=models.CASCADE)
    result = models.TextField()
    def __str__(self):
        return(f"{self.student} {self.exam}")