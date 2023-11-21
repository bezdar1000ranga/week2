from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.urls import reverse
from django.core.exceptions import ValidationError
import os

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)




class Category(models.Model):
    title = models.CharField(max_length=100)
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'pk': self.pk})
    

class CatalogRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'Принято в работу'),
        ('completed', 'Выполнено'),
    ]
    
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    comment = models.TextField(null=True, blank=True)
    image_after = models.ImageField(upload_to='images', null=True, blank=True)
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > 2 * 1024 * 1024:
            raise ValidationError("Размер изображения не должен превышать 2 МБ")
        
        ext = os.path.splitext(image.name)[1]
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        
        if not ext.lower() in valid_extensions:
            raise ValidationError("Неподдерживаемый формат изображения. Поддерживаемые форматы: JPG, JPEG, PNG, BMP")
        try:
            with Image.open(image) as img:
                pass
        except:
            raise ValidationError("Невозможно открыть изображение. Проверьте, что файл является изображением")
        
        return image
    

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('catalog_request_detail', kwargs={'pk': self.pk})