from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

from .models import Post, Category, Comment, ContactMessage, Newsletter


class ContactForm(forms.Form):
    """نموذج التواصل"""
    name = forms.CharField(
        label=_("الاسم"),
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل اسمك'
        })
    )
    email = forms.EmailField(
        label=_("البريد الإلكتروني"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل بريدك الإلكتروني',
            'dir': 'ltr'
        })
    )
    subject = forms.CharField(
        label=_("الموضوع"),
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل موضوع الرسالة'
        })
    )
    message = forms.CharField(
        label=_("الرسالة"),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'أدخل رسالتك'
        })
    )
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name.strip()) < 2:
            raise ValidationError(_("الاسم يجب أن يكون حرفين على الأقل."))
        return name.strip()
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message.strip()) < 10:
            raise ValidationError(_("الرسالة يجب أن تكون 10 أحرف على الأقل."))
        return message.strip()


class NewsletterForm(forms.Form):
    """نموذج الاشتراك في النشرة الإخبارية"""
    email = forms.EmailField(
        label=_("البريد الإلكتروني"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل بريدك الإلكتروني',
            'dir': 'ltr'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Newsletter.objects.filter(email=email, is_active=True).exists():
            raise ValidationError(_("أنت مشترك بالفعل في النشرة الإخبارية."))
        return email


class PostForm(forms.ModelForm):
    """نموذج المنشور"""
    class Meta:
        model = Post
        fields = ['title', 'content', 'excerpt', 'category', 'featured_image', 'status', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل عنوان المنشور'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'أدخل محتوى المنشور'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أدخل ملخص المنشور'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class CommentForm(forms.ModelForm):
    """نموذج التعليق"""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أدخل تعليقك'
            })
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 5:
            raise ValidationError(_("التعليق يجب أن يكون 5 أحرف على الأقل."))
        return content.strip()


class CategoryForm(forms.ModelForm):
    """نموذج الفئة"""
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'color', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم الفئة'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أدخل وصف الفئة'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل أيقونة الفئة'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
