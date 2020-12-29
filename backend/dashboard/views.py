import urllib
import json
import csv

from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, date
from django.utils.formats import dateformat
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required


from urllib.parse import urlencode
from .pychromeprint import print_from_urls

from .forms import UndssForm, MasterIncidentForm
from .json_serializable import Common, csv_response
from reference.models import Province, District, CityVillage, Area, IncidentType, IncidentSubtype, IncidentSource
from .models import Undss, MasterIncident
from giz.utils import replace_query_param
from .utils import Echo


from django.views.generic import CreateView, DetailView

from import_export.formats import base_formats
from django.urls import reverse_lazy
from giz.import_export_views import ImportView
from .resources import UndssResource, MasterIncidentResource

@method_decorator(staff_member_required, name='dispatch')
class UndssImportView(ImportView):
    model = Undss
    template_name = 'dashboard/import/reference_import_undss.html'
    formats = (base_formats.XLSX,)
    resource_class = UndssResource
    success_url = reverse_lazy('importdataundss')

    def create_dataset(self, *args, **kwargs):
        """ Insert an extra 'source_user' field into the data.
        """
        dataset = super().create_dataset(*args, **kwargs)
        length = len(dataset._data)
        dataset.append_col([self.request.user.id] * length,
                           header="source_user")
        return dataset


@method_decorator(staff_member_required, name='dispatch')
class MasterIncidentsImportView(ImportView):
    model = MasterIncident
    template_name = 'dashboard/import/reference_import_masterincident.html'
    formats = (base_formats.XLSX,)
    resource_class = MasterIncidentResource
    success_url = reverse_lazy('importmasterdataundss')

    def create_dataset(self, *args, **kwargs):
        """ Insert an extra 'source_user' field into the data.
        """
        dataset = super().create_dataset(*args, **kwargs)
        length = len(dataset._data)
        dataset.append_col([self.request.user.id] * length,
                           header="source_user")
        return dataset

@method_decorator(login_required, name='dispatch')
class UndssDetailView(DetailView):
    template_name = "dashboard/undss_detail.html"
    model = Undss
    # queryset = Undss.objects.all()

    # def get_object(self):
    #     id_ = self.kwargs.get('pk')
    #     return get_object_or_404(self.model, id=id_)

@method_decorator(login_required, name='dispatch')
class MasterIncidentDetailView(DetailView):
    template_name = "dashboard/master_detail.html"
    model = MasterIncident
    # queryset = MasterIncident.objects.all()

@method_decorator(staff_member_required, name='dispatch')
class InputUndssView(CreateView):
    template_name = "dashboard/undss_form.html"
    form_class = UndssForm
    queryset = Undss.objects.all()

    def form_valid(self, form):
        # print(self.request.Province)
        # form.instance.Province = self.request.Province
        print(form.cleaned_data)
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class InputMasterIncidentView(CreateView):
    template_name = "dashboard/masterincident_form.html"
    form_class = MasterIncidentForm
    queryset = MasterIncident.objects.all()

    def form_valid(self, form):
        # print(self.request.Province)
        # form.instance.Province = self.request.Province
        print(form.cleaned_data)
        return super().form_valid(form)


