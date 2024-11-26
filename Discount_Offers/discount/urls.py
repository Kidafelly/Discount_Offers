from django.urls import path

from . import views
urlpatterns = [
    path('', views.discount_offers_table, name='discount_offers_table'),
    path('add_discount_offer', views.discount_form_view, name='add_discount_offer'),
    path('success/', views.success_view, name='success'),
    path('discount-offers/', views.discount_offers_table, name='discount_offers_table'),
    path('api/discount-offers/', views.discount_offers_api, name='discount_offers_api'),
    path('export-discount-offers/', views.export_to_excel, name='export_discount_offers'),
]


