from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from .forms import UndssForm
from .json_serializable import Common
from giz.utils import replace_query_param

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
    
    if not request.GET.get('page'):
        currenturl = request.build_absolute_uri()
        return redirect(replace_query_param(currenturl, 'page', 'dashboard'))

    response = Common(request)
    # template = "dashboard/dashboard_base.html"
    template = "dashboard/dashboard_content.html"
    return render(request, template, response)