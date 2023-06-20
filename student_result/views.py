from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
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