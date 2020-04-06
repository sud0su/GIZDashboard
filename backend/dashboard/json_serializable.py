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
    response['chart']['xAxis_incident_type'] = incident_type_name
    response['chart']['xAxis_target_type'] = target_type_name
    ## Bar Chart
    response['chart']['bar_chart'] = {}
    response['chart']['bar_chart']['data-val'] = []
    response['chart']['bar_chart']['title'] = "Number of Casualties by Incident Type"
    for pc in category:
        incident_type_data = Undss.objects.values('Incident_Type__name').annotate(total = Coalesce(Sum(pc), 0)).order_by('-Incident_Type_id')
        total_result = [total['total'] for total in incident_type_data]
        response['chart']['bar_chart']['data-val'].append({'name':pc, 'data': total_result})

    ## Polar Chart
    chart_type = ['incident_type', 'target_type']

    for ct in chart_type:
        response['chart']['polar_'+ct] = {}
        response['chart']['polar_'+ct]['data-val'] = []
        if ct == 'incident_type':
            Title = 'Incident Type'
            OrderId = 'Incident_Type_id'
            DbRelated = 'Incident_Type__name'
        else:
            Title = 'Target Type'
            OrderId = 'Target_id'
            DbRelated = 'Target__code'
        response['chart']['polar_'+ct]['title'] = "Graph of Incident and Casualties Trend by "+ Title
        for pc in category:
            incident_type_data = Undss.objects.values(DbRelated).annotate(total = Coalesce(Sum(pc), 0)).order_by('-'+OrderId)
            total_result = [total['total'] for total in incident_type_data]
            response['chart']['polar_'+ct]['data-val'].append({'type':pc, 'data': total_result})

    # Tables
    response['tables'] = {}
    response['tables']['list_of_latest_incidents'] = Undss.objects.values('Date', 'Description_of_Incident').order_by('-Date')
    
    return response

def Common(request):
    response = {}

    if 'page' not in request.GET:
        response = dashboard(request)
    response['jsondata'] = json.dumps(response, cls=CustomEncoder)

    return response


