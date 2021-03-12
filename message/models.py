from django.db import models

def product_photos_dir(instanse, filename):
    # usrnme = f'{instanse.name}'
    folder_name = f"message/{filename}"
    return folder_name

class Message(models.Model):
    title = models.CharField(max_length=250)
    text = models.TextField()
    photo = models.ImageField(upload_to=product_photos_dir, default="default/default.png", null=True, blank=True)

    def __str__(self):
        return self.title
    