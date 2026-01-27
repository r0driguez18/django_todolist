from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task

@login_required
def task_list(request):
    q = Task.objects.filter(owner=request.user)
    status = request.GET.get('status')
    if status == 'done':
        q = q.filter(is_done=True)
    elif status == 'pending':
        q = q.filter(is_done=False)
    ctx = {
        'tasks': q,
    }
    return render(request, 'tasks/list.html', ctx)

@login_required
def create_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        if title:
            Task.objects.create(owner=request.user, title=title, description=description)
            return redirect('task_list')
    return render(request, 'tasks/create.html')

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)
    if request.method == 'POST':
        task.title = request.POST.get('title', task.title)
        task.description = request.POST.get('description', task.description)
        task.save()
        return redirect('task_list')
    return render(request, 'tasks/edit.html', {'task': task})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'tasks/delete.html', {'task': task})

@login_required
def toggle_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)
    task.is_done = not task.is_done
    task.save()
    return redirect('task_list')
