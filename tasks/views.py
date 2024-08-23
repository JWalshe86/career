from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest

from .models import *
from .forms import *

def index(request):

    tasks = Task.objects.all()
    
    form = TaskForm()

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/tasks/')
    context = {'tasks': tasks, 'form': form}
    return render(request, 'tasks/list.html', context)


def updateTask(request, pk):
    task = get_object_or_404(Task, id=pk)

    if request.method == 'POST':
        # Updating the task based on the POST data
        task.complete = 'complete' in request.POST  # Update based on checkbox
        task.title = request.POST.get('title', task.title)  # Preserve the title if unchanged
        task.save()
        return redirect('/tasks')  # Redirect to the task list or any other desired page

    else:
        # Pre-fill the form with the existing task data for GET requests
        form = TaskForm(instance=task)

    context = {'form': form, 'task': task}
    return render(request, 'tasks/update_task.html', context)

def deleteTask(request, pk):
    item = get_object_or_404(Task, id=pk)
    
    if request.method == 'POST':
        item.delete()
        return redirect('/tasks')  # Redirect to home or any other page you want after deletion
    
    # Handle GET request or other methods
    context = {'item': item}
    return render(request, 'tasks/delete.html', context)    











