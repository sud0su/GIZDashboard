import json
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from .models import Undss
from reference.models import IncidentType, Province, District
from organization.models import Organization
from datetime import datetime
from giz.utils import JSONEncoderCustom

def MainData(request):
    main = {}

    main["incident_type_name"] = IncidentType.objects.values_list('name', flat=True).order_by('-id')
    main["target_type_name"] = Organization.objects.values_list('code', flat=True).order_by('-id')
    main["province_name"] = Province.objects.values_list('name', flat=True).order_by('-id')
    main["category"] = ['killed', 'Injured', 'Abducted']
    main["chart_type"] = ['incident_type', 'target_type']

    return main

def Chart(request, code, daterange):
    main = MainData(request)
    chart = {}

    undssQueryset =  Undss.objects.all()
    if code:
        getCode = code.split('=')
        if getCode[0] == 'prov':
            undssQueryset = undssQueryset.filter(Q(Province__name=getCode[1]))
        else:
            undssQueryset = undssQueryset.filter(Q(District__name=getCode[1]))

    if daterange:
        date = daterange.split(',')
        undssQueryset = undssQueryset.filter(Date__gte=date[0],Date__lte=date[1])

    ## Bar Chart
    chart['bar_chart'] = {}
    chart['bar_chart']['data_val'] = []
    chart['bar_chart']['title'] = "Number of Casualties by Incident Type"
    chart['bar_chart']['key'] = "number_of_casualties_by_incident_type"
    chart['bar_chart']['labels'] = main["incident_type_name"]
    for pc in main["category"]:
        undssQueryset = undssQueryset.values('Incident_Type__name').annotate(total = Coalesce(Sum(pc), 0)).order_by('-Incident_Type_id')
        total_result = [total['total'] for total in undssQueryset]
        chart['bar_chart']['data_val'].append({'name':pc, 'data': total_result})

    ## Spline Chart
    chart['spline'] = {}
    chart['spline']['data_val'] = []
    chart['spline']['title'] = "Historical Date of Incidents and Casualties by Incident Type"
    chart['spline']['key'] = "history_incident_and_casualties_trend_by_incident_type"
    for pc in main["category"]:
        undssQueryset = undssQueryset.values('Date').annotate(total = Coalesce(Sum(pc), 0)).order_by('-Date')
        total_result = [[total['Date'].timestamp() * 1000, total['total']] for total in undssQueryset]
        chart['spline']['data_val'].append({'name':pc, 'data': total_result})


    ## Polar Chart
    for ct in main["chart_type"]:
        chart['polar_'+ct] = {}
        chart['polar_'+ct]['data_val'] = []
        if ct == 'incident_type':
            Title = 'Incident Type'
            OrderId = 'Incident_Type_id'
            DbRelated = 'Incident_Type__name'
            chart['polar_'+ct]['labels'] = main["incident_type_name"]
            chart['polar_'+ct]['labels_all'] = main["incident_type_name"]
            chart['polar_'+ct]['key'] = "graph_of_incident_and_casualties_trend_by_incident_type"
        else:
            Title = 'Target Type'
            OrderId = 'Target_id'
            DbRelated = 'Target__code'
            chart['polar_'+ct]['labels'] = main["target_type_name"]
            chart['polar_'+ct]['labels_all'] = main["target_type_name"]
            chart['polar_'+ct]['key'] = "graph_of_incident_and_casualties_trend_by_target_type"
        chart['polar_'+ct]['title'] = "Graph of Incident and Casualties Trend by "+ Title
        for pc in main["category"]:
            type_data = undssQueryset.values(DbRelated).annotate(total = Coalesce(Sum(pc), 0)).order_by('-'+OrderId)
            total_result = [total['total'] for total in type_data]
            chart['polar_'+ct]['data_val'].append({'type':pc, 'data': total_result})

    return chart

def Table(request, code, daterange):
    table = {}
    main = MainData(request)

    undssQueryset =  Undss.objects.all()
    if code:
        getCode = code.split('=')
        if getCode[0] == 'prov':
            undssQueryset = undssQueryset.filter(Q(Province__name=getCode[1]))
        else:
            undssQueryset = undssQueryset.filter(Q(District__name=getCode[1]))

    if daterange:
        date = daterange.split(',')
        undssQueryset = undssQueryset.filter(Date__gte=date[0],Date__lte=date[1])

    # list_of_latest_incidents
    table['list_of_latest_incidents'] = undssQueryset.values('Date', 'Time_of_Incident','Description_of_Incident').order_by('-Date')
    
    # total killed, injure, abducted group by incident type
    incidentTypeData = []
    incidentTypeName = []
    for pc in main["category"]:
        incident_type_data = undssQueryset.values('Incident_Type__name').annotate(total = Coalesce(Sum(pc), 0)).order_by('-Incident_Type_id')
        total_result = [total['total'] for total in incident_type_data]
        incident_name = [total['Incident_Type__name'] for total in incident_type_data]
        incidentTypeData += [total_result]
        incidentTypeName += [incident_name]

    # incidents_and_casualties_by_incident_type
    table_incident_type_total = []
    for i in range(0, len(incidentTypeName[0])):
        table_data = {
            'incident_name': incidentTypeName[0][i],
            'killed': incidentTypeData[0][i],
            'injured': incidentTypeData[1][i],
            'abducted': incidentTypeData[2][i],
            'total': incidentTypeData[0][i] + incidentTypeData[1][i] + incidentTypeData[2][i]
        }
        table_incident_type_total.append(table_data)
    
    table['incidents_and_casualties_by_incident_type'] = table_incident_type_total

    # total killed, injure, abducted group by province, and country
    countryData = []
    for pc in main["category"]:
        country_data = undssQueryset.values(pc).annotate(total = Coalesce(Sum(pc), 0)).order_by('-'+pc)
        total_result = [int(total['total']) for total in country_data]
        countryData += [sum(total_result)]

    provinceData = []
    provinceName = []
    for pc in main["category"]:
        province_data = undssQueryset.values('Province__name').annotate(total = Coalesce(Sum(pc), 0)).order_by('-Province_id')
        total_result = [total['total'] for total in province_data]
        province_name = [total['Province__name'] for total in province_data]
        provinceData += [total_result]
        provinceName += [province_name]


    # number_of_incident_and_casualties_overview
    parentname = ['Afghanistan']
    table['number_of_incident_and_casualties_overview'] = {}
    countryDataParent = parentname + countryData + [sum(countryData)]

    table['number_of_incident_and_casualties_overview']['parentdata'] = [countryDataParent]
    table['number_of_incident_and_casualties_overview']['child'] = []
    countryDataChild = []
    for i in range(0, len(provinceName[0])):
        tot = provinceData[0][i] + provinceData[1][i] + provinceData[2][i]
        countryDataChild = [provinceName[0][i]] + [provinceData[0][i]] + [provinceData[1][i]] + [provinceData[2][i]] + [tot]
        # table['number_of_incident_and_casualties_overview']['child'].append({'name':provinceName[0][i].replace(" ", "_").lower(), 'value': countryDataChild})
        table['number_of_incident_and_casualties_overview']['child'].append({'name':provinceName[0][i], 'value': countryDataChild})
    table['number_of_incident_and_casualties_overview']['key'] = "number_of_incident_and_casualties_overview"
    table['number_of_incident_and_casualties_overview']['title'] = "Number of Incident and Casualties Overview"

    return table

def Region(request, code):
    region = {}
    provname = ""
    distname = ""
    
    getProvince = Province.objects.values()
    getDistrict = District.objects.all().values("id","name","province__name")
    
    if code:
        getCode = code.split('=')
        if getCode[0] == 'prov':
            getDistrict = getDistrict.filter(Q(province__name=getCode[1]))
        else:
            getDistrict = getDistrict.filter(Q(name=getCode[1]))

        getName = [[v["province__name"],v["name"]] for v in getDistrict]
        provname = getName[0][0]
        distname = getName[0][1]
    else:
        getDistrict = getDistrict.filter(Q(province__name=code))

    region["province"] = []
    region["province"].append({"data_val" : getProvince, "selected": provname, "type" : "Province", "urlcode": "prov"})
    region["district"] = []
    region["district"].append({"data_val" : getDistrict, "selected": distname, "type" : "District", "urlcode": "dist"})
    return region

def Total(request, code, daterange):
    total = {}
    main = MainData(request)

    undssQueryset =  Undss.objects.all()
    if code:
        getCode = code.split('=')
        if getCode[0] == 'prov':
            undssQueryset = undssQueryset.filter(Q(Province__name=getCode[1]))
        else:
            undssQueryset = undssQueryset.filter(Q(District__name=getCode[1]))

    if daterange:
        date = daterange.split(',')
        undssQueryset = undssQueryset.filter(Date__gte=date[0],Date__lte=date[1])

    countryData = []
    totalCountry = []
    for pc in main["category"]:
        country_data = undssQueryset.values(pc).annotate(total = Coalesce(Sum(pc), 0)).order_by('-'+pc)
        total_result = [int(total['total']) for total in country_data]
        totalCountry += [sum(total_result)]
        countryData.append({pc: sum(total_result)})

    provinceData = []
    provinceName = []
    for pc in main["category"]:
        province_data = undssQueryset.values('Province__name').annotate(total = Coalesce(Sum(pc), 0)).order_by('-Province_id')
        total_result = [total['total'] for total in province_data]
        province_name = [total['Province__name'] for total in province_data]
        provinceData += [total_result]
        provinceName += [province_name]

    countryDataChild = []
    for i in range(0, len(provinceName[0])):
        tot = provinceData[0][i] + provinceData[1][i] + provinceData[2][i]
        countryDataChild.append({
            'killed': provinceData[0][i],
            'injured': provinceData[1][i],
            'abducted': provinceData[2][i],
            'total' : tot
        })
    
    countryData.append({'total': sum(totalCountry)})

    if code:
        total['total_data'] = countryDataChild
    else:
        total['total_data'] = countryData  

    return total  

def DashboardResponse(request, code, daterange):
    dashboardresponse = {}
    chart = Chart(request, code, daterange)
    table = Table(request, code, daterange)
    total = Total(request, code, daterange)
    region = Region(request, code)
    dashboardresponse["chart"] = chart
    dashboardresponse["tables"] = table
    dashboardresponse["region"] = region
    dashboardresponse["total"] = total
    return dashboardresponse

def Common(request):
    response = {}
    code = None
    daterange = None

    if 'code' in request.GET:
        code = request.GET['code']

    if 'daterange' in request.GET:
        daterange = request.GET['daterange']

    if 'page' not in request.GET:
        mutable = request.GET._mutable
        request.GET._mutable = True
        request.GET['page'] = 'dashboard'
        request.GET._mutable = mutable

    if request.GET['page'] == 'dashboard':
        response = DashboardResponse(request, code, daterange)
        
    response['jsondata'] = json.dumps(response, cls=JSONEncoderCustom)

    return response


