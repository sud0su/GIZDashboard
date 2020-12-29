from organization.models import Organization
from reference.models import District, IncidentSource, IncidentSubtype, IncidentType, Province
from django.core.exceptions import ValidationError
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateWidget
from .models import Undss, MasterIncident
from datetime import datetime, time


class DistrictForeignKey(ForeignKeyWidget):
    def get_queryset(self, value, row, *args, **kwargs):
        return self.model.objects.filter(name=value, province__name__contains=row.get('Province'))


class IncidentSubTypeForeignKey(ForeignKeyWidget):
    def get_queryset(self, value, row, *args, **kwargs):
        return self.model.objects.filter(name=value, incidenttype__name__contains=row.get('Inc_Type'))

class UndssResource(resources.ModelResource):
    Date = fields.Field(column_name='Date', attribute='Date',
                        widget=DateWidget(format='%m-%d-%Y'))
    Time_of_Incident = fields.Field(
        column_name='Time_Inc', attribute='Time_of_Incident', default=time())
    province = fields.Field(column_name='Province', attribute='Province',
                            widget=ForeignKeyWidget(Province, 'name'))
    district = fields.Field(column_name='District', attribute='District',
                            widget=DistrictForeignKey(District, 'name'))
    City_Village = fields.Field(
        column_name='City_Vill', attribute='City_Village')
    Police_District = fields.Field(
        column_name='Police_Dist', attribute='Police_District')
    incident_type = fields.Field(
        column_name='Inc_Type', attribute='Incident_Type', widget=ForeignKeyWidget(IncidentType, 'name'))
    incident_subtype = fields.Field(column_name='Inc_Subtype', attribute='Incident_Subtype',
                                    widget=IncidentSubTypeForeignKey(IncidentSubtype, 'name'))
    Description_of_Incident = fields.Field(
        column_name='Inc_Desc', attribute='Description_of_Incident')
    initiator = fields.Field(column_name='Initiator', attribute='Initiator',
                             widget=ForeignKeyWidget(Organization, 'code'))
    target = fields.Field(column_name='Target', attribute='Target',
                          widget=ForeignKeyWidget(Organization, 'code'))
    incident_source = fields.Field(column_name='Source', attribute='Incident_Source')
    Incident_Source_Office = fields.Field(column_name='Source Office', attribute='Incident_Source_Office')
    
    class Meta:
        model = Undss
        fields = ('Single_ID', 'Date', 'Time_of_Incident', 'province', 'district', 'City_Village', 'Area', 'Police_District', 'incident_type', 'incident_subtype', 'Description_of_Incident', 'HPA', 'initiator', 'target','IGHO', 'Kill_Natl', 'Kill_Intl', 'Kill_ANSF',
                  'Kill_IM', 'Kill_ALP_PGM', 'Kill_AOG', 'Kill_ISKP', 'Inj_Natl', 'Inj_Intl', 'Inj_ANSF', 'Inj_IM', 'Inj_ALP_PGM', 'Inj_AOG', 'Inj_ISKP', 'Abd_Natl', 'Abd_Intl', 'Abd_ANSF', 'Abd_IM', 'Abd_ALP_PGM', 'Latitude', 'Longitude', 'incident_source','Incident_Source_Office',)
        exclude = ('id', 'created_at', 'updated_at',)
        clean_model_instances = True
        import_id_fields = ('Single_ID',)

    def before_import_row(self, row, **kwargs):
        single_id = row.get('Single_ID')
        province = row.get('Province')
        district = row.get('District')
        date = row.get('Date')
        incident_type = row.get('Inc_Type')
        incident_subtype = row.get('Inc_Subtype')
        initiator = row.get('Initiator')
        target = row.get('Target')
        # incident_source = row.get('Source')
        timeofincident = row.get('Time_Inc')
        hpa = row.get('HPA')

        if single_id == 'null' or single_id == None:
            raise ValidationError("Single ID cannot be null")

        if date is not None or date != 'null':
            if isinstance(date, datetime):
                value = date.date().strftime('%m-%d-%Y')
                try:
                    datetime.strptime(str(value), '%m-%d-%Y')
                    row['Date'] =  date.date().strftime('%m-%d-%Y')
                except (ValueError, TypeError):
                    raise ValidationError(
                        "Incorrect data format, should be MM-DD-YYYY")
            else:
                raise ValidationError(
                    "Incorrect data format, Date should be in date format")
        else:
            raise ValidationError("Date cannot be blank")

        if timeofincident is not None or timeofincident != 'null':
            try:
                if isinstance(timeofincident, datetime):
                    row['Time_Inc'] = timeofincident.strftime('%H:%M:%S')
                else:
                    row['Time_Inc'] = timeofincident
            except ValueError:
                raise ValidationError(
                    "Incorrect time format, should be hh:mm:ss")
        else:
            raise ValidationError('Time of Incident cannot be blank')

        if hpa is None:
            row['HPA'] = 'no'
        elif hpa.lower() == 'yes' or hpa.lower() == 'no':
            row['HPA'] = hpa.lower()
        else:
            raise ValidationError('HPA value must be "yes" or "no"')

        prov = Province.objects.filter(name=province)
        if not bool(prov):
            raise ValidationError(
                'Province name %s cannot be found' % province)

        dist = District.objects.filter(
            name=district, province__name__contains=province)
        if not bool(dist):
            raise ValidationError(
                'District name %s cannot be found in %s Province' % (district, province))

        itype = IncidentType.objects.filter(name=incident_type)
        if not bool(itype):
            raise ValidationError(
                'Incident Type name %s cannot be found' % incident_type)

        if incident_subtype is not None:
            istype = IncidentSubtype.objects.filter(
                name=incident_subtype, incidenttype__name__contains=incident_type)
            if not bool(istype):
                raise ValidationError('Incident Sub Type name %s cannot be found in %s Incident Type' % (
                    incident_subtype, incident_type))

        init = Organization.objects.filter(code=initiator)
        if not bool(init):
            raise ValidationError('Initiator name %s cannot be found' % init)

        target = Organization.objects.filter(code=target)
        if not bool(target):
            raise ValidationError('Target name %s cannot be found' % target)

        # incsource = IncidentSource.objects.filter(name=incident_source)
        # if not bool(incsource):
        #     raise ValidationError(
        #         'Incident Source name %s cannot be found' % incident_source)

