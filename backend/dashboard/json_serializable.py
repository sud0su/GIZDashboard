import json
import datetime
from django.db.models import Sum, Q, Count, F, Case, CharField, Value, When
from django.db.models.functions import Coalesce, Trim, Lower
from .models import Undss
from reference.models import IncidentType, IncidentSubtype, Province, District, IncidentSource
from organization.models import Organization
from giz.utils import JSONEncoderCustom
from .utils import NoneStr2Obj

source_type_dbfield = {'prmo':'PRMO', 'undss':'UNDSS', 'inso':'INSO'}

def MainData(request, filters={}):
    main = {}

    enddate = datetime.date.today()
    startdate = datetime.date.today() - datetime.timedelta(days=365)
    main["daterange"] = startdate.strftime("%Y-%m-%d")+','+enddate.strftime("%Y-%m-%d")

    main["incident_type_name"] = IncidentType.objects.values_list('name', flat=True).order_by('-id')
    main["target_type_name"] = Organization.objects.values_list('code', flat=True).order_by('-id')
    main["province_name"] = Province.objects.values_list('name', flat=True).order_by('-id')
    main["category"] = ['killed', 'Injured', 'Abducted']
    main["chart_type"] = ['incident_type', 'target_type']
    main['filters'] = {
        'source_type': {
            # 'prmo': {
            #     'options': Undss.objects.annotate(PRMO2=Lower(Trim('PRMO'))).values_list('PRMO2', flat=True).distinct().order_by('PRMO2'),
            # },
            # 'undss': {
            #     'options': Undss.objects.annotate(UNDSS2=Lower(Trim('UNDSS'))).values_list('UNDSS2', flat=True).distinct().order_by('UNDSS2'),
            # },
            # 'inso': {
            #     'options': Undss.objects.annotate(INSO2=Lower(Trim('INSO'))).values_list('INSO2', flat=True).distinct().order_by('INSO2'),
            # },
            'options': IncidentSource.objects.values('id','name').order_by('id'),
        },
        'target_type': {
            'name': Organization.objects.values('id','code','name').order_by('-id'),
        },
        'initiator': {
            'options': Organization.objects.values('id','code','name').order_by('-id'),
        },
        'police_district': {
            'options': Undss.objects.values_list('Police_District', flat=True).distinct().order_by('Police_District'),
        },
        'hpa': {
            'options': yesno_annotate(Undss.objects, 'HPA').values_list('yesno', flat=True).distinct().order_by('-yesno'),
        },
        'incident_type': {
            'options': IncidentType.objects.values('id','name').order_by('-id'),
        },
        'incident_subtype': {
            'options': IncidentSubtype.objects.values('incidenttype','incidenttype__name','id','name').order_by('-incidenttype','-id'),
        },
    }

    main["filters"]['police_district']['selected'] = filters['police_district']
    main["filters"]['hpa']['selected'] = filters['hpa']
    main["filters"]['incident_type']['checked'] = filters['incident_type'] or [i['id'] for i in main["filters"]['incident_type']['options']]
    main["filters"]['incident_subtype']['checked'] = filters['incident_subtype'] or [i['id'] for i in main["filters"]['incident_subtype']['options']]
    main['filters']["source_type"]['selected'] = json.loads(filters.get('source_type') or 'null')
    main['filters']["initiator"]['selected'] = json.loads(filters.get('initiator') or 'null')
    main['filters']["target_type"]["checked"] = filters['target_type'] or [i['id'] for i in main['filters']["target_type"]["name"]]

    main['is_subtype'] = bool(filters.get('incident_subtype'))
    main['type_key'] = 'incident_subtype' if main['is_subtype'] else "incident_type"
    main['filters']["target_type"]["labels"] = [i['code'] for i in main['filters']['target_type']['name'] if i['id'] in main['filters']['target_type']['checked']]
    
    filter_incident = main['filters'][main['type_key']]
    filter_incident["labels"] = [i['name'] for i in filter_incident['options'] if i['id'] in filter_incident['checked']]

    return main

