from django.contrib import admin

from discount.models import DiscountOffer


# Register your models here.
@admin.register(DiscountOffer)
class Admin(admin.ModelAdmin):
    list_display = ('account_number', 'discount_offer', 'ticket_number', 'region', 'date_processed')
    search_fields = ('account_number', 'discount_offer', 'ticket_number', 'region')
    list_filter = ('region', 'date_processed')
    ordering = ('-date_processed',)
    date_hierarchy = 'date_processed'
    list_per_page = 10
    list_max_show_all = 100
