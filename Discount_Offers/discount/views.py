from django.shortcuts import render, redirect
from django.contrib import messages
from openpyxl.workbook.workbook import Workbook
from django.http import HttpResponse
from .forms import DiscountOfferForm
from .models import DiscountOffer

from django.http import FileResponse, HttpResponseNotFound
import os
from .utils import export_db_to_excel
from django.http import JsonResponse


def discount_form_view(request):
    if request.method == 'POST':
        form = DiscountOfferForm(request.POST)
        if form.is_valid():
            account_number = form.cleaned_data['account_number']
            discount_offer = form.cleaned_data['discount_offer']
            ticket_number = form.cleaned_data['ticket_number']
            region = form.cleaned_data['region']
            date_processed = form.cleaned_data['date_processed']

            # Save the validated data to the database
            DiscountOffer.objects.create(
                account_number=account_number,
                discount_offer=discount_offer,
                ticket_number=ticket_number,
                region=region,
                date_processed=date_processed
            )

            # Show success message
            messages.success(request, f"Discount {discount_offer} applied successfully!")
            return redirect('success')
    else:
        form = DiscountOfferForm()

    return render(request, 'discount_form.html', {'form': form})


def success_view(request):
    """Renders the success page."""
    return render(request, 'success.html')


def export_to_excel(request):
    # Fetch all DiscountOffer data
    data = DiscountOffer.objects.all()

    # Create a new Excel workbook
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Discount Offers"

    # Add headers
    headers = ["Account Number", "Discount Offer", "Ticket Number", "Region", "Date Processed"]
    sheet.append(headers)

    # Add data rows
    for offer in data:
        sheet.append([
            offer.account_number,
            offer.discount_offer,
            offer.ticket_number,
            offer.region,
            offer.date_processed.strftime("%Y-%m-%d")
        ])

    # Create HTTP response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename="discount_offers.xlsx"'
    workbook.save(response)
    return response


def discount_offers_api(request):
    offers = DiscountOffer.objects.all().values(
        'account_number', 'discount_offer', 'ticket_number', 'region', 'date_processed'
    )
    return JsonResponse({'data': list(offers)})


def discount_offers_table(request):
    return render(request, 'data_view_and_export.html')
