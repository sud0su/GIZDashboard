import json
from django.db.models import Sum
from django.db.models.functions import Coalesce
from .models import Undss
from reference.models import IncidentType
from organization.models import Organization
from datetime import datetime


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if obj.__class__.__name__ in ["GeoValuesQuerySet","ValuesQuerySet","QuerySet"]:
            return list(obj)
        elif obj.__class__.__name__ == "date":
            return obj.strftime("%Y-%m-%d")
        elif obj.__class__.__name__ == "datetime":
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif obj.__class__.__name__ == "Decimal":
            return float(obj)
        else:
            print('not converted to json:', obj.__class__.__name__)
            return 'not converted to json: %s' % (obj.__class__.__name__)

def dashboard(request):
    response = {}

    incident_type_name = IncidentType.objects.values_list('name', flat=True).order_by('-id')
    target_type_name = Organization.objects.values_list('code', flat=True).order_by('-id')
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
            response['chart']['polar_'+ct]['key'] = "graph_of_incident_and_casualties_trend_by_incident_type"
        else:
            Title = 'Target Type'
            OrderId = 'Target_id'
            DbRelated = 'Target__code'
            response['chart']['polar_'+ct]['labels'] = target_type_name
            response['chart']['polar_'+ct]['key'] = "graph_of_incident_and_casualties_trend_by_target_type"
        response['chart']['polar_'+ct]['title'] = "Graph of Incident and Casualties Trend by "+ Title
        for pc in category:
            type_data = Undss.objects.values(DbRelated).annotate(total = Coalesce(Sum(pc), 0)).order_by('-'+OrderId)
            total_result = [total['total'] for total in type_data]
            response['chart']['polar_'+ct]['data_val'].append({'type':pc, 'data': total_result})

    # Tables
    response['tables'] = {}
    response['tables']['list_of_latest_incidents'] = Undss.objects.values('Date', 'Description_of_Incident').order_by('-Date')
    
    incidentTypeData = []
    for pc in category:
        incident_type_data = Undss.objects.values('Incident_Type__name').annotate(total = Coalesce(Sum(pc), 0)).order_by('-Incident_Type_id')
        total_result = [total['total'] for total in incident_type_data]
        incidentTypeData += [total_result]

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
    return response

def Common(request):
    response = {}

    if 'page' not in request.GET:
        response = dashboard(request)
    response['jsondata'] = json.dumps(response, cls=CustomEncoder)

    return response


