from django.urls import path

from . import views
from .controllers import AssetController
from assets.views import LabelsView

app_name = "assets"
urlpatterns = [
    # path("", views.menu, name="menu"),
    path("", views.index, name="index"),
    path("login", views.loginPage, name="login"),
    path("logged", views.logged, name="logged"),
    path("logout", views.getLogout, name="logout"),
    path("create", views.create, name="create"),
    path("edit/<int:asset_id>", views.edit, name="edit"),
    path("assetCreateOrUpdate", AssetController.createOrUpdate, name="assetCreateOrUpdate"),
    path("assetImageDelete/<int:img_id>", AssetController.deleteImage, name="assetImageDelete"),
    path("assetImageDelete", AssetController.invalidRoute, name="assetImageDelete"),
    path("assetFileDelete/<int:file_id>", AssetController.deleteFile, name="assetFileDelete"),
    path("assetFileDelete", AssetController.invalidRoute, name="assetFileDelete"),
    path("assetSalida", AssetController.registrarSalida, name="assetSalida"),
    path("testjson", AssetController.testJson, name="testjson"),
    path("exportAssets", views.exportAssetsExcel, name="exportAssets"),
    path("seeQR/<int:asset_id>", views.LabelsView.as_view(), name="seeQR"),
    path("seeQR", AssetController.invalidRoute, name="seeQR"),
]