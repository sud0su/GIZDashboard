from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Undss
from .forms import UndssForm

@login_required
def InputDashboard(request):
    template = "dashboard/undss_form.html"

    form = UndssForm(request.POST or None)
    if form.is_valid():
        form.save()

    context = { 'form': form }
    return render(request, template, context)

@login_required
def Dashboard(request):
    title = 'Dashboard page'
    data = 'Statistic Info'
    template = "dashboard/dashboard_base.html"
    context = {"title": title, "data": data}
    return render(request, template, context)