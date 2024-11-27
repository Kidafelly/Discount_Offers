from django.db import models

class DiscountOffer(models.Model):
    account_number = models.CharField(max_length=255)
    discount_offer = models.CharField(max_length=10)
    ticket_number = models.CharField(max_length=10)
    region = models.CharField(max_length=50)
    date_processed = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[('blocked_offer', 'Blocked Offer'), ('inactive_offer', 'Inactive Offer')],
        default='inactive_offer'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['account_number', 'discount_offer', 'status'],
                name='unique_blocked_offer_discount'
            )
        ]

    def __str__(self):
        return f"{self.account_number} - {self.discount_offer} - {self.status}"
