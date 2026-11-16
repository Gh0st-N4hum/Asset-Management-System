from django.urls import path

from . import views

urlpatterns = [
    path("", views.AssetListView.as_view(), name="asset_list"),
    path("assets/new/", views.AssetCreateView.as_view(), name="asset_create"),
    path("assets/<int:pk>/", views.AssetDetailView.as_view(), name="asset_detail"),
    path("assets/<int:pk>/edit/", views.AssetUpdateView.as_view(), name="asset_update"),
]
