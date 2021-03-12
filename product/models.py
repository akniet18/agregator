from django.db import models


class Pharmacy(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    working_hours = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=150)
    owner = models.ForeignKey('users.User',on_delete=models.CASCADE, null=True, blank=True, related_name="my_pharmacy")

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField()
    rating = models.FloatField(null=True, blank=True)
    author = models.ForeignKey("users.User", on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    def __str__(self):
        return self.pharmacy.name


class Manufacture(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


def product_photos_dir(instanse, filename):
    usrnme = f'{instanse.name}'
    folder_name = f"{usrnme}/{filename}"
    return folder_name


class Product(models.Model):
    name = models.CharField(max_length=150)
    manufacturer = models.ForeignKey(Manufacture, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to=product_photos_dir, default="default/default.png", null=True, blank=True)
    composition = models.TextField(null=True, blank=True)
    category = models.ForeignKey("categories.Category", on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.name


class CountProduct(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name="available")
    count = models.BigIntegerField(null=True, blank=True)
    price = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.product.name + " " + self.pharmacy.name