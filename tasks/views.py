from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Task
from .forms import TaskForm


def task_list(request):
    tasks = Task.objects.all()
    form = TaskForm()

    # Handle task creation
    if request.method == 'POST' and 'create_task' in request.POST:
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard:dashboard')  # Redirect to dashboard after creating a task

    # Handle task updates
    if request.method == 'POST' and 'task_id' in request.POST:  # Use 'task_id' to identify updates
        task_id = request.POST.get('task_id')  # Get task ID from the request
        task = get_object_or_404(Task, pk=task_id)
        form = TaskForm(request.POST, instance=task)  # Bind form to existing task instance
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})  # Respond with JSON for AJAX success

    context = {'tasks': tasks, 'form': form}
    return render(request, 'tasks/tasks.html', context)

def get_task(request):
    task_id = request.GET.get('task_id')  # Get task ID from query parameters
    task = get_object_or_404(Task, pk=task_id)  # Fetch the task
    data = {
        'title': task.title,
        'complete': task.complete
    }
    return JsonResponse(data)  # Return task data as JSON


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

