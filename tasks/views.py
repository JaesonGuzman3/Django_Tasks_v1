from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .form import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# from django.http import HttpResponse


# Create your views here.
def home(request):
    return render(request, 'home.html', {
    })


def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })

    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'],
                                                password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    "error": 'usuario ya existe'
                })

        return render(request, 'signup.html', {
            'form': UserCreationForm,
            "error": 'CONTRASEÑA NO COINCIDEN'
        })


@login_required
def tasks(request):

    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)

    return render(request, 'tasks.html', {'tasks': tasks})


@login_required
def tasks_completed(request):

    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False)

    return render(request, 'tasks.html', {'tasks': tasks})


@login_required
def create_task(request):

    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except VelueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Revise los datos ingresados'
            })


@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task1 = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task1)
        return render(request, 'task_detail.html', {'task': task1, 'form': form})
    else:
        try:
            task1 = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task1)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html',
                          {'task': Task, 'form': form,
                           'error': "Error actialiando tareas"})


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, 
                             pk=task_id, 
                             user=request.user).order_by('-datecompleted')
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')
    

@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Usuario o Contraseña incorrecto'
            })
        else:
            login(request, user)
            return redirect('tasks')
