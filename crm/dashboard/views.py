from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserLoginForm

# Create your views here.
def home(request):
    return render(request, 'base/base.html')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = UserLoginForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            print(email)
            password = form.cleaned_data['password']
            print(password)
            # Perform authentication here
            user = authenticate(request, email=email, password=password)
            print(user)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                print("No user specified")
                form.add_error(None, 'Invalid email or password')
                return render(request, 'auth/login.html', {'form': form})
    return render(request, 'auth/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')