@login_required
def Dashboard(request):
    bodyparam_dict = {}
    bodyparam = urlencode(bodyparam_dict)

    headerparam_dict = {p: request.GET.get(
        p, '') for p in ['hideuserinfo', 'lang'] if p in request.GET}
    headerparam_dict.update({
        # 'onpdf': user_logo.get('onpdf'),
        # 'userlogo': user_logo.get('logo_url'),
        # 'name': request.user.first_name+' '+request.user.last_name,
        # 'cust_title': '%s %s'%('Dashboard',request.GET.get('page', '').title()),
        # 'organization': (request.user.organization or ''),
    })
    headerparam = urllib.parse.urlencode(headerparam_dict)

    currenturl = request.build_absolute_uri()
    if not request.GET.get('page'):
        return redirect(replace_query_param(currenturl, 'page', 'dashboard'))

    # if no source_type in url then redirect with added source_type=DEFAULT_SOURCE_ID
    if not request.GET.get('source_type'):
        DEFAULT_SOURCE_NAME = 'master'
        return redirect(replace_query_param(currenturl, 'source_type', DEFAULT_SOURCE_NAME))
        # source_row = IncidentSource.objects.filter(name=DEFAULT_SOURCE_NAME).first() or IncidentSource.objects.first()
        # if source_row:
        #     return redirect(replace_query_param(currenturl, 'source_type', source_row.id))

    if 'pdf' in request.GET:
        options = {
            # pychrome settings
            # match screen to print layout and resolution as close as possible
            # in order for the map to scale correctly
            # for print debugging, uncomment ruler.png in custombase.html,
            # resolution in pixel, size in inches, time in seconds
            'screen-width': 1024,  # resolution when loading the page
            'screen-height': 1024,  # resolution when loading the page
            'paperWidth': 8.27,
            'paperHeight': 11.69,
            # 'marginTop': 0.78,
            'marginTop': 0.90,
            'marginBottom': 0.45,
            'marginLeft': 0.3,
            'marginRight': 0.3,
            'scale': 0.71,  # 0.71 roughly equal to 1024 px print width on 1024 screen-width
            'after-document-loaded-delay': 1,  # in seconds
            'timeout': 60,  # in seconds
            # 'header-html': 'http://%s/static/epr_bgd/head_print/rep_header_chrome.html?%s'%(request.META.get('HTTP_HOST'),headerparam),
            'header-html': 'http://'+request.META.get('HTTP_HOST')+'/static/print/header_chrome.html',
            'headerparam': headerparam_dict,
        }
        # if re.match('^/v2', request.path):
        # 	options['viewport-size'] = '1240x800'
        domainpath = request.META.get(
            'HTTP_HOST')+request.META.get('PATH_INFO')
        url = 'http://'+str(domainpath)+'print?'+request.META.get(
            'QUERY_STRING')+'&user='+str(request.user.id)+'&'+bodyparam
        print('print url', url)
        # pdf = pdfkit.from_url(url, False, options=options)
        pdf = print_from_urls([url], print_option=options)
        date_string = dateformat.format(datetime.now(), "Y-m-d")
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="' + \
            request.GET['page']+'_'+date_string+'.pdf"'
        return response

    elif 'csv' in request.GET:
        date_string = dateformat.format(datetime.now(), "Y-m-d")
        rows = csv_response(request)
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = HttpResponse((writer.writerow(row) for row in rows), content_type='text/csv')
        filename = '_'.join([request.GET['page'], request.GET.get('source_type'), date_string])+'.csv'
        response['Content-Disposition'] = 'attachment; filename="%s"'%(filename)
        return response
    
    else:
        response = Common(request)
        template = "dashboard/dashboard_content.html"
        return render(request, template, response)


def DashboardPrint(request):
    template = 'dashboard/dashboard_content.html'
    response = Common(request)
    return render(request, template, response)


# Chained Dropdown
def get_district(request, province_id):
    province = Province.objects.get(pk=province_id)
    district = District.objects.filter(province=province)
    district_dict = []
    district_dict = [{'id': None, 'text': 'Select District', 'selected': True}]
    for dist in district:
        district_dict.append({'id': dist.id, 'text': dist.name})
    return HttpResponse(json.dumps(district_dict), 'application/json')


def get_area_city(request, province_id, district_id):
    data_area_city = []

    province = Province.objects.get(pk=province_id)
    district = District.objects.get(pk=district_id)

    # Area
    area = Area.objects.filter(province=province).filter(district=district)
    area_dict = [{'id': '', 'text': 'Select Area'}]
    for ar in area:
        area_dict.append({'id': ar.id, 'text': ar.name})

    # CityVillage
    cityvillage = CityVillage.objects.filter(
        province=province).filter(district=district)
    cityvillage_dict = [{'id': '', 'text': 'Select City Village'}]
    for cv in cityvillage:
        cityvillage_dict.append({'id': cv.id, 'text': cv.name})

    data_area_city.append({'area': area_dict, 'cityvillage': cityvillage_dict})

    return HttpResponse(json.dumps(data_area_city), 'application/json')


def get_incident_subtype(request, incidenttype_id):
    incidenttype = IncidentType.objects.get(pk=incidenttype_id)
    incidentsubtype = IncidentSubtype.objects.filter(incidenttype=incidenttype)
    incidentsubtype_dict = [{'id': '', 'text': 'Select Incident Subtype'}]
    for ist in incidentsubtype:
        incidentsubtype_dict.append({'id': ist.id, 'text': ist.name})
    return HttpResponse(json.dumps(incidentsubtype_dict), 'application/json')


def load_district(request):
    province_id = request.GET.get('province')
    data = District.objects.filter(province_id=province_id).order_by('name')
    return render(request, 'dashboard/select/select.html', {'data': data, 'type': 'District'})


def load_subtype(request):
    incidenttype_id = request.GET.get('incidenttype')
    data = IncidentSubtype.objects.filter(
        incidenttype_id=incidenttype_id).order_by('name')
    return render(request, 'dashboard/select/select.html', {'data': data, 'type': 'IncidentSubtype'})


def load_area(request):
    province_id = request.GET.get('province')
    district_id = request.GET.get('district')
    data = Area.objects.filter(
        province=province_id).filter(district=district_id)

    return render(request, 'dashboard/select/select.html', {'data': data, 'type': 'Area'})


def load_cityillage(request):
    province_id = request.GET.get('province')
    district_id = request.GET.get('district')
    data = CityVillage.objects.filter(
        province=province_id).filter(district=district_id)

    return render(request, 'dashboard/select/select.html', {'data': data, 'type': 'CityVillage'})
