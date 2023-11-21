from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Profile
import re
from .models import CatalogRequest, Category

class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(label='Full_name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Full name'}), required=True)
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    agree_to_process_personal_data = forms.BooleanField(label='Verify edit your personal information', required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        
        if not re.match('^[а-яА-ЯёЁ\s-]+$', full_name):
            raise ValidationError(_('Full name can use Russian'))
        
        return full_name

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        if not all(char.isalnum() or char == '-' for char in username):
            raise ValidationError(_('Login can be only eng and -'))
        
        if User.objects.filter(username=username).exists():
            raise ValidationError(_('Already used'))
        
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Already used'))
        
        return email

    def clean_agree_to_process_personal_data(self):
        agree_to_process_personal_data = self.cleaned_data.get('agree_to_process_personal_data')
        
        if not agree_to_process_personal_data:
            raise ValidationError(_('Verify edit your personal information'))
        
        return agree_to_process_personal_data
    

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']




        
class CatalogRequestForm(forms.ModelForm):
    class Meta:
        model = CatalogRequest
        exclude = ['user']
        fields = ['title', 'content', 'image', 'category', 'status', 'comment', 'image_after']
        labels = {
            "status": "Статус",
            "title": "Название",
            "content": "Содержание",
            "image": "Изображение",
            "category": "Категория",
            "comment": "Комментарий",
            "image_after": "Изображение после работы"
        }
        widgets = {
            "category": forms.Select(attrs={'class': "form-control"}),
            "comment": forms.Textarea(attrs={'class': "form-control"}),
            "status": forms.Select(attrs={'class': "form-control"}),
        }
    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["title"]
        labels = {
            "title": "Название категории"
        }
