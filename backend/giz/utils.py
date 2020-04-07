import json

class JSONEncoderCustom(json.JSONEncoder):
    def default(self, obj):
        if obj.__class__.__name__ in ["GeoValuesQuerySet","ValuesQuerySet","QuerySet"]:
            return list(obj)
        elif obj.__class__.__name__ == "date":
            return obj.strftime("%Y-%m-%d")
        elif obj.__class__.__name__ == "time":
            return obj.strftime("%H-%M-%S")
        elif obj.__class__.__name__ == "datetime":
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif obj.__class__.__name__ == "Decimal":
            return float(obj)
        else:
            print('not converted to json:', obj.__class__.__name__)
            return 'not converted to json: %s' % (obj.__class__.__name__)
