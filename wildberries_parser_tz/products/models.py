from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    rating = models.FloatField(null=True)
    reviews_count = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    wb_id = models.BigIntegerField(unique=True)

    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['price']),
            models.Index(fields=['rating']),
            models.Index(fields=['reviews_count']),
            models.Index(fields=['created_at']),
        ]
