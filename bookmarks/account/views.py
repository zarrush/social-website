from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import LoginForm


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data

            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password']
            )

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                return HttpResponse("Invalid credentials.")

    else:
        form = LoginForm()

    return render(
        request,
        'account/login.html',
        {'form': form}
    )


@login_required
def dashboard(request):
    return render(
        request,
        'account/dashboard.html',
        {'section': 'dashboard'}
    )


@login_required
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')

    return redirect('dashboard')



def images(request):
    return render(
        request,
        'account/images.html',
        {'section': 'images'}
    )


def peoples(request):
    return render(
        request,
        'account/peoples.html',
        {'section': 'peoples'}
    )