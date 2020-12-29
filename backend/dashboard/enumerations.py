MASTER_NAME = 'Master'
source_type_dbfield = {'prmo':'PRMO', 'inso':'INSO', 'undss':'UNDSS'}
source_types = [
    {'id':'master', 'name': 'Master'},
    {'id':'prmo', 'name':'PRMO'},
    {'id':'inso', 'name':'INSO'},
    {'id':'undss', 'name':'UNDSS'},
]
source_type_rename = {'PRMO': 'PRMO_yesno', 'INSO': 'INSO_yesno', 'UNDSS': 'UNDSS_yesno'}
yesno2truefalse = {'yes':True, 'no': False}
