import pdfkit
from django.shortcuts import render, redirect
# from django.template import RequestContext
from django.template.loader import get_template 
# from django.template import Context

from django.contrib.auth.decorators import login_required

from .forms import UndssForm
from .json_serializable import Common
from giz.utils import replace_query_param

@login_required
def InputDashboard(request):
    template = "dashboard/undss_form.html"

    # form = UndssForm(request.POST or None)
    # if form.is_valid():
    #     form.save()

    form = UndssForm(request.POST, request.FILES or None)
    if form.is_valid():
        form.save()

    # if request.method == 'POST':
    #     form = UndssForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         form.save()
    # else:
    #     form = UndssForm()

    context = {'form': form }
    return render(request, template, context)


@login_required
def Dashboard(request):
    if not request.GET.get('page'):
        currenturl = request.build_absolute_uri()
        return redirect(replace_query_param(currenturl, 'page', 'dashboard'))

    response = Common(request)
    template = "dashboard/dashboard_content.html"

    if 'pdf' in request.GET:
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
        }
        template = get_template(template)
        # context = Context(response)  # data is the context data that is sent to the html file to render the output. 
        html = template.render(response)  # Renders the template with the context data.
        pdfkit.from_string(html, 'out.pdf')
        pdf = open("out.pdf")
        response = HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
        response['Content-Disposition'] = 'attachment; filename=output.pdf'
        pdf.close()
        os.remove("out.pdf")  # remove the locally created pdf file.
        return response  # returns the response

    return render(request, template, response)

# @login_required
# def DashboardPrint(request):
#     response = Common(request)
#     # template = ""
#     pass