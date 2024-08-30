from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Task
from .forms import TaskForm

def task_list(request):
    tasks = Task.objects.all()
    form = TaskForm()

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/tasks/')
    
    context = {'tasks': tasks, 'form': form}
    return render(request, 'tasks/list.html', context)


def create_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        complete = request.POST.get('complete') == 'True'
        task = Task.objects.create(title=title, complete=complete)
        
        response_data = {
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'complete': task.complete
            }
        }
        print(f"Task ID: {task.id}")        
        return JsonResponse(response_data)
    
    return JsonResponse({'success': False, 'errors': 'Invalid request'}, status=400)


def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk)  # Fetch the task by primary key
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks:list')  # Redirect to a page after saving
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/update_task.html', {'form': form, 'task': task})


def delete_task(request, pk):
    item = get_object_or_404(Task, id=pk)
    
    if request.method == 'POST':
        item.delete()
        return redirect('/tasks')  # Redirect to home or any other page you want after deletion
    
    context = {'item': item}
    return render(request, 'tasks/delete.html', context)    

def toggle_task_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.complete = not task.complete
    task.save()
    return redirect('tasks:list')  # Redirect to the tasks dashboard or another appropriate page

