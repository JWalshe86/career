from django.shortcuts import render, redirect

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


