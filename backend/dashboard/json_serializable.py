import json
from django.db.models import Sum, Q, Count
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

def Chart(request, code, daterange, incident_type):
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

    if incident_type:
        undssQueryset = undssQueryset.filter(Incident_Type__name__in=incident_type.split(','))


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
        undssQueryset = undssQueryset.values('Date').annotate(total = Coalesce(Sum(pc), 0)).order_by('Date')
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

def Table(request, code, daterange, incident_type):
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

    if incident_type:
        print(incident_type)
        undssQueryset = undssQueryset.filter(Incident_Type__name__in=incident_type.split(','))

    # list_of_latest_incidents
    table['list_of_latest_incidents'] = undssQueryset.values('Date', 'Time_of_Incident','Description_of_Incident').order_by('-Date')
    
    # total killed, injure, abducted group by incident type
    incidentTypeData = []
    incidentTypeName = []
    incidentCountData = []
    for pc in main["category"]:
        incident_type_data = undssQueryset.values('Incident_Type__name').annotate(count = Coalesce(Count("Incident_Type_id"), 0),total = Coalesce(Sum(pc), 0)).order_by('-Incident_Type_id')
        total_incident = [total['count'] for total in incident_type_data] 
        total_result = [total['total'] for total in incident_type_data]
        incident_name = [total['Incident_Type__name'] for total in incident_type_data]
        incidentTypeData += [total_result]
        incidentCountData += [total_incident]
        incidentTypeName += [incident_name]

    # incidents_and_casualties_by_incident_type
    table_incident_type_total = []
    for i in range(0, len(incidentTypeName[0])):
        table_data = {
            'incident_name': incidentTypeName[0][i],
            'killed': incidentTypeData[0][i],
            'injured': incidentTypeData[1][i],
            'abducted': incidentTypeData[2][i],
            # 'total': incidentTypeData[0][i] + incidentTypeData[1][i] + incidentTypeData[2][i]
            'total': incidentCountData[0][i]
        }
        table_incident_type_total.append(table_data)
    
    table['incidents_and_casualties_by_incident_type'] = table_incident_type_total

    # total killed, injure, abducted group by province, and country
    countryData = []
    countryIncident = []
    for pc in main["category"]:
        country_data = Undss.objects.all().values(pc).annotate(count = Coalesce(Count("Incident_Type_id"), 0), total = Coalesce(Sum(pc), 0)).order_by('-'+pc)
        total_incident = [total['count'] for total in country_data] 
        total_result = [int(total['total']) for total in country_data]
        countryIncident += [sum(total_incident)]
        countryData += [sum(total_result)]

    provinceData = []
    provinceName = []
    provinceIncident = []
    for pc in main["category"]:
        province_data = undssQueryset.values('Province__name').annotate(count = Coalesce(Count("Incident_Type_id"), 0), total = Coalesce(Sum(pc), 0)).order_by('-Province_id')
        total_incident = [total['count'] for total in province_data] 
        total_result = [total['total'] for total in province_data]
        province_name = [total['Province__name'] for total in province_data]
        provinceData += [total_result]
        provinceIncident += [total_incident]
        provinceName += [province_name]

    
    districtData = []
    districtName = []
    districtIncident = []
    for pc in main["category"]:
        district_data = undssQueryset.values('District__name').annotate(count = Coalesce(Count("Incident_Type_id"), 0), total = Coalesce(Sum(pc), 0)).order_by('-District_id')
        total_incident = [total['count'] for total in district_data] 
        total_result = [total['total'] for total in district_data]
        district_name = [total['District__name'] for total in district_data]
        districtData += [total_result]
        districtIncident += [total_incident]
        districtName += [district_name]

    # number_of_incident_and_casualties_overview
    parentname = ['Afghanistan']
    table['number_of_incident_and_casualties_overview'] = {}
    parentIncident = [countryIncident[0]]
    parentAbducted = [countryData[2]]
    parentInjured = [countryData[1]]
    parentKilled = [countryData[0]]

    if code:
        getCode = code.split('=')
        if getCode[0] == 'prov':
            parentname = [getCode[1]]
            parentIncident = [provinceIncident[0][0]]
            parentAbducted = [provinceData[2][0]]
            parentInjured = [provinceData[1][0]]
            parentKilled =  [provinceData[0][0]]
        elif getCode[0] == 'dist':
            parentname = [getCode[1]]
            parentIncident = [districtIncident[0][0]]
            parentAbducted = [districtData[2][0]]
            parentInjured = [districtData[1][0]]
            parentKilled =  [districtData[0][0]]
    
    countryDataParent = parentname + parentIncident + parentAbducted + parentInjured + parentKilled

    table['number_of_incident_and_casualties_overview']['parentdata'] = [countryDataParent]
    table['number_of_incident_and_casualties_overview']['child'] = []
    
    dataChild = []
    if code:
        getCode = code.split('=')
        if getCode[0] == 'prov':
            for i in range(0, len(districtName[0])):
                if districtName[0][i] == 'NULL':
                    districtName[0][i] = 'NoName'
                dataChild = [districtName[0][i]] + [districtIncident[0][i]] +[districtData[2][i]] + [districtData[1][i]] + [districtData[0][i]]
                table['number_of_incident_and_casualties_overview']['child'].append({'name':districtName[0][i], 'value': dataChild})
    else:    
        for i in range(0, len(provinceName[0])):
            if provinceName[0][i] == 'NULL':
                provinceName[0][i] = 'NoName'
            dataChild = [provinceName[0][i]] + [provinceIncident[0][i]] +[provinceData[2][i]] + [provinceData[1][i]] + [provinceData[0][i]]
            table['number_of_incident_and_casualties_overview']['child'].append({'name':provinceName[0][i], 'value': dataChild})
    
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
        if provname is not "" and getCode[0] == 'dist':
            distname = getName[0][1]
    else:
        getDistrict = getDistrict.filter(Q(province__name=code))

    region["province"] = []
    region["province"].append({"data_val" : getProvince, "selected": provname, "type" : "Province", "urlcode": "prov"})
    region["district"] = []
    region["district"].append({"data_val" : getDistrict, "selected": distname, "type" : "District", "urlcode": "dist"})
    return region

