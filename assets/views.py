from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from .models import Asset
from .controllers import AssetController
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from assets.models import Activity, AssetQR
from django.contrib.auth.decorators import permission_required
from typing import List
from django.contrib.auth.mixins import LoginRequiredMixin
from django_renderpdf.views import PDFView
from weasyprint.urls import default_url_fetcher
from django.conf.urls.static import static
from django.conf import settings
from django.urls import reverse

# from assets.views import create

# Create your views here.

def loginPage(request):
    context = {}
    return render(request, "assets/login.html", context)

def logged(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        redirect_to = request.GET.get('next') or '/assets/'
        return redirect(redirect_to)
         
    return redirect('/assets/login')

def getLogout(request):
    logout(request)
    return redirect('/assets/')


@login_required(login_url='/assets/login')
@permission_required("assets.view_asset", raise_exception=True)
def index(request):
    data = request.GET
    param = data.get('param')
    customer = data.get('customer')
    status = data.get('status')
    # search puede ser invocado sin parametros (pero nos daria todos los registros)
    # en este caso solo utilizamos in campo "param" que lo usaremos para buscar como asset, description, pediment, etc...
    assets = AssetController.search(param, param, customer, param, param, param, status)
    context = AssetController.getIndexContext(assets, request.user)
    return render(request, "assets/index.html", context)

@login_required(login_url='/assets/login')
def create(request):
    context = AssetController.getContext(request.user)
    return render(request, "assets/create.html", context)

def edit(request, asset_id):
    asset = get_object_or_404(Asset, pk=asset_id)
    # revisar si el usuario tin accesso al cliente de este asset
    if(not asset.customer.isAuthorizedForUser(request.user)):
        context = {
            'message': 'Accesso denegado! Cliente no autorizado'
        }
        return render(request, "assets/warning_page.html", context)

    context = AssetController.getContext(request.user,asset)
    return render(request, "assets/create.html", context)

def exportAssetsExcel(request):
    data = request.GET
    param = data.get('param')
    customer = data.get('customer')
    status = data.get('status')
    # search puede ser invocado sin parametros (pero nos daria todos los registros)
    # en este caso solo utilizamos in campo "param" que lo usaremos para buscar como asset, description, pediment, etc...
    assets = AssetController.search(param, param, customer, param, param, param, status)
    return AssetController.exportAssets(list(assets))


class LabelsView(LoginRequiredMixin, PDFView):
    """Generate labels for some Shipments.

    A PDFView behaves pretty much like a TemplateView, so you can treat it as such.
    """
    template_name = 'assets/pdf_qr_template.html'

    def get_context_data(self, *args, **kwargs):
    
        """Pass some extra context to the template."""
        context = super().get_context_data(*args, **kwargs)
        asset = Asset.objects.get(pk=kwargs['asset_id'])
        context['asset'] = asset
        media_folder_url = settings.HOSTNAME
        if(media_folder_url is None):
            media_folder_url = self.request.get_host()

        
        context['url'] = default_url_fetcher(settings.PROTOCOL+media_folder_url+"/media/logo.png")['redirected_url']
        # crear el QR
        view_asset_url = reverse('assets:edit',args=[asset.pk])
        qr = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data='+settings.PROTOCOL+media_folder_url+view_asset_url
        
        qr_url = asset.loadQR(qr)
        qr_url = qr_url.image.name
        context['imgname'] = qr_url
        context['host'] = media_folder_url
        context['qr'] = default_url_fetcher(settings.PROTOCOL+media_folder_url+"/media/"+qr_url)['redirected_url']

        return context
    

    
    
