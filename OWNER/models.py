from django.db import models

# Create your models here.

class Owner(models.Model):
    username = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=255)

class CategoryOne(models.Model):
    GENDER_CHOICES = [
        ("bride", "Bride"),
        ("groom", "Groom"),
    ]
    name = models.CharField(max_length=100, unique=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    gender_type = models.CharField(max_length=10, choices=GENDER_CHOICES, default="bride")


class CategoryTwo(models.Model):
    GENDER_CHOICES = [
        ("bride", "Bride"),
        ("groom", "Groom"),
    ]
    category_1 = models.ForeignKey(
        CategoryOne,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100)
    image = models.CharField(max_length=255, blank=True, null=True)
    gender_type = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default="bride",
    )

    
class Section(models.Model):
    name = models.CharField(max_length=100, unique=True)
    rack_no = models.CharField(max_length=30, unique=True)
    
class Product(models.Model):

    name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=0)

    actual_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    offer_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    description = models.TextField()

    # Image paths / image URLs stored as text
    image_1 = models.CharField(max_length=255)
    image_2 = models.CharField(max_length=255, blank=True, null=True)
    image_3 = models.CharField(max_length=255, blank=True, null=True)

    category_1 = models.ForeignKey(
        CategoryOne,
        on_delete=models.PROTECT,
        
    )

    category_2 = models.ForeignKey(
        CategoryTwo,
        on_delete=models.PROTECT,
        
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
    )

    def rating(self):
        """Calculate average rating from user feedback; returns 0 if no feedback exists."""
        from USER.models import Feedback
        from django.db.models import Avg
        avg_rating = Feedback.objects.filter(product=self).aggregate(Avg('rating'))['rating__avg']
        return round(float(avg_rating), 1) if avg_rating is not None else 0

    def discount_pct(self):
        try:
            if self.actual_price and self.offer_price and self.offer_price < self.actual_price:
                return int(round((1 - float(self.offer_price) / float(self.actual_price)) * 100))
        except (ValueError, ZeroDivisionError):
            pass
        return 0

    def sizes(self):
        return ["XS", "S", "M", "L", "XL", "XXL"]



class Staff(models.Model):
    staff_name = models.CharField(max_length=200)

    username = models.CharField(
        max_length=150,
        unique=True
    )

    phone_no = models.CharField(
        max_length=15,
        unique=True
    )

    password = models.CharField(max_length=255,null=True)
    

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


class Offer(models.Model):
    OFFER_TYPES = [
        ("percentage", "Percentage Discount (%)"),
        ("fixed", "Fixed Discount (₹)"),
        ("category", "Category Special"),
        ("occasion", "Occasion Special"),
    ]
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPES, default="percentage")
    discount_value = models.DecimalField(max_digits=8, decimal_places=2, default=15.00)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"