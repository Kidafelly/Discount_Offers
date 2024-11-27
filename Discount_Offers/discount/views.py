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


from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import DiscountOfferForm
from .models import DiscountOffer

def discount_form_view(request):
    if request.method == 'POST':
        form = DiscountOfferForm(request.POST)
        if form.is_valid():
            account_number = form.cleaned_data['account_number']
            discount_offer = form.cleaned_data['discount_offer']
            status = form.cleaned_data['status']
            ticket_number = form.cleaned_data['ticket_number']
            region = form.cleaned_data['region']
            date_processed = form.cleaned_data['date_processed']

            # Additional validation for blocked_offer and 50% discount
            if status == 'blocked_offer':
                if discount_offer != '50%':
                    messages.error(request, "Blocked Offer is only eligible for a 50% discount.")
                    return render(request, 'discount_form.html', {'form': form})
                
                # Check if 50% discount has already been applied for this account
                already_applied = DiscountOffer.objects.filter(
                    account_number=account_number, discount_offer='50%', status='blocked_offer'
                ).exists()
                if already_applied:
                    messages.error(request, "50% discount can only be applied once for a Blocked Offer.")
                    return render(request, 'discount_form.html', {'form': form})

            # Validation for inactive_offer
            if status == 'inactive_offer':
                applied_discounts = DiscountOffer.objects.filter(account_number=account_number).values_list(
                    'discount_offer', flat=True
                )
                required_sequence = ['50%', '25%', '10%']
                
                # Check if all discounts have been applied
                if len(applied_discounts) >= len(required_sequence):
                    messages.error(request, "This account has already applied for all available discounts.")
                    return render(request, 'discount_form.html', {'form': form})

                # Check if the discount is applied in the correct order
                next_discount = required_sequence[len(applied_discounts)]
                if discount_offer != next_discount:
                    messages.error(
                        request, f"Discounts must be applied in this order: {', '.join(required_sequence)}. "
                                 f"You must apply for the {next_discount} discount first."
                    )
                    return render(request, 'discount_form.html', {'form': form})

            # Save the validated data to the database
            DiscountOffer.objects.create(
                account_number=account_number,
                discount_offer=discount_offer,
                status=status,
                ticket_number=ticket_number,
                region=region,
                date_processed=date_processed
            )

            messages.success(request, f"Discount {discount_offer} for {status} applied successfully!")
            return redirect('success')
    else:
        form = DiscountOfferForm()

    return render(request, 'discount_form.html', {'form': form})


def success_view(request):
    """Renders the success page."""
    return render(request, 'success.html')


from django.http import JsonResponse, HttpResponse
from openpyxl.workbook.workbook import Workbook
from .models import DiscountOffer

def export_to_excel(request):
    # Fetch all DiscountOffer data
    data = DiscountOffer.objects.all()

    # Create a new Excel workbook
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Discount Offers"

    # Add headers
    headers = ["Account Number", "Discount Offer", "Status", "Ticket Number", "Region", "Date Processed"]
    sheet.append(headers)

    # Add data rows
    for offer in data:
        sheet.append([
            offer.account_number,
            offer.discount_offer,
            offer.status,  # Include the status field
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
    # Include the status field in the API response
    offers = DiscountOffer.objects.all().values(
        'account_number', 'discount_offer', 'status', 'ticket_number', 'region', 'date_processed'
    )
    return JsonResponse({'data': list(offers)})


def discount_offers_table(request):
    # Render the updated template with the new status field
    return render(request, 'data_view_and_export.html')
