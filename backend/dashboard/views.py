import pdfkit
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import RequestContext
from datetime import datetime, date
from django.utils.formats import dateformat
from django.contrib.auth.decorators import login_required

from .forms import UndssForm
from .json_serializable import Common
from giz.utils import replace_query_param

from urllib.parse import urlencode

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


# @login_required
def Dashboard(request):
    bodyparam_dict = {}
    bodyparam = urlencode(bodyparam_dict)

    if not request.GET.get('page'):
        currenturl = request.build_absolute_uri()
        return redirect(replace_query_param(currenturl, 'page', 'dashboard'))

    if 'pdf' in request.GET:
        options = {
			    'quiet': '',
			    'page-size': 'A4',
				'page-width': '2480px',
				'page-height': '3508px',
				'dpi':300,
			    # 'margin-left': 10,
			    # 'margin-right': 10,
			    'margin-bottom':10,
			    'margin-top':30,
			    'viewport-size':'1240x800',
                'header-html': 'http://'+request.META.get('HTTP_HOST')+'/static/print/header.html',
                'encoding': "UTF-8",
			    # 'lowquality':'-',
			    # 'disable-smart-shrinking':'-',
			    # 'print-media-type':'-',
			    # 'no-stop-slow-scripts':'-',
			    # 'enable-javascript':'-',
			    # 'javascript-delay': 30000,
                # 'load-error-handling': 'ignore',
			    # 'window-status': 'ready',
        }

        date_string = dateformat.format(date.today(), "Y-m-d")
        domainpath = request.META.get('HTTP_HOST')+request.META.get('PATH_INFO')
        url = 'http://'+str(domainpath)+'print?'+request.META.get('QUERY_STRING')+'&user='+str(request.user.id)+'&'+bodyparam
        pdf = pdfkit.from_url(url , False, options=options)
        response = HttpResponse(pdf, content_type='application/pdf')
        response["Content-Disposition"] = 'attachment; filename="'+request.GET['page']+'_'+date_string+'.pdf"'
        return response

    else:
        response = Common(request)
        template = "dashboard/dashboard_content.html"
        return render(request, template, response)

def DashboardPrint(request):
    template = 'dashboard/dashboard_content.html'
    response = Common(request)
    return render(request, template, response)