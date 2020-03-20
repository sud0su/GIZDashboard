from django.shortcuts import render

def Dashboard(request):
    data = 'wowww'
    title = 'renderer template'
    template = "dashboard/dashboard_base.html"
    context = {"title": title, "data": data}
    return render(request, template, context)