from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Task
from .forms import TaskForm

def task_list(request):
    tasks = Task.objects.all()
    form = TaskForm()

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard:dashboard')  # Redirect to dashboard after creating a task
    
    context = {'tasks': tasks, 'form': form}
    return render(request, 'tasks/tasks.html', context)

def create_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        complete = request.POST.get('complete') == 'True'
        task = Task.objects.create(title=title, complete=complete)
        
        # Redirect to the dashboard after creating a task
        return redirect('dashboard:dashboard')  # Adjust this to your dashboard URL
    
    return JsonResponse({'success': False, 'errors': 'Invalid request'}, status=400)

def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('dashboard:dashboard')  # Redirect to the dashboard after updating the task
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/update_task.html', {'form': form, 'task': task})

def delete_task(request, pk):
    item = get_object_or_404(Task, id=pk)
    
    if request.method == 'POST':
        item.delete()
        return redirect('tasks:list')
    
    context = {'item': item}
    return render(request, 'tasks/delete.html', context)

def toggle_task_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.complete = not task.complete
    task.save()
    return redirect('tasks:list')

