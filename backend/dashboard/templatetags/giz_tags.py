import json
from django import template
from giz.utils import JSONEncoderCustom

register = template.Library()

@register.simple_tag
def readable(val):
    if val>=1000 and val<1000000:
    	c = ('%.1f' % (round((val/1000), 2))).rstrip('0').rstrip('.')
    	return '{} K'.format(c) 
    elif val>=1000000 and val<1000000000:
    	b = ('%.1f' % (round((val/1000000), 2))).rstrip('0').rstrip('.')
    	return '{} M'.format(b)
    else:
    	return ('%.1f' % round(val or 0)).rstrip('0').rstrip('.')

@register.filter( is_safe=True )
def jsonify(object):
	return json.dumps(object,cls=JSONEncoderCustom)


@register.filter
def listbykeys(object, keys):
	return [object.get(k.strip()) for k in keys.split(',')]

@register.filter
def createlist(object, listname):
	object[listname] = []
	return object[listname]

@register.filter
def listaddchild(object, listname):
	object[listname] = []
	return object[listname]
