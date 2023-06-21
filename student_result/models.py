from django.db import models

class Session(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    year = models.CharField(max_length=10)
    name = models.CharField(max_length=20)
    courses = models.TextField()
    def __str__(self):
        return(f"{self.year} {self.name}")

class Student(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    regi = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    hall = models.BooleanField(default=False)
    session = models.ForeignKey(Session, null=True, on_delete=models.SET_NULL)
    def __str__(self):
        return(self.name)
    
class Semester(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    def __str__(self):
        return(self.name)
    
class Exam(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(Session, null=True, on_delete=models.SET_NULL)
    semester = models.ForeignKey(Semester, null=True, on_delete=models.SET_NULL)
    held = models.CharField(max_length=20)
    def __str__(self):
        return(f"{self.semester} {self.held}")
    
class Result(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(Student, null=True, on_delete=models.SET_NULL)
    exam = models.ForeignKey(Exam, null=True, on_delete=models.SET_NULL)
    result = models.TextField()
    def __str__(self):
        return(f"{self.student} {self.Exam}")