import json
import datetime

from django.db.models import Sum, Q, Count, F, Case, CharField, Value, When
from django.db.models.functions import Coalesce, Trim, Lower, TruncHour, TruncDate
from itertools import chain

from .models import Undss, MasterIncident, Bool2YesNo
from .enumerations import MASTER_NAME, source_type_dbfield, source_type_rename, source_types, yesno2truefalse
from reference.models import IncidentType, IncidentSubtype, Province, District, IncidentSource, PrmoOffice
from organization.models import Organization
from giz.utils import JSONEncoderCustom
from .utils import NoneStr2Obj


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

    main["sum_by_casualty_type"] = {
        'killed': \
            Coalesce(Sum(F('Kill_Natl')), 0)+\
            Coalesce(Sum(F('Kill_Intl')), 0)+\
            Coalesce(Sum(F('Kill_ANSF')), 0)+\
            Coalesce(Sum(F('Kill_IM')), 0)+\
            Coalesce(Sum(F('Kill_ALP_PGM')), 0)+\
            Coalesce(Sum(F('Kill_AOG')), 0)+\
            Coalesce(Sum(F('Kill_ISKP')), 0),
        'injured': \
            Coalesce(Sum(F('Inj_Natl')), 0)+\
            Coalesce(Sum(F('Inj_Intl')), 0)+\
            Coalesce(Sum(F('Inj_ANSF')), 0)+\
            Coalesce(Sum(F('Inj_IM')), 0)+\
            Coalesce(Sum(F('Inj_ALP_PGM')), 0)+\
            Coalesce(Sum(F('Inj_AOG')), 0)+\
            Coalesce(Sum(F('Inj_ISKP')), 0),
        'abducted': \
            Coalesce(Sum(F('Abd_Natl')), 0)+\
            Coalesce(Sum(F('Abd_Intl')), 0)+\
            Coalesce(Sum(F('Abd_ANSF')), 0)+\
            Coalesce(Sum(F('Abd_IM')), 0)+\
            Coalesce(Sum(F('Abd_ALP_PGM')), 0),
    }

    main['master_id'] = IncidentSource.objects.before_min_id()
    main['filters'] = {
        'source_type': {
            # 'options': source_types,
            'options': [{'id':main['master_id'], 'name': MASTER_NAME}] + list(IncidentSource.objects.values('id','name').order_by('id')),
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
        'prmo_loc': {
            # 'options': Undss.objects.annotate(name=Lower(Trim('Incident_Source_Office'))).\
            #     values('name').distinct().order_by('name'),
            'options': PrmoOffice.objects.values('id','name').order_by('id'),
        },
    }

    main["filters"]['police_district']['selected'] = filters['police_district']
    main["filters"]['hpa']['selected'] = filters['hpa']
    main["filters"]['incident_type']['checked'] = filters['incident_type'] or [i['id'] for i in main["filters"]['incident_type']['options']]
    main["filters"]['incident_subtype']['checked'] = filters['incident_subtype'] or [i['id'] for i in main["filters"]['incident_subtype']['options']]
    # main['filters']["source_type"]['selected'] = json.loads(filters.get('source_type') or 'null')
    main['filters']["source_type"]['selected'] = json.loads(filters.get('source_type') or 'null')
    main['filters']["prmo_loc"]['selected'] = json.loads(filters.get('prmo_loc') or 'null')
    main['filters']["initiator"]['selected'] = json.loads(filters.get('initiator') or 'null')
    main['filters']["target_type"]["checked"] = filters['target_type'] or [i['id'] for i in main['filters']["target_type"]["name"]]

    main['is_subtype'] = bool(filters.get('incident_subtype'))
    main['type_key'] = 'incident_subtype' if main['is_subtype'] else "incident_type"
    main['filters']["target_type"]["labels"] = [i['code'] for i in main['filters']['target_type']['name'] if i['id'] in main['filters']['target_type']['checked']]
    main['filters']["source_type"]['prmo_id'] = IncidentSource.objects.get_prmo_id()
    main['is_prmo'] = main['filters']["source_type"]['prmo_id'] and main['filters']["source_type"]['selected'] == main['filters']["source_type"]['prmo_id']

    filter_incident = main['filters'][main['type_key']]
    filter_incident_options_dict = {i['id']:i['name'] for i in filter_incident['options']}
    filter_incident["labels"] = [filter_incident_options_dict.get(i) for i in filter_incident['checked']]

    main['is_master'] = main['filters']["source_type"]['selected'] == main['master_id']
    main["model"] = MasterIncident if main['is_master'] else Undss
    main["qs"] = main["model"].objects.all()
    main["qs_filtered"] = ApplyFilters(main["qs"], filters, main=main)

    main['filters']['impact'] = {
        'options': main["qs"].annotate(IGCHO_yesno=Bool2YesNo('IGCHO')).values_list('IGCHO_yesno', flat=True).distinct().order_by('-IGCHO_yesno'),
        'selected': filters['impact'],
    }

    return main

def Chart(request, filters={}, main={}):
    chart = {}

    # undssQueryset = Undss.objects.all()
    # undssQueryset = ApplyFilters(undssQueryset, filters, main=main)
    undssQueryset = main["qs_filtered"]

    filter_incident = main['filters'][main['type_key']]

    ## Bar Chart incident type
    chart['bar_chart_incident'] = {}
    chart['bar_chart_incident']['data_val'] = []
    chart['bar_chart_incident']['title'] = "Number of Casualties by Incident Subtype" if main['is_subtype'] else "Number of Casualties by Incident Type"
    chart['bar_chart_incident']['key'] = "number_of_casualties_by_incident_type"
    chart['bar_chart_incident']['labels'] = filter_incident["labels"]
    id_field = 'Incident_Subtype' if main['is_subtype'] else 'Incident_Type'
    for pc in main["category"]:
        # qs_bar_chart_incident = undssQueryset.values_list(id_field).annotate(total = Coalesce(Sum(pc), 0))
        qs_bar_chart_incident = undssQueryset.values_list(id_field).annotate(total = main['sum_by_casualty_type'][pc.lower()])
        qs_bar_chart_incident_dict = dict(qs_bar_chart_incident)
        total_result = [qs_bar_chart_incident_dict.get(id,0) for id in filter_incident['checked']]
        chart['bar_chart_incident']['data_val'].append({'name':pc, 'data': total_result})

    ## Bar Chart target type
    chart['bar_chart_target'] = {}
    chart['bar_chart_target']['data_val'] = []
    chart['bar_chart_target']['title'] = "Number of Casualties by Target Type"
    chart['bar_chart_target']['key'] = "number_of_casualties_by_target_type"
    chart['bar_chart_target']['labels'] = main['filters']["target_type"]["labels"]
    for pc in main["category"]:
        # qs_bar_chart_target = undssQueryset.values_list('Target').annotate(total = Coalesce(Sum(pc), 0))
        qs_bar_chart_target = undssQueryset.values_list('Target').annotate(total = main['sum_by_casualty_type'][pc.lower()])
        qs_bar_chart_target_dict = dict(qs_bar_chart_target)
        total_result = [qs_bar_chart_target_dict.get(id,0) for id in main['filters']["target_type"]['checked']]
        chart['bar_chart_target']['data_val'].append({'name':pc, 'data': total_result})

    # Donut Chart by casualtiy type and subtype
    chart['donut_chart_casualty_subtype'] = [
        {
            'key': 'number_of_national_casualties',
            'title': "National Casualties",
            'fields': ['Kill_Natl','Inj_Natl','Abd_Natl'],
        },
        {
            'key': 'number_of_international_casualties',
            'title': "International Casualties",
            'fields': ['Kill_Intl','Inj_Intl','Abd_Intl'],
        },
        {
            'key': 'number_of_ansf_casualties',
            'title': "ANSF Casualties",
            'fields': ['Kill_ANSF','Inj_ANSF','Abd_ANSF'],
        },
        {
            'key': 'number_of_alp-pgm_casualties',
            'title': "ALP-PGM Casualties",
            'fields': ['Kill_ALP_PGM','Inj_ALP_PGM','Abd_ALP_PGM'],
        },
        {
            'key': 'number_of_aog_casualties',
            'title': "AOG Casualties",
            'fields': ['Kill_AOG','Inj_AOG'],
        },
        {
            'key': 'number_of_iskp_casualties',
            'title': "ISKP Casualties",
            'fields': ['Kill_ISKP','Inj_ISKP'],
        },
        {
            'key': 'number_of_im_casualties',
            'title': "IM Casualties",
            'fields': ['Kill_IM','Inj_IM','Abd_IM'],
        },
    ]
    all_fields = list(chain.from_iterable([i['fields'] for i in chart['donut_chart_casualty_subtype']]))
    sum_queries = {i:Coalesce(Sum(i), 0) for i in all_fields}
    bar_chart_casualty_subtype_qs = undssQueryset.aggregate(**sum_queries)
    prefix2label = {'Kill':'Killed', 'Inj':'Injured', 'Abd':'Abducted'}
    field2label = lambda x: prefix2label.get(x.split('_')[0])
    for c in chart['donut_chart_casualty_subtype']:
        c['values'] = [[field2label(field), bar_chart_casualty_subtype_qs[field]] for field in c['fields']]

    ## Bar Chart by casualtiy type and subtype
    chart['bar_chart_casualty_subtype'] = {
        'data_val': [],
        'title': "Number of Casualties",
        'key': "number_of_casualties_by_type_and_subtype",
        'labels': [i['title'].split()[0] for i in chart['donut_chart_casualty_subtype']],
    }
    for prefix in prefix2label:
        data = []
        label = field2label(prefix)
        for item in chart['donut_chart_casualty_subtype']:
            field = next((f for f in item['fields'] if f.split('_')[0] == prefix), None)
            data += [bar_chart_casualty_subtype_qs.get(field, 0)] 
        chart['bar_chart_casualty_subtype']['data_val'].append({'name':label, 'data': data})

    # data = {prefix:[] for prefix in prefix2label}
    # for item in chart['donut_chart_casualty_subtype']:
    #     for prefix in prefix2label:
    #         field = next((f for f in item['fields'] if f.split('_')[0] == prefix), None)
    #         data[prefix] += [bar_chart_casualty_subtype_qs.get(field, 0)] 
    # chart['bar_chart_casualty_subtype']['data_val'] = [{'name':prefix2label[prefix], 'data': data[prefix]} for prefix in data]

    # for pc in main["category"]:
    #     # qs_bar_chart_target = undssQueryset.values_list('Target').annotate(total = Coalesce(Sum(pc), 0))
    #     qs_bar_chart_target = undssQueryset.values_list('Target').annotate(total = main['sum_by_casualty_type'][pc.lower()])
    #     qs_bar_chart_target_dict = dict(qs_bar_chart_target)
    #     total_result = [qs_bar_chart_target_dict.get(id,0) for id in main['filters']["target_type"]['checked']]
    #     chart['bar_chart_casualty_subtype']['data_val'].append({'name':pc, 'data': total_result})

    ## Spline Chart
    chart['spline'] = {}
    chart['spline']['data_val'] = []
    chart['spline']['title'] = "Historical Date of Incidents and Casualties by Incident Type"
    chart['spline']['key'] = "history_incident_and_casualties_trend_by_incident_type"
    # for pc in main["category"]:
    #     # qs_spline = undssQueryset.values('Date','Time_of_Incident').annotate(total = Coalesce(Sum(pc), 0)).order_by('Date')
    #     qs_spline = undssQueryset.values('Date','Time_of_Incident').annotate(total = main['sum_by_casualty_type'][pc.lower()]).order_by('Date','Time_of_Incident')
    #     # qs_spline = undssQueryset.values('Date').annotate(total = main['sum_by_casualty_type'][pc.lower()]).order_by('Date')
    #     total_result = [
    #         [(datetime.datetime.combine(total['Date'].date(), total['Time_of_Incident'])).timestamp() * 1000, total['total']]
    #         # [total['Date'].timestamp() * 1000, total['total']]
    #         for total in qs_spline
    #     ]

    #     chart['spline']['data_val'].append({'name':pc, 'data': total_result})
    # qs_spline = undssQueryset.values('Date').annotate(hour=TruncHour('Time_of_Incident'),**main['sum_by_casualty_type']).order_by('Date','hour')
    qs_spline = undssQueryset.values('Date','Time_of_Incident').annotate(**main['sum_by_casualty_type']).order_by('Date','Time_of_Incident')
    # qs_spline = undssQueryset.values('Date').annotate(Date_date=TruncDate('Date'),**main['sum_by_casualty_type']).order_by('Date_date')
    # timestamps = [datetime.datetime.combine(i['Date'].date(), i['hour']).timestamp() * 1000 for i in qs_spline]
    timestamps = [datetime.datetime.combine(i['Date'], i['Time_of_Incident'] or datetime.time()).replace(tzinfo=datetime.timezone.utc).timestamp() * 1000 for i in qs_spline]
    # timestamps = [i['Date'].timestamp() * 1000 for i in qs_spline]
    # qs_spline_dict = {ts: qs_spline[i] for i, ts in enumerate(timestamps)}
    for casualty_type in main['sum_by_casualty_type']:
        chart['spline']['data_val'].append({
            'name': casualty_type,
            'data': [(ts, qs_spline[i][casualty_type]) for i, ts in enumerate(timestamps)],
        })
    chart['spline']['date_combined'] = [datetime.datetime.combine(i['Date'], i['Time_of_Incident'] or datetime.time()) for i in qs_spline]
    chart['spline']['timestamps'] = timestamps

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
                chart_ct['key'] = "graph_of_incident_and_casualties_trend_by_incident_type"
            else:
                Title = 'Incident Type'
                OrderId = 'Incident_Type_id'
                DbRelated = 'Incident_Type__name'
                chart_ct['key'] = "graph_of_incident_and_casualties_trend_by_incident_type"
        else:
            Title = 'Target Type'
            OrderId = 'Target_id'
            DbRelated = 'Target__code'
            chart_ct['labels'] = main['filters']["target_type"]["labels"]
            chart_ct['labels_all'] = chart_ct['labels']
            chart_ct['key'] = "graph_of_incident_and_casualties_trend_by_target_type"
        chart_ct['title'] = "Graph of Incident and Casualties Trend by "+ Title
        for pc in main["category"]:
            # type_data = undssQueryset.values_list(OrderId).annotate(total = Coalesce(Sum(pc), 0))
            type_data = undssQueryset.values_list(OrderId).annotate(total = main['sum_by_casualty_type'][pc.lower()])
            type_data_dict = dict(type_data)
            total_result = [type_data_dict.get(id,0) for id in main['filters'][filter_key]['checked']]
            chart_ct['data_val'].append({'type':pc, 'data': total_result})

    return chart

def Table(request, filters={}, main={}):
    table = {}

    # undssQueryset = Undss.objects.all()
    # undssQueryset= ApplyFilters(undssQueryset, filters, main=main)
    undssQueryset = main["qs_filtered"]

    # list_of_latest_incidents
    list_of_latest_incidents_qs = undssQueryset
    db_fields = ('id','Date', 'Time_of_Incident','Description_of_Incident')
    table['list_of_latest_incidents'] = {'column_names': db_fields, 'url_name': 'incident_detail'}
    if main['model'] == MasterIncident:
        list_of_latest_incidents_qs = bool2yesno_annotate(undssQueryset)
        table['list_of_latest_incidents']['column_names'] = db_fields + tuple(source_type_rename.keys())
        table['list_of_latest_incidents']['url_name'] = 'master_incident_detail'
        db_fields += tuple(source_type_rename.values())
    table['list_of_latest_incidents']['rows'] = list_of_latest_incidents_qs.values(*db_fields).order_by('-Date','-Time_of_Incident')

    # table incidents_and_casualties_by_incident_type 
    id_field = 'Incident_Subtype' if main['is_subtype'] else 'Incident_Type'
    name_field = 'Incident_Subtype__name' if main['is_subtype'] else 'Incident_Type__name'
    order_field = '-Incident_Subtype_id' if main['is_subtype'] else '-Incident_Type_id'
    filter_incident = main['filters'][main['type_key']]
    qs_casualties_by_incident_type = undssQueryset.\
        values(id_field).\
        annotate(
            row_id = F(id_field),
            incident_name = F(name_field),
            total = Coalesce(Count("id"), 0),
            **main['sum_by_casualty_type'],
            # killed = Coalesce(Sum('killed'), 0),
            # injured = Coalesce(Sum('Injured'), 0),
            # abducted = Coalesce(Sum('Abducted'), 0),
        ).\
        order_by('Date', 'Time_of_Incident')
    qs_casualties_by_incident_type_dict = {i[id_field]:i for i in qs_casualties_by_incident_type}
    default_val = lambda i: {id_field:i,'row_id':i,'incident_name':filter_incident['labels'][i],'total':0,'killed':0,'injured':0,'abducted':0}
    table_incident_type_total = [qs_casualties_by_incident_type_dict.get(type_id, default_val(i)) \
        for i, type_id in enumerate(filter_incident['checked'])]

    table['incidents_and_casualties_by_incident_type'] = {
        'title': 'Incidents and Casualties by Incident %s' % ('Subtype' if main['is_subtype'] else 'Type'),
        'values': table_incident_type_total,
    }

    # table number_of_incident_and_casualties_overview
    if filters.get('dist'):
        adm_code = filters.get('dist') 
        adm_dict = dict(District.objects.values_list('id', 'name').filter(id=filters.get('dist')).order_by('id'))
        child_adm_dict = adm_dict
    elif filters.get('prov'):
        adm_code = filters.get('prov') 
        adm_dict = dict(Province.objects.values_list('id', 'name').order_by('id')) 
        child_adm_dict = dict(District.objects.values_list('id', 'name').filter(province=filters.get('prov')).order_by('id'))
    else:
        adm_code = 0
        adm_dict = {adm_code: 'Afghanistan'}
        child_adm_dict = dict(Province.objects.values_list('id', 'name').order_by('id')) 

    if filters.get('dist') or filters.get('prov'):
        child_adm_id_field = 'District'
        child_adm_name_field = 'District__name'
        child_adm_order_field = '-District_id'
    else:
        child_adm_id_field = 'Province'
        child_adm_name_field = 'Province__name'
        child_adm_order_field = '-Province_id'

    qs_casualties_aggregate = undssQueryset.\
        aggregate(
            total = Coalesce(Count("id"), 0),
            **main['sum_by_casualty_type'],
            # killed = Coalesce(Sum('killed'), 0),
            # injured = Coalesce(Sum('Injured'), 0),
            # abducted = Coalesce(Sum('Abducted'), 0),
        )
    table['number_of_incident_and_casualties_overview'] = {
        'parentdata': [
            adm_dict.get(adm_code),
            qs_casualties_aggregate['total'],
            qs_casualties_aggregate['abducted'],
            qs_casualties_aggregate['injured'],
            qs_casualties_aggregate['killed'],
        ]
    }

    qs_casualties_by_child_adm = undssQueryset.\
        values(child_adm_id_field).\
        annotate(
            row_id = F(child_adm_id_field),
            name = F(child_adm_name_field),
            total = Coalesce(Count("id"), 0),
            **main['sum_by_casualty_type'],
            # killed = Coalesce(Sum('killed'), 0),
            # injured = Coalesce(Sum('Injured'), 0),
            # abducted = Coalesce(Sum('Abducted'), 0),
        ).\
        order_by(child_adm_order_field)
    qs_casualties_by_child_adm_dict = {i[child_adm_id_field]:i for i in qs_casualties_by_child_adm}

    table['number_of_incident_and_casualties_overview']['child'] = [{
        'id': id,
        'name': name,
        'value': [
            name,
            qs_casualties_by_child_adm_dict.get(id,{}).get('total',0),
            qs_casualties_by_child_adm_dict.get(id,{}).get('abducted',0),
            qs_casualties_by_child_adm_dict.get(id,{}).get('injured',0),
            qs_casualties_by_child_adm_dict.get(id,{}).get('killed',0),
        ],
    } for id, name in child_adm_dict.items()]

    table['number_of_incident_and_casualties_overview']['key'] = "number_of_incident_and_casualties_overview"
    table['number_of_incident_and_casualties_overview']['title'] = "Number of Incident and Casualties Overview"

    return table

def Region(request, filters):
    region = {}
    prov = filters.get('prov')
    
    getProvince = Province.objects.values()
    getDistrict = District.objects.all().values("id","name","province__id","province__name")

    prov_name = next((item['name'] for item in getProvince if item["id"] == prov), '')
    dist_name = next((item['name'] for item in getDistrict if item["id"] == filters.get('dist')), '')
     
    if filters.get('dist'):
        dist_qs = getDistrict.get(Q(id=filters.get('dist')))
        prov = dist_qs['province__id']
    getDistrict = getDistrict.filter(Q(province__id=prov))

    region["province"] = {"data_val" : getProvince, "selected": prov, "selected_name": prov_name, "type" : "Province", "urlcode": "prov"}
    region["district"] = {"data_val" : getDistrict, "selected": filters.get('dist',''), "selected_name": dist_name, "type" : "District", "urlcode": "dist"}
    
    return region

def Total(request, filters={}, main={}):
    total = {}

    # undssQueryset = Undss.objects.all()    
    # undssQueryset= ApplyFilters(undssQueryset, filters, main=main)
    undssQueryset = main["qs_filtered"]

    # countryData = []
    # totalCountry = []
    # for pc in main["category"]:
    #     # country_data = undssQueryset.values(pc).annotate(count = Coalesce(Count("Incident_Type_id"), 0), total = Coalesce(Sum(pc), 0)).order_by('-'+pc)
    #     country_data = undssQueryset.values(pc).annotate(count = Coalesce(Count("Incident_Type_id"), 0), total = main['sum_by_casualty_type'][pc.lower()]).order_by('-'+pc)
    #     total_incident = [int(total['count']) for total in country_data]
    #     total_result = [int(total['total']) for total in country_data]
    #     totalCountry += [sum(total_result)]
    #     countryData.append({pc: sum(total_result)})

    # provinceData = []
    # provinceName = []
    # provinceIncident = []
    # for pc in main["category"]:
    #     # province_data = undssQueryset.values('Province__name').annotate(count = Coalesce(Count("Incident_Type_id"), 0),total = Coalesce(Sum(pc), 0)).order_by('-Province_id')
    #     province_data = undssQueryset.values('Province__name').annotate(count = Coalesce(Count("Incident_Type_id"), 0),total = main['sum_by_casualty_type'][pc.lower()]).order_by('-Province_id')
    #     total_incident = [total['count'] for total in province_data] 
    #     total_result = [total['total'] for total in province_data]
    #     province_name = [total['Province__name'] for total in province_data]
    #     provinceData += [[0] if not total_result else total_result]
    #     provinceIncident += [[0] if not total_incident else total_incident]
    #     provinceName += [province_name]

    # countryDataChild = []
    # for i in range(0, len(provinceName[0])):
    #     countryDataChild.append({
    #         'killed': provinceData[0][i],
    #         'injured': provinceData[1][i],
    #         'abducted': provinceData[2][i],
    #         'incident' : provinceIncident[0][i]
    #     })
    
    # countryData.append({'incident': sum(total_incident)})

    # if filters.get('code'):
    #     total['total_data'] = countryDataChild
    # else:
    #     total['total_data'] = countryData  

    total = undssQueryset.aggregate(**main['sum_by_casualty_type'], incident = Coalesce(Count("id"), 0))

    return total  

def DashboardResponse(request, filters={}):
    dashboardresponse = {}
    main = MainData(request, filters=filters)
    chart = Chart(request, filters=filters, main=main)
    table = Table(request, filters=filters, main=main)
    total = Total(request, filters=filters, main=main)
    region = Region(request, filters)
    dashboardresponse["chart"] = chart
    dashboardresponse["tables"] = table
    dashboardresponse["region"] = region
    dashboardresponse["total"] = total
    dashboardresponse["incident_type"] = {}
    dashboardresponse["incident_type"]["name"] = main["incident_type_name"]
    if not filters.get('incident_type') or filters.get('incident_type') == [0]:
        dashboardresponse["incident_type"]["checked"] =  main["incident_type_name"]
    else:
        dashboardresponse["incident_type"]["checked"] = filters.get('incident_type')

    dashboardresponse["filters"] = main["filters"]

    return dashboardresponse

def csv_response(request):
    field_rename_pairs = (
        ('Single_ID', 'Single_ID'),
        ('Date', 'Date '),
        ('Time_of_Incident', 'Time_Inc'),
        ('Province__name', 'Province'),
        ('District__name', 'District'),
        ('City_Village', 'City_Vill'),
        ('Area', 'Area'),
        ('Police_District', 'Police_Dist'),
        ('Incident_Type__name', 'Inc_Type'),
        ('Incident_Subtype__name', 'Inc_Subtype'),
        ('Description_of_Incident', 'Inc_Desc'),
        ('HPA', 'HPA'),
        ('Initiator__code', 'Initiator'),
        ('Target__code', 'Target'),
        ('IGCHO_yesno', 'IGCHO'),
        ('Kill_Natl', 'Kill_Natl'),
        ('Kill_Intl', 'Kill_Intl'),
        ('Kill_ANSF', 'Kill_ANSF'),
        ('Kill_IM', 'Kill_IM'),
        ('Kill_ALP_PGM', 'Kill_ALP_PGM'),
        ('Kill_AOG', 'Kill_AOG'),
        ('Kill_ISKP', 'Kill_ISKP'),
        ('Inj_Natl', 'Inj_Natl'),
        ('Inj_Intl', 'Inj_Intl'),
        ('Inj_ANSF', 'Inj_ANSF'),
        ('Inj_IM', 'Inj_IM'),
        ('Inj_ALP_PGM', 'Inj_ALP_PGM'),
        ('Inj_AOG', 'Inj_AOG'),
        ('Inj_ISKP', 'Inj_ISKP'),
        ('Abd_Natl', 'Abd_Natl'),
        ('Abd_Intl', 'Abd_Intl'),
        ('Abd_ANSF', 'Abd_ANSF'),
        ('Abd_IM', 'Abd_IM'),
        ('Abd_ALP_PGM', 'Abd_ALP_PGM'),
        ('Latitude', 'Latitude'),
        ('Longitude', 'Longitude'),
        # ('Incident_Source__name', 'Source'),
        # ('created_at', 'created_at'),
        # ('updated_at', 'updated_at'),
    )
    filters = make_filters(request)
    main = MainData(request, filters=filters)
    undssQueryset = main["qs_filtered"]
    if main['is_master']:
        # field_rename_pairs += (
        #     ('PRMO', 'PRMO'),
        #     ('INSO', 'INSO'),
        #     ('UNDSS', 'UNDSS'),
        # )
        field_rename_pairs += tuple((f2, f) for f, f2 in source_type_rename.items())
        undssQueryset = bool2yesno_annotate(undssQueryset)
    else:
        field_rename_pairs += (
            ('Incident_Source__name', 'Source'),
        )
        if main['is_prmo']:
            field_rename_pairs += (
                ('Incident_Source_Office__name', 'Source_Office'),
            )
    field_names = [i[0] for i in field_rename_pairs]
    field_renames = [i[1] for i in field_rename_pairs]
    # undssQueryset = Undss.objects.all()
    # undssQueryset = ApplyFilters(undssQueryset, filters, main=main)
    # undssQueryset = bool2yesno_annotate(undssQueryset, field_rename_dict={'IGCHO':'iGHO_yesno'})
    undssQueryset = undssQueryset.annotate(IGCHO_yesno=Bool2YesNo('IGCHO'))
    undssQueryset = undssQueryset.values_list(*field_names).order_by('Date', 'Time_of_Incident')
    return chain([field_renames], undssQueryset)

def Common(request):
    response = {}
    filters = make_filters(request)

    if request.GET['page'] == 'dashboard':
        response = DashboardResponse(request, filters=filters)
         
    response['jsondata'] = json.dumps(response, cls=JSONEncoderCustom)

    return response

def make_filters(request):

    if 'page' not in request.GET:
        mutable = request.GET._mutable
        request.GET._mutable = True
        request.GET['page'] = 'dashboard'
        request.GET._mutable = mutable

    filters = {
        # 'source_type': str(request.GET.get('source_type') or '').strip().lower(),
        # 'prmo_loc': str(request.GET.get('prmo_loc') or '').strip().lower(),
        'source_type': request.GET.get('source_type'),
        'prmo_loc': request.GET.get('prmo_loc'),
        'target_type': [int(i) for i in list(filter(None, (request.GET.get('target_type','').split(','))))],
        'police_district': request.GET.get('police_district'),
        'hpa': str(request.GET.get('hpa') or '').strip().lower(),
        'initiator': request.GET.get('initiator'),
        'impact': str(request.GET.get('impact') or '').strip().lower(),
        'incident_type': [int(i) for i in list(filter(None, (request.GET.get('incident_type','').split(','))))],
        'incident_subtype': [int(i) for i in list(filter(None, (request.GET.get('incident_subtype','').split(','))))],
        'code': request.GET.get('code'),
        'daterange': request.GET.get('daterange'),
    }

    area_param = request.GET.get('code','').split('=')
    if len(area_param) == 2:
        if area_param[0] in ['prov', 'dist']:
            filters[area_param[0]] = int(area_param[1])

    return filters

def ApplyFilters(queryset, filters, main={}):

    if filters.get('prov'):
        queryset = queryset.filter(Province=filters.get('prov'))

    if filters.get('dist'):
        queryset = queryset.filter(District=filters.get('dist'))

    if filters.get('daterange'):
        date = filters['daterange'].split(',')
        queryset = queryset.filter(Date__gte=date[0],Date__lte=date[1])
    else:
        date = main["daterange"].split(',')
        queryset = queryset.filter(Date__gte=date[0],Date__lte=date[1])
        
    if filters.get('incident_type'):
        queryset = queryset.filter(Incident_Type__in=filters.get('incident_type'))

    if filters.get('source_type'):
        if main['model'] == Undss:
            # queryset = queryset.annotate(source_type_lowered=Lower(Trim('Incident_Source'))).\
            #     filter(source_type_lowered=filters.get('source_type'))
            queryset = queryset.filter(Incident_Source=filters.get('source_type'))

            if main['is_prmo'] and filters.get('prmo_loc'):
                # queryset = queryset.annotate(prmo_loc_lowered=Lower(Trim('Incident_Source_Office'))).\
                #     filter(prmo_loc_lowered=filters.get('prmo_loc'))
                queryset = queryset.filter(Incident_Source_Office=filters.get('prmo_loc'))

    if filters.get('incident_subtype'):
        queryset = queryset.filter(Incident_Subtype__in=filters.get('incident_subtype'))

    if filters.get('initiator'):
        queryset = queryset.filter(Initiator=filters.get('initiator'))

    if filters.get('target_type'):
        queryset = queryset.filter(Target__in=filters.get('target_type'))

    if filters.get('police_district'):
        queryset = queryset.filter(Police_District=filters.get('police_district'))

    if filters.get('hpa') in yesno2truefalse:
        queryset = yesno_annotate(queryset, 'HPA').filter(**{'yesno': filters.get('hpa')})

    # if filters.get('impact'):
    if filters.get('impact') in yesno2truefalse:
        queryset = queryset.filter(IGCHO=yesno2truefalse[filters['impact']])

    return queryset

def bool2yesno_annotate(queryset, field_rename_dict=source_type_rename):
    annotations = {f2: Bool2YesNo(f) for f, f2 in field_rename_dict.items()}
    return queryset.annotate(**annotations)

def yesno_annotate(queryset, field):
    return queryset.annotate(lowered=Lower(Trim(field))).annotate(
                yesno=Case(
                    When(lowered='yes', then=Value('yes')),
                    default=Value('no'),
                    output_field=CharField(),
                ),
            )
