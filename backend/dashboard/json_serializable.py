import json
from django.db.models import Sum
from django.db.models.functions import Coalesce
from .models import Undss
from reference.models import IncidentType, Province
from organization.models import Organization
from datetime import datetime
from giz.utils import JSONEncoderCustom

def dashboard(request):
    response = {}

    incident_type_name = IncidentType.objects.values_list('name', flat=True).order_by('-id')
    target_type_name = Organization.objects.values_list('code', flat=True).order_by('-id')
    province_name = Province.objects.values_list('name', flat=True).order_by('-id')
    category = ['killed', 'Injured', 'Abducted']

    # Chart
    response['chart'] = {}

    ## Bar Chart
    response['chart']['bar_chart'] = {}
    response['chart']['bar_chart']['data_val'] = []
    response['chart']['bar_chart']['title'] = "Number of Casualties by Incident Type"
    response['chart']['bar_chart']['key'] = "number_of_casualties_by_incident_type"
    response['chart']['bar_chart']['labels'] = incident_type_name
    for pc in category:
        incident_type_data = Undss.objects.values('Incident_Type__name').annotate(total = Coalesce(Sum(pc), 0)).order_by('-Incident_Type_id')
        total_result = [total['total'] for total in incident_type_data]
        response['chart']['bar_chart']['data_val'].append({'name':pc, 'data': total_result})

    ## Spline Chart
    response['chart']['spline'] = {}
    response['chart']['spline']['data_val'] = []
    response['chart']['spline']['title'] = "Historical Date of Incidents and Casualties by Incident Type"
    response['chart']['spline']['key'] = "history_incident_and_casualties_trend_by_incident_type"
    for pc in category:
        incident_type_data = Undss.objects.values('Date').annotate(total = Coalesce(Sum(pc), 0)).order_by('-Date')
        total_result = [[total['Date'].timestamp() * 1000, total['total']] for total in incident_type_data]
        response['chart']['spline']['data_val'].append({'name':pc, 'data': total_result})


    ## Polar Chart
    chart_type = ['incident_type', 'target_type']
    for ct in chart_type:
        response['chart']['polar_'+ct] = {}
        response['chart']['polar_'+ct]['data_val'] = []
        if ct == 'incident_type':
            Title = 'Incident Type'
            OrderId = 'Incident_Type_id'
            DbRelated = 'Incident_Type__name'
            response['chart']['polar_'+ct]['labels'] = incident_type_name
            response['chart']['polar_'+ct]['labels_all'] = incident_type_name
            response['chart']['polar_'+ct]['key'] = "graph_of_incident_and_casualties_trend_by_incident_type"
        else:
            Title = 'Target Type'
            OrderId = 'Target_id'
            DbRelated = 'Target__code'
            response['chart']['polar_'+ct]['labels'] = target_type_name
            response['chart']['polar_'+ct]['labels_all'] = target_type_name
            response['chart']['polar_'+ct]['key'] = "graph_of_incident_and_casualties_trend_by_target_type"
        response['chart']['polar_'+ct]['title'] = "Graph of Incident and Casualties Trend by "+ Title
        for pc in category:
            type_data = Undss.objects.values(DbRelated).annotate(total = Coalesce(Sum(pc), 0)).order_by('-'+OrderId)
            total_result = [total['total'] for total in type_data]
            response['chart']['polar_'+ct]['data_val'].append({'type':pc, 'data': total_result})

    # Tables
    response['tables'] = {}

    # list_of_latest_incidents
    response['tables']['list_of_latest_incidents'] = Undss.objects.values('Date', 'Time_of_Incident','Description_of_Incident').order_by('-Date')
    
    # total killed, injure, abducted group by incident type
    incidentTypeData = []
    for pc in category:
        incident_type_data = Undss.objects.values('Incident_Type__name').annotate(total = Coalesce(Sum(pc), 0)).order_by('-Incident_Type_id')
        total_result = [total['total'] for total in incident_type_data]
        incidentTypeData += [total_result]

    # incidents_and_casualties_by_incident_type
    table_incident_type_total = []
    for i in range(0, len(incident_type_name)):
        table_data = {
            'incident_name': incident_type_name[i],
            'killed': incidentTypeData[0][i],
            'injured': incidentTypeData[1][i],
            'abducted': incidentTypeData[2][i],
            'total': incidentTypeData[0][i] + incidentTypeData[1][i] + incidentTypeData[2][i]
        }
        table_incident_type_total.append(table_data)
    
    response['tables']['incidents_and_casualties_by_incident_type'] = table_incident_type_total

    # total killed, injure, abducted group by province, and country
    countryData = []
    for pc in category:
        country_data = Undss.objects.values(pc).annotate(total = Coalesce(Sum(pc), 0)).order_by('-'+pc)
        total_result = [int(total['total']) for total in country_data]
        countryData += [sum(total_result)]

    provinceData = []
    for pc in category:
        province_data = Undss.objects.values('Province__name').annotate(total = Coalesce(Sum(pc), 0)).order_by('-Province_id')
        total_result = [total['total'] for total in province_data]
        provinceData += [total_result]


    # number_of_incident_and_casualties_overview
    parentname = ['Afghanistan']
    response['tables']['number_of_incident_and_casualties_overview'] = {}
    countryDataParent = parentname + countryData + [sum(countryData)]

    response['tables']['number_of_incident_and_casualties_overview']['parentdata'] = [countryDataParent]
    response['tables']['number_of_incident_and_casualties_overview']['child'] = []
    countryDataChild = []
    for i in range(0, len(province_name)):
        tot = provinceData[0][i] + provinceData[1][i] + provinceData[2][i]
        countryDataChild = [province_name[i]] + [provinceData[0][i]] + [provinceData[1][i]] + [provinceData[2][i]] + [tot]
        response['tables']['number_of_incident_and_casualties_overview']['child'].append({'name':province_name[i].replace(" ", "_").lower(), 'value': countryDataChild})
    response['tables']['number_of_incident_and_casualties_overview']['key'] = "number_of_incident_and_casualties_overview"
    response['tables']['number_of_incident_and_casualties_overview']['title'] = "Number of Incident and Casualties Overview"

    return response

def Common(request):
    response = {}

    if 'page' not in request.GET:
        response = dashboard(request)
    response['jsondata'] = json.dumps(response, cls=JSONEncoderCustom)

    return response