class MasterIncidentResource(resources.ModelResource):
    Date = fields.Field(column_name='Date', attribute='Date',
                        widget=DateWidget(format='%m-%d-%Y'))
    Time_of_Incident = fields.Field(
        column_name='Time_Inc', attribute='Time_of_Incident', default=time())
    province = fields.Field(column_name='Province', attribute='Province',
                            widget=ForeignKeyWidget(Province, 'name'))
    district = fields.Field(column_name='District', attribute='District',
                            widget=DistrictForeignKey(District, 'name'))
    City_Village = fields.Field(
        column_name='City_Vill', attribute='City_Village')
    Police_District = fields.Field(
        column_name='Police_Dist', attribute='Police_District')
    incident_type = fields.Field(
        column_name='Inc_Type', attribute='Incident_Type', widget=ForeignKeyWidget(IncidentType, 'name'))
    incident_subtype = fields.Field(column_name='Inc_Subtype', attribute='Incident_Subtype',
                                    widget=IncidentSubTypeForeignKey(IncidentSubtype, 'name'))
    Description_of_Incident = fields.Field(
        column_name='Inc_Desc', attribute='Description_of_Incident')
    initiator = fields.Field(column_name='Initiator', attribute='Initiator',
                             widget=ForeignKeyWidget(Organization, 'code'))
    target = fields.Field(column_name='Target', attribute='Target',
                          widget=ForeignKeyWidget(Organization, 'code'))

    class Meta:
        model = MasterIncident
        fields = ('Single_ID', 'Date', 'Time_of_Incident', 'province', 'district', 'City_Village', 'Area', 'Police_District', 'incident_type', 'incident_subtype', 'Description_of_Incident', 'HPA', 'initiator', 'target','IGHO', 'Kill_Natl', 'Kill_Intl', 'Kill_ANSF',
                  'Kill_IM', 'Kill_ALP_PGM', 'Kill_AOG', 'Kill_ISKP', 'Inj_Natl', 'Inj_Intl', 'Inj_ANSF', 'Inj_IM', 'Inj_ALP_PGM', 'Inj_AOG', 'Inj_ISKP', 'Abd_Natl', 'Abd_Intl', 'Abd_ANSF', 'Abd_IM', 'Abd_ALP_PGM', 'Latitude', 'Longitude','PRMO','UNDSS','INSO',)
        exclude = ('id', 'created_at', 'updated_at',)
        clean_model_instances = True
        import_id_fields = ('Single_ID',)

    def before_import_row(self, row, **kwargs):
        single_id = row.get('Single_ID')
        province = row.get('Province')
        district = row.get('District')
        date = row.get('Date')
        incident_type = row.get('Inc_Type')
        incident_subtype = row.get('Inc_Subtype')
        initiator = row.get('Initiator')
        target = row.get('Target')
        timeofincident = row.get('Time_Inc')
        hpa = row.get('HPA')
        prmo = str.lower('no' if row.get('PRMO') is None else row.get('PRMO'))
        undss = str.lower('no' if row.get('UNDSS') is None else row.get('UNDSS'))
        inso = str.lower('no' if row.get('INSO') is None else row.get('INSO'))

        if prmo == 'yes':
            row['PRMO'] = 1
        else:
            row['PRMO'] = 0
        
        if undss == 'yes':
            row['UNDSS'] = 1
        else:
            row['UNDSS'] = 0
    
        if inso == 'yes':
            row['INSO'] = 1
        else:
            row['INSO'] = 0

        if single_id == 'null' or single_id == None:
            raise ValidationError("Single ID cannot be null")

        if date is not None or date != 'null':
            if isinstance(date, datetime):
                value = date.date().strftime('%m-%d-%Y')
                try:
                    datetime.strptime(str(value), '%m-%d-%Y')
                    row['Date'] =  date.date().strftime('%m-%d-%Y')
                except (ValueError, TypeError):
                    raise ValidationError(
                        "Incorrect data format, should be MM-DD-YYYY")
            else:
                raise ValidationError(
                    "Incorrect data format, Date should be in date format")
        else:
            raise ValidationError("Date cannot be blank")

        if timeofincident is not None or timeofincident != 'null':
            try:
                if isinstance(timeofincident, datetime):
                    row['Time_Inc'] = timeofincident.strftime('%H:%M:%S')
                else:
                    row['Time_Inc'] = timeofincident
            except ValueError:
                raise ValidationError(
                    "Incorrect time format, should be hh:mm:ss")
        else:
            raise ValidationError('Time of Incident cannot be blank')

        if hpa is None:
            row['HPA'] = 'no'
        elif hpa.lower() == 'yes' or hpa.lower() == 'no':
            row['HPA'] = hpa.lower()
        else:
            raise ValidationError('HPA value must be "yes" or "no"')

        prov = Province.objects.filter(name=province)
        if not bool(prov):
            raise ValidationError(
                'Province name %s cannot be found' % province)

        dist = District.objects.filter(
            name=district, province__name__contains=province)
        if not bool(dist):
            raise ValidationError(
                'District name %s cannot be found in %s Province' % (district, province))

        itype = IncidentType.objects.filter(name=incident_type)
        if not bool(itype):
            raise ValidationError(
                'Incident Type name %s cannot be found' % incident_type)

        if incident_subtype is not None:
            istype = IncidentSubtype.objects.filter(
                name=incident_subtype, incidenttype__name__contains=incident_type)
            if not bool(istype):
                raise ValidationError('Incident Sub Type name %s cannot be found in %s Incident Type' % (
                    incident_subtype, incident_type))

        init = Organization.objects.filter(code=initiator)
        if not bool(init):
            raise ValidationError('Initiator name %s cannot be found' % init)

        target = Organization.objects.filter(code=target)
        if not bool(target):
            raise ValidationError('Target name %s cannot be found' % target)
