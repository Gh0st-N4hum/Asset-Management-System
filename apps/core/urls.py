from django.urls import path

from . import views

urlpatterns = [
    path("", views.AssetListView.as_view(), name="asset_list"),
    path("assets/<int:pk>/", views.AssetDetailView.as_view(), name="asset_detail"),
]