def Chart(request, code, daterange, incident_type, filters={}, main={}):
    # main = MainData(request)
    chart = {}
    undssQueryset = Undss.objects.all()
    
    if code:
        getCode = code.split('=')
        if getCode[0] == 'prov':
            undssQueryset = undssQueryset.filter(Q(Province__name=getCode[1]))
        else:
            undssQueryset = undssQueryset.filter(Q(District__name=getCode[1]))

    if daterange:
        date = daterange.split(',')
        undssQueryset = undssQueryset.filter(Date__gte=date[0],Date__lte=date[1])
    else:
        date = main["daterange"].split(',')
        undssQueryset = undssQueryset.filter(Date__gte=date[0],Date__lte=date[1])
        

    if incident_type:
        undssQueryset = undssQueryset.filter(Incident_Type__in=incident_type.split(','))

    undssQueryset = ApplyFilters(undssQueryset, filters)

    filter_incident = main['filters'][main['type_key']]

    ## Bar Chart
    chart['bar_chart_incident'] = {}
    chart['bar_chart_incident']['data_val'] = []
    chart['bar_chart_incident']['title'] = "Number of Casualties by Incident Subtype" if main['is_subtype'] else "Number of Casualties by Incident Type"
    chart['bar_chart_incident']['key'] = "number_of_casualties_by_incident_type"
    # chart['bar_chart_incident']['labels'] = main["incident_type_name"]
    chart['bar_chart_incident']['labels'] = filter_incident["labels"]
    values_field = 'Incident_Subtype' if main['is_subtype'] else 'Incident_Type'
    order_field = '-Incident_Subtype_id' if main['is_subtype'] else '-Incident_Type_id'
    for pc in main["category"]:
        qs_bar_chart_incident = undssQueryset.values_list(values_field).annotate(total = Coalesce(Sum(pc), 0))
        qs_bar_chart_incident_dict = dict(qs_bar_chart_incident)
        total_result = [qs_bar_chart_incident_dict.get(id,0) for id in filter_incident['checked']]
        chart['bar_chart_incident']['data_val'].append({'name':pc, 'data': total_result})

    chart['bar_chart_target'] = {}
    chart['bar_chart_target']['data_val'] = []
    chart['bar_chart_target']['title'] = "Number of Casualties by Target Type"
    chart['bar_chart_target']['key'] = "number_of_casualties_by_target_type"
    # chart['bar_chart_target']['labels'] = main["target_type_name"]
    chart['bar_chart_target']['labels'] = main['filters']["target_type"]["labels"]
    for pc in main["category"]:
        qs_bar_chart_target = undssQueryset.values('Target__code').annotate(total = Coalesce(Sum(pc), 0)).order_by('-Target_id')
        total_result = [total['total'] for total in qs_bar_chart_target]
        chart['bar_chart_target']['data_val'].append({'name':pc, 'data': total_result})

    ## Spline Chart
    chart['spline'] = {}
    chart['spline']['data_val'] = []
    chart['spline']['title'] = "Historical Date of Incidents and Casualties by Incident Type"
    chart['spline']['key'] = "history_incident_and_casualties_trend_by_incident_type"
    for pc in main["category"]:
        # undssQueryset = undssQueryset.values('Date').annotate(total = Coalesce(Sum(pc), 0)).order_by('Date')
        # total_result = [[total['Date'].timestamp() * 1000, total['total']] for total in undssQueryset]
        qs_spline = undssQueryset.values('Date','Time_of_Incident').annotate(total = Coalesce(Sum(pc), 0)).order_by('Date')
        # total = [total['total'] for total in undssQueryset]
        # splineDateTime = [(datetime.datetime.combine(total['Date'].date(), total['Time_of_Incident'])).timestamp() * 1000 for total in undssQueryset]
        
        # total_result = []
        # for i in range(len(total)):
        #     combine = [splineDateTime[i]] + [total[i]]
        #     total_result.append(combine)
        
        total_result = [
            [(datetime.datetime.combine(total['Date'].date(), total['Time_of_Incident'])).timestamp() * 1000, total['total']]
            for total in qs_spline
        ]

        chart['spline']['data_val'].append({'name':pc, 'data': total_result})


    ## Polar Chart
    for ct in main["chart_type"]:
        chart_ct = chart['polar_'+ct] = {}
        chart_ct['data_val'] = []
        filter_key = ct
        if ct == 'incident_type':
            filter_key = main['type_key']
            chart_ct['labels'] = filter_incident["labels"]
            chart_ct['labels_all'] = chart_ct['labels']
            if main['is_subtype']:
                Title = 'Incident Subtype'
                OrderId = 'Incident_Subtype_id'
                DbRelated = 'Incident_Subtype__name'
                # chart_ct['labels'] = [i['name'] for i in main['filters']["incident_type"]['incident_subtype']['options']]
                chart_ct['key'] = "graph_of_incident_and_casualties_trend_by_incident_type"
            else:
                Title = 'Incident Type'
                OrderId = 'Incident_Type_id'
                DbRelated = 'Incident_Type__name'
                # chart_ct['labels'] = main["incident_type_name"]
                chart_ct['key'] = "graph_of_incident_and_casualties_trend_by_incident_type"
        else:
            Title = 'Target Type'
            OrderId = 'Target_id'
            DbRelated = 'Target__code'
            # chart_ct['labels'] = main["target_type_name"]
            chart_ct['labels'] = main['filters']["target_type"]["labels"]
            chart_ct['labels_all'] = chart_ct['labels']
            chart_ct['key'] = "graph_of_incident_and_casualties_trend_by_target_type"
        chart_ct['title'] = "Graph of Incident and Casualties Trend by "+ Title
        for pc in main["category"]:
            type_data = undssQueryset.values_list(OrderId).annotate(total = Coalesce(Sum(pc), 0))
            type_data_dict = dict(type_data)
            # total_result = [total['total'] for total in type_data]
            total_result = [type_data_dict.get(id,0) for id in main['filters'][filter_key]['checked']]
            chart_ct['data_val'].append({'type':pc, 'data': total_result})

    return chart

def Table(request, code, daterange, incident_type, filters={}, main={}):
    table = {}
    # main = MainData(request)

    undssQueryset = Undss.objects.all()
    
    if code:
        getCode = code.split('=')
        if getCode[0] == 'prov':
            undssQueryset = undssQueryset.filter(Q(Province__name=getCode[1]))
        else:
            undssQueryset = undssQueryset.filter(Q(District__name=getCode[1]))

    if daterange:
        date = daterange.split(',')
        undssQueryset = undssQueryset.filter(Date__gte=date[0],Date__lte=date[1])
    else:
        date = main["daterange"].split(',')
        undssQueryset = undssQueryset.filter(Date__gte=date[0],Date__lte=date[1])

    if incident_type:
        undssQueryset = undssQueryset.filter(Incident_Type__in=incident_type.split(','))

    undssQueryset= ApplyFilters(undssQueryset, filters)

    # list_of_latest_incidents
    table['list_of_latest_incidents'] = undssQueryset.values('id','Date', 'Time_of_Incident','Description_of_Incident').order_by('-Date')
    

    # total killed, injure, abducted group by incident type
    incidentTypeData = []
    incidentSubtypeName = []
    incidentTypeName = []
    incidentCountData = []
    values_field = 'Incident_Subtype' if main['is_subtype'] else 'Incident_Type'
    order_field = '-Incident_Subtype_id' if main['is_subtype'] else '-Incident_Type_id'
    filter_incident = main['filters'][main['type_key']]
    for pc in main["category"]:
        incident_type_data = undssQueryset.\
            values(values_field).\
            annotate(count = Coalesce(Count("id"), 0),total = Coalesce(Sum(pc), 0)).\
            order_by(order_field)
        incident_type_data_dict = {
            i[values_field]: {
                'count': i['count'],
                'total':i['total']
            } for i in incident_type_data}
        # total_incident = [total['count'] for total in incident_type_data] 
        total_incident = [incident_type_data_dict.get(i,{}).get('count',0) for i in filter_incident['checked']] 
        # total_result = [total['total'] for total in incident_type_data]
        total_result = [incident_type_data_dict.get(i,{}).get('total',0) for i in filter_incident['checked']] 
        # incident_name = [total[values_field] for total in incident_type_data]
        incident_name = filter_incident['labels']
        # incident_subtype_name = [total['Incident_Subtype__name'] for total in incident_type_data]
        incidentTypeData += [total_result]
        incidentCountData += [total_incident]
        incidentTypeName += [incident_name]
        # incidentSubtypeName += [incident_subtype_name]

    # incidents_and_casualties_by_incident_type
    table_incident_type_total = []
    for i in range(0, len(filter_incident['labels'])):
        table_data = {
            # 'incident_name': incidentTypeName[0][i],
            'incident_name': filter_incident['labels'][i],
            # 'incident_subtype_name': incidentSubtypeName[0][i],
            'killed': incidentTypeData[0][i],
            'injured': incidentTypeData[1][i],
            'abducted': incidentTypeData[2][i],
            # 'total': incidentTypeData[0][i] + incidentTypeData[1][i] + incidentTypeData[2][i]
            'total': incidentCountData[0][i]
        }
        table_incident_type_total.append(table_data)
    
    table['incidents_and_casualties_by_incident_type'] = {
        'title': 'Incidents and Casualties by Incident %s' % 'Subtype' if main['is_subtype'] else 'Type',
        'values': table_incident_type_total,
    }

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
        provinceData += [[0] if not total_result else total_result]
        provinceIncident += [[0] if not total_incident else total_incident]
        provinceName += [province_name]

    
    districtData = []
    districtName = []
    districtIncident = []
    for pc in main["category"]:
        district_data = undssQueryset.values('District__name').annotate(count = Coalesce(Count("Incident_Type_id"), 0), total = Coalesce(Sum(pc), 0)).order_by('-District_id')
        total_incident = [total['count'] for total in district_data] 
        total_result = [total['total'] for total in district_data]
        district_name = [total['District__name'] for total in district_data]
        districtData += [[0] if not total_result else total_result]
        districtIncident += [[0] if not total_incident else total_incident]
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

def Total(request, code, daterange, incident_type, filters={}, main={}):
    total = {}
    # main = MainData(request)

    undssQueryset = Undss.objects.all()
    
    if code:
        getCode = code.split('=')
        if getCode[0] == 'prov':
            undssQueryset = undssQueryset.filter(Q(Province__name=getCode[1]))
        else:
            undssQueryset = undssQueryset.filter(Q(District__name=getCode[1]))

    if daterange:
        date = daterange.split(',')
        undssQueryset = undssQueryset.filter(Date__gte=date[0],Date__lte=date[1])
    else:
        date = main["daterange"].split(',')
        undssQueryset = undssQueryset.filter(Date__gte=date[0],Date__lte=date[1])

    if incident_type:
        undssQueryset = undssQueryset.filter(Incident_Type__in=incident_type.split(','))

    undssQueryset= ApplyFilters(undssQueryset, filters)

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
        provinceData += [[0] if not total_result else total_result]
        provinceIncident += [[0] if not total_incident else total_incident]
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

def DashboardResponse(request, code, daterange, incident_type, filters={}):
    dashboardresponse = {}
    main = MainData(request, filters=filters)
    chart = Chart(request, code, daterange, incident_type, filters=filters, main=main)
    table = Table(request, code, daterange, incident_type, filters=filters, main=main)
    total = Total(request, code, daterange, incident_type, filters=filters, main=main)
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

    dashboardresponse["filters"] = main["filters"]

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

    filters = {
        # 'source_type': {dbfield: NoneStr2Obj(request.GET[filter]) for filter, dbfield in source_type_dbfield.items() if filter in request.GET},
        # # 'source_type': {filter: json.loads(request.GET[filter]) for filter in source_type_dbfield.keys() if filter in request.GET},
        'source_type': request.GET.get('source_type'),
        # 'target_type': request.GET.get('target_type'),
        'target_type': [int(i) for i in list(filter(None, (request.GET.get('target_type','').split(','))))],
        'police_district': request.GET.get('police_district'),
        'hpa': str(request.GET.get('hpa') or '').strip().lower(),
        'initiator': request.GET.get('initiator'),
        # 'incident_type': request.GET.get('incident_type'),
        'incident_type': [int(i) for i in list(filter(None, (request.GET.get('incident_type','').split(','))))],
        'incident_subtype': [int(i) for i in list(filter(None, (request.GET.get('incident_subtype','').split(','))))],
    }

    if request.GET['page'] == 'dashboard':
        response = DashboardResponse(request, code, daterange, incident_type, filters=filters)
         
    response['jsondata'] = json.dumps(response, cls=JSONEncoderCustom)

    return response

def ApplyFilters(queryset, filters):

    if filters.get('source_type'):
        queryset = queryset.filter(Incident_Source=filters.get('source_type'))

    if filters.get('incident_subtype'):
        queryset = queryset.filter(Incident_Subtype__in=filters.get('incident_subtype'))

    if filters.get('initiator'):
        queryset = queryset.filter(Initiator=filters.get('initiator'))

    if filters.get('target_type'):
        queryset = queryset.filter(Target__in=filters.get('target_type'))

    if filters.get('police_district'):
        queryset = queryset.filter(Police_District=filters.get('police_district'))

    if filters.get('hpa') in ['yes', 'no']:
        queryset = yesno_annotate(queryset, 'HPA').filter(**{'yesno': filters.get('hpa')})

    # for key, value in filters.get('source_type', {}).items():
    #     # trimmed_or_none = value if value is None else value.strip().lower()
    #     # queryset = queryset.annotate(trimmed=Lower(Trim(key))).filter(**{'trimmed': trimmed_or_none})
    #     queryset = queryset.annotate(**{key+'_trim':Lower(Trim(source_type_dbfield[key]))}).filter(**{key+'_trim':'yes'})

    return queryset

def yesno_annotate(queryset, field):
    return queryset.annotate(lowered=Lower(Trim(field))).annotate(
                yesno=Case(
                    When(lowered='yes', then=Value('yes')),
                    default=Value('no'),
                    output_field=CharField(),
                ),
            )
