from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from . forms import RegisterUserForm
from django.contrib import messages

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username= username, password= password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are logged in')
            return redirect('home')
        else:
            messages.error(request, 'Error check information again')
            return render(request, 'authenticate/login.html', {})
    else:
        return render(request, 'authenticate/login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, 'You were logged out')
    return redirect('login')

def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            if User.objects.filter(username=username).exists() or User.objects.filter(password=password).exists():
                messages.error(request, 'Username or email already exists. Please choose a different one.')
                return render(request, 'authenticate/register_user.html', {'form': form})
            user = authenticate(username=username, password=password)   
            login(request, user)
            messages.success(request,'Registation succesfull!')
            return redirect('home')
        else:
            messages.error(request,'Please check the information again..!')
            return render(request, 'authenticate/register_user.html', {'form':form})
    else:
        form = RegisterUserForm
        return render(request, 'authenticate/register_user.html', {'form':form})