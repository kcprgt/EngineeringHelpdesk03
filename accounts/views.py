from django.contrib.auth import views as auth_views
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})
        