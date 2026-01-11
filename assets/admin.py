from django.contrib import admin
from .models import Asset
from .models import Customer
from .models import Custom
from .models import Regime
from .models import Status 
from .models import Activity
from .models import AssetImage
from .models import AssetQR
from .models import Transaction
from .models import CustomerForUser
from assets.models import AssetQR

# Register your models here.
admin.site.register(Asset)
admin.site.register(Customer)
admin.site.register(Custom)
admin.site.register(Regime)
admin.site.register(Status)
admin.site.register(Activity)
admin.site.register(AssetImage)
admin.site.register(AssetQR)
admin.site.register(Transaction)
admin.site.register(CustomerForUser)

admin.site.site_header = "Administracion"
admin.site.site_title = "Assets Admin Page"
