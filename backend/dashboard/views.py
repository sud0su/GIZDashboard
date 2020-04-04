from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from .forms import UndssForm
from .json_serializable import Common

@login_required
def InputDashboard(request):
    template = "dashboard/undss_form.html"

    # form = UndssForm(request.POST or None)
    # if form.is_valid():
    #     form.save()

    form = UndssForm(request.POST, request.FILES or None)
    if form.is_valid():
        form.save()

    # if request.method == 'POST':
    #     form = UndssForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         form.save()
    # else:
    #     form = UndssForm()

    context = {'form': form }
    return render(request, template, context)


@login_required
def Dashboard(request):
    response = Common(request)
    template = "dashboard/dashboard_base.html"
    return render(request, template, response)