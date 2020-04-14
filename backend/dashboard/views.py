import pdfkit
import urllib

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
from .pychromeprint import print_from_urls

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

	headerparam_dict = {p: request.GET.get(p, '') for p in ['hideuserinfo','lang'] if p in request.GET}
	headerparam_dict.update({
		# 'onpdf': user_logo.get('onpdf'),
		# 'userlogo': user_logo.get('logo_url'),
		# 'name': request.user.first_name+' '+request.user.last_name,
		# 'cust_title': '%s %s'%('Dashboard',request.GET.get('page', '').title()),
		# 'organization': (request.user.organization or ''),
	})
	headerparam = urllib.parse.urlencode(headerparam_dict)

	if not request.GET.get('page'):
		currenturl = request.build_absolute_uri()
		return redirect(replace_query_param(currenturl, 'page', 'dashboard'))

	if 'pdf' in request.GET:
		options = {
			# pychrome settings
			# match screen to print layout and resolution as close as possible
			# in order for the map to scale correctly
			# for print debugging, uncomment ruler.png in custombase.html,
			# resolution in pixel, size in inches, time in seconds
			'screen-width':1024, # resolution when loading the page
			'screen-height':1024, # resolution when loading the page
			'paperWidth':8.27,
			'paperHeight':11.69,
			'marginTop':0.78,
			'marginBottom':0.45,
			'marginLeft':0.3,
			'marginRight':0.3,
			'scale':0.71, # 0.71 roughly equal to 1024 px print width on 1024 screen-width
			'after-document-loaded-delay': 1, # in seconds
			'timeout': 60, # in seconds
			# 'header-html': 'http://%s/static/epr_bgd/head_print/rep_header_chrome.html?%s'%(request.META.get('HTTP_HOST'),headerparam),
			'header-html': 'http://'+request.META.get('HTTP_HOST')+'/static/print/header_chrome.html',
			'headerparam':headerparam_dict,
		}
		# if re.match('^/v2', request.path):
		# 	options['viewport-size'] = '1240x800'
		domainpath = request.META.get('HTTP_HOST')+request.META.get('PATH_INFO')
		url = 'http://'+str(domainpath)+'print?'+request.META.get('QUERY_STRING')+'&user='+str(request.user.id)+'&'+bodyparam
		print('print url', url)
		# pdf = pdfkit.from_url(url, False, options=options)
		pdf = print_from_urls([url], print_option=options)
		date_string = dateformat.format(datetime.now(), "Y-m-d")
		response = HttpResponse(pdf,content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="'+request.GET['page']+'_'+date_string+'.pdf"'
		return response

		# options = {
		# 		'quiet': '',
		# 		'page-size': 'A4',
		# 		'page-width': '2480px',
		# 		'page-height': '3508px',
		# 		'dpi':300,
		# 		# 'margin-left': 10,
		# 		# 'margin-right': 10,
		# 		'margin-bottom':10,
		# 		'margin-top':30,
		# 		'viewport-size':'1240x800',
		# 		'header-html': 'http://'+request.META.get('HTTP_HOST')+'/static/print/header.html',
		# 		'encoding': "UTF-8",
		# 		# 'lowquality':'-',
		# 		# 'disable-smart-shrinking':'-',
		# 		# 'print-media-type':'-',
		# 		# 'no-stop-slow-scripts':'-',
		# 		# 'enable-javascript':'-',
		# 		# 'javascript-delay': 30000,
		# 		# 'load-error-handling': 'ignore',
		# 		# 'window-status': 'ready',
		# }

		# date_string = dateformat.format(date.today(), "Y-m-d")
		# domainpath = request.META.get('HTTP_HOST')+request.META.get('PATH_INFO')
		# url = 'http://'+str(domainpath)+'print?'+request.META.get('QUERY_STRING')+'&user='+str(request.user.id)+'&'+bodyparam
		# pdf = pdfkit.from_url(url , False, options=options)
		# response = HttpResponse(pdf, content_type='application/pdf')
		# response["Content-Disposition"] = 'attachment; filename="'+request.GET['page']+'_'+date_string+'.pdf"'
		# return response

	else:
		response = Common(request)
		template = "dashboard/dashboard_content.html"
		return render(request, template, response)

def DashboardPrint(request):
	template = 'dashboard/dashboard_content.html'
	response = Common(request)
	return render(request, template, response)