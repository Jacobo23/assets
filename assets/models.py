from django.db import models
from django.contrib.auth.models import User
from pathlib import Path
# from assets.models import AssetQR
# from assets.models import CustomerForUser
# from .models import Transaction
import datetime
# from .controllers import AssetController
import os
import requests
from django.core.files.base import ContentFile


class Customer(models.Model):
    name = models.CharField(max_length=100)
    # allowed_users = models.ManyToManyField(User,blank=True, default=None)
    def __str__(self):
        return self.name
    def getCustomersForUser(user: User):
        customers_rel = CustomerForUser.objects.filter(user=user)
        customers = []
        for customer in customers_rel:
            customers.append(customer.customer)
        return customers
    def isAuthorizedForUser(self,user: User):
        customers_rel = Customer.getCustomersForUser(user)
        return self in customers_rel

        
class Regime(models.Model):
    name = models.CharField(max_length=10)
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=15)
    def __str__(self):
        return self.name


class Custom(models.Model):
    name = models.CharField(max_length=15)
    def __str__(self):
        return self.name


class StorageLocation(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name


class Asset(models.Model):
    asset = models.CharField(max_length=50, null=True, default=None)
    asset_identifier = models.CharField(max_length=10, null=True, default=None)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    description = models.CharField(max_length=250, null=True, default=None)
    brand = models.CharField(max_length=50, null=True, default=None)
    model = models.CharField(max_length=50, null=True, default=None)
    serial_number = models.CharField(max_length=50)
    storage_location = models.CharField(max_length=50)
    pediment = models.CharField(max_length=10, null=True, default=None)
    invoice = models.CharField(max_length=50, null=True, default=None)
    pediment_invoice_date = models.DateTimeField("Pediment-Invoice date", null=True, default=None)
    regime = models.ForeignKey(Regime, on_delete=models.CASCADE, null=True)
    custom = models.ForeignKey(Custom, on_delete=models.CASCADE, null=True)
    patent = models.CharField(max_length=50, null=True, default=None)
    tags = models.ManyToManyField(Tag,blank=True)
    notes = models.CharField(max_length=1024, null=True, default=None)
    status = models.ForeignKey(Status, on_delete=models.CASCADE,null=True)
    motivo_salida = models.CharField(max_length=100,null=True, default=None)

    def __str__(self):
        return self.asset_identifier
    def formatedInvoiceDate(self):
        return 'hi'
    def getImages(self):
        images = AssetImage.objects.filter(asset=self)
        ret = []
        for img in images:
            ret.append(img)
        return ret
    def getImagesCount(self):
        count = len(self.getImages())
        return count
    def getFiles(self):
        files = AssetFile.objects.filter(asset=self)
        ret = []
        for file in files:
            ret.append(file)
        return ret
    def getFilesCount(self):
        count = len(self.getFiles())
        return count
    def setField(self, user, field, value):
        # haz los cambios
        old_val = getattr(self, field)
        setattr(self, field, value)
        # registra la transaccion solo si es un Update
        if(self.pk):
            try:
            # revisar si realment hubo un cambio
                if(old_val != value):
                    transaccion = Transaction()
                    transaccion.user = user
                    transaccion.asset = self
                    transaccion.date = datetime.datetime.now() 
                    transaccion.action = 'Updated ' + field + " from " + old_val + " to " + value
                    transaccion.save()
            except:
                return
    def getTransactions(self):
        return Transaction.objects.filter(asset=self)
    def warnings(self):
        # podemos usar esta funcion para dar alertas sobre algun asset
        # Ex: Falta de pedimento o factura
        warnings = []
        if(self.pediment is None or self.pediment == ''):
            warnings.append({
                    'type':'warning',
                    'message':'Falta Pedimento'
                })
        if(self.invoice is None or self.invoice == ''):
            warnings.append({
                    'type':'warning',
                    'message':'Falta Factura'
                })
        return warnings
    
    def cleanQRs(self):
        qrs = AssetQR.objects.filter(asset=self)
        ret = []
        for qr in qrs:
            qr.delete()
        return None
    def getQR(self):
        return AssetQR.objects.get(asset=self)

    def loadQR(self, url):
        response = requests.get(url)
        response.raise_for_status()
        image_content = response.content

        filename = os.path.basename(url)
        image_file = ContentFile(image_content, name=filename)
        # borrar QR existente y volverlo a crear, puede no tener sentido al principio pero es una manera de resetear el qr si algo salio mal en el intento pasado
        self.cleanQRs()
        qrEnt = AssetQR()
        qrEnt.asset = self
        qrEnt.image = image_file
        qrEnt.save()
        return qrEnt



class AssetImage(models.Model):
    asset = models.ForeignKey(Asset, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='asset_images/')

    def __str__(self):
        return f"Image for {self.asset.pk}"
    
class AssetQR(models.Model):
    asset = models.ForeignKey(Asset, related_name='qr', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='asset_qr/')

    def __str__(self):
        return f"QR for {self.asset.pk}"
    
  
    

class AssetFile(models.Model):
    asset = models.ForeignKey(Asset, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='asset_files/')

    def __str__(self):
        return f"File for {self.asset.pk}"
    def filename(self):
        return Path(self.file.name).name


class Activity(models.Model):
    type = models.CharField(max_length=10)
    user = models.CharField(max_length=10)
    action = models.CharField(max_length=50)

    def __str__(self):
        return self.action
    def slog(text):
        slog = Activity()
        slog.action = text
        slog.type = 'slog'
        slog.user = ''
        slog.save()
    
class Transaction(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField("Fecha de la Transaccion")
    action = models.CharField(max_length=100)

    def __str__(self):
        return self.action
    
class CustomerForUser(models.Model):
    # este modelo guarda la relacion entre usuario y cliente ya que cada usuario solo tendra acceso a clientes especificos
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f"User {self.user} can see {self.customer}"
    