def Total(request, code, daterange, incident_type):
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

    if incident_type:
        undssQueryset = undssQueryset.filter(Incident_Type__name__in=incident_type.split(','))

    countryData = []
    totalCountry = []
    for pc in main["category"]:
        country_data = undssQueryset.values(pc).annotate(count = Coalesce(Count("Incident_Type_id"), 0), total = Coalesce(Sum(pc), 0)).order_by('-'+pc)
        total_incident = [int(total['count']) for total in country_data]
        total_result = [int(total['total']) for total in country_data]
        totalCountry += [sum(total_result)]
        countryData.append({pc: sum(total_result)})

    provinceData = []
    provinceName = []
    provinceIncident = []
    for pc in main["category"]:
        province_data = undssQueryset.values('Province__name').annotate(count = Coalesce(Count("Incident_Type_id"), 0),total = Coalesce(Sum(pc), 0)).order_by('-Province_id')
        total_incident = [total['count'] for total in province_data] 
        total_result = [total['total'] for total in province_data]
        province_name = [total['Province__name'] for total in province_data]
        provinceData += [total_result]
        provinceIncident += [total_incident]
        provinceName += [province_name]

    countryDataChild = []
    for i in range(0, len(provinceName[0])):
        # tot = provinceData[0][i] + provinceData[1][i] + provinceData[2][i]
        countryDataChild.append({
            'killed': provinceData[0][i],
            'injured': provinceData[1][i],
            'abducted': provinceData[2][i],
            'incident' : provinceIncident[0][i]
        })
    
    countryData.append({'incident': sum(total_incident)})

    if code:
        total['total_data'] = countryDataChild
    else:
        total['total_data'] = countryData  

    return total  

def DashboardResponse(request, code, daterange, incident_type):
    dashboardresponse = {}
    main = MainData(request)
    chart = Chart(request, code, daterange, incident_type)
    table = Table(request, code, daterange, incident_type)
    total = Total(request, code, daterange, incident_type)
    region = Region(request, code)
    dashboardresponse["chart"] = chart
    dashboardresponse["tables"] = table
    dashboardresponse["region"] = region
    dashboardresponse["total"] = total
    dashboardresponse["incident_type"] = {}
    dashboardresponse["incident_type"]["name"] = main["incident_type_name"]
    if not incident_type or incident_type == "0":
        dashboardresponse["incident_type"]["checked"] =  main["incident_type_name"]
    else:
        dashboardresponse["incident_type"]["checked"] = incident_type.split(',')
    
    return dashboardresponse

def Common(request):
    response = {}
    code = None
    daterange = None
    incident_type = ""

    if 'code' in request.GET:
        code = request.GET['code']

    if 'daterange' in request.GET:
        daterange = request.GET['daterange']
    
    if 'incident_type' in request.GET:
        incident_type = request.GET['incident_type']

    if 'page' not in request.GET:
        mutable = request.GET._mutable
        request.GET._mutable = True
        request.GET['page'] = 'dashboard'
        request.GET._mutable = mutable

    if request.GET['page'] == 'dashboard':
        response = DashboardResponse(request, code, daterange, incident_type)
         
    response['jsondata'] = json.dumps(response, cls=JSONEncoderCustom)

    return response


