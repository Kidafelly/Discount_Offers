from django import forms
from datetime import date
from .models import DiscountOffer

class DiscountOfferForm(forms.Form):
    account_number = forms.CharField(max_length=255, label="Account Number")
    discount_offer = forms.ChoiceField(
        choices=[('50%', '50% Discount'), ('25%', '25% Discount'), ('10%', '10% Discount')],
        label="Discount Offer"
    )
    status = forms.ChoiceField(
        choices=[('blocked_offer', 'Blocked Offer'), ('inactive_offer', 'Inactive Offer')],
        label="Status"
    )
    ticket_number = forms.CharField(max_length=10, label="Ticket Number")
    region = forms.ChoiceField(
        choices=[('Nairobi', 'Nairobi'), ('Garissa', 'Garissa'), ('Wajir', 'Wajir'), ('Embu', 'Embu')],
        label="Region"
    )
    date_processed = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date Processed"
    )

    def clean_account_number(self):
        """Validate that account number starts with 'AFRIQ' and is followed by integers."""
        account_number = self.cleaned_data['account_number']
        if not account_number.startswith("AFRIQ"):
            raise forms.ValidationError("Account number must start with 'AFRIQ'.")
        if not account_number[5:].isdigit():
            raise forms.ValidationError("Account number must be followed by integers after 'AFRIQ'.")
        return account_number

    def clean(self):
        """Ensure account number is not used for both blocked_offer and inactive_offer."""
        cleaned_data = super().clean()
        account_number = cleaned_data.get('account_number')
        status = cleaned_data.get('status')

        if account_number and status:
            # Check if the account number already exists with a different status
            conflicting_offer = DiscountOffer.objects.filter(
                account_number=account_number
            ).exclude(status=status).exists()

            if conflicting_offer:
                raise forms.ValidationError(
                    "This account number cannot be used for both Blocked Offer and Inactive Offer."
                )

        return cleaned_data

    def clean_discount_offer(self):
        """Validate discount rules based on the status and sequential requirements."""
        discount_offer = self.cleaned_data['discount_offer']
        status = self.cleaned_data.get('status')
        account_number = self.cleaned_data.get('account_number')

        # Rule for blocked_offer
        if status == 'blocked_offer':
            if discount_offer != '50%':
                raise forms.ValidationError("Blocked Offer is only eligible for a 50% discount.")
            
            # Check if 50% discount has already been applied for this account
            already_applied = DiscountOffer.objects.filter(
                account_number=account_number, discount_offer='50%', status='blocked_offer'
            ).exists()
            if already_applied:
                raise forms.ValidationError("50% discount can only be applied once for a Blocked Offer.")

        # Rule for inactive_offer
        if status == 'inactive_offer':
            applied_discounts = DiscountOffer.objects.filter(account_number=account_number).values_list(
                'discount_offer', flat=True
            )
            required_sequence = ['50%', '25%', '10%']
            if len(applied_discounts) >= len(required_sequence):
                raise forms.ValidationError("This account has already applied for all available discounts.")
            next_discount = required_sequence[len(applied_discounts)]
            if discount_offer != next_discount:
                raise forms.ValidationError(
                    f"Discounts must be applied in this order: {', '.join(required_sequence)}. "
                    f"You must apply for the {next_discount} discount first."
                )

        return discount_offer

    def clean_ticket_number(self):
        """Validate that ticket number contains only integers."""
        ticket_number = self.cleaned_data['ticket_number']
        if not ticket_number.isdigit():
            raise forms.ValidationError("Ticket number must contain only integers.")
        return ticket_number

    def clean_date_processed(self):
        """Validate that the date processed is not in the future."""
        date_processed = self.cleaned_data['date_processed']
        if date_processed > date.today():
            raise forms.ValidationError("Date processed cannot be in the future.")
        return date_processed
