from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """نموذج إنشاء مستخدم مخصص"""
    email = forms.EmailField(
        label=_("البريد الإلكتروني"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل بريدك الإلكتروني',
            'dir': 'ltr'
        })
    )
    first_name = forms.CharField(
        label=_("الاسم الأول"),
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل اسمك الأول'
        })
    )
    last_name = forms.CharField(
        label=_("اسم العائلة"),
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل اسم العائلة'
        })
    )
    phone = forms.CharField(
        label=_("رقم الهاتف"),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل رقم هاتفك',
            'dir': 'ltr'
        })
    )
    password1 = forms.CharField(
        label=_("كلمة المرور"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور'
        })
    )
    password2 = forms.CharField(
        label=_("تأكيد كلمة المرور"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أكد كلمة المرور'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'أدخل اسم المستخدم',
            'dir': 'ltr'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # لا نكشف عن وجود البريد لتجنب enumeration لكن نمنع التكرار فعلياً
        if not email:
            return email

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("لا يمكن استخدام هذا البريد الإلكتروني."))

        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # تحقق من صحة رقم الهاتف
            phone_pattern = r'^(\+966|0)?[5-9][0-9]{8}$'
            if not re.match(phone_pattern, phone):
                raise ValidationError(_("رقم الهاتف غير صحيح. يجب أن يبدأ بـ 05 أو 5."))
        return phone


class CustomAuthenticationForm(AuthenticationForm):
    """نموذج تسجيل الدخول المخصص"""
    username = forms.EmailField(
        label=_("البريد الإلكتروني"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل بريدك الإلكتروني',
            'dir': 'ltr',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label=_("كلمة المرور"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور'
        })
    )
    remember_me = forms.BooleanField(
        label=_("تذكرني"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class PasswordResetForm(forms.Form):
    """نموذج إعادة تعيين كلمة المرور"""
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
        if not User.objects.filter(email=email, is_active=True).exists():
            raise ValidationError(_("لا يوجد حساب مرتبط بهذا البريد الإلكتروني."))
        return email


class PasswordResetConfirmForm(forms.Form):
    """نموذج تأكيد إعادة تعيين كلمة المرور"""
    new_password1 = forms.CharField(
        label=_("كلمة المرور الجديدة"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور الجديدة'
        })
    )
    new_password2 = forms.CharField(
        label=_("تأكيد كلمة المرور الجديدة"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أكد كلمة المرور الجديدة'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(_("كلمتا المرور غير متطابقتين."))
            
            # تحقق من قوة كلمة المرور
            if len(password1) < 8:
                raise ValidationError(_("كلمة المرور يجب أن تكون 8 أحرف على الأقل."))
            
            if not re.search(r'[A-Za-z]', password1):
                raise ValidationError(_("كلمة المرور يجب أن تحتوي على حرف واحد على الأقل."))
            
            if not re.search(r'[0-9]', password1):
                raise ValidationError(_("كلمة المرور يجب أن تحتوي على رقم واحد على الأقل."))
        
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """نموذج تحديث الملف الشخصي"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'avatar', 'birth_date', 'address')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسمك الأول'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم العائلة'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل بريدك الإلكتروني',
                'dir': 'ltr'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل رقم هاتفك',
                'dir': 'ltr'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أدخل عنوانك'
            }),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if not avatar:
            return avatar
        max_size = 2 * 1024 * 1024
        if hasattr(avatar, 'size') and avatar.size > max_size:
            raise ValidationError(_('حجم الصورة يجب ألا يتجاوز 2MB.'))
        content_type = getattr(avatar, 'content_type', '') or ''
        if content_type and not content_type.startswith('image/'):
            raise ValidationError(_('يجب أن يكون الملف صورة.'))
        valid_ext = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        name_lower = getattr(avatar, 'name', '').lower()
        if name_lower and not any(name_lower.endswith(ext) for ext in valid_ext):
            raise ValidationError(_('امتداد الصورة غير مدعوم.'))
        return avatar
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_("هذا البريد الإلكتروني مستخدم بالفعل."))
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone_pattern = r'^(\+966|0)?[5-9][0-9]{8}$'
            if not re.match(phone_pattern, phone):
                raise ValidationError(_("رقم الهاتف غير صحيح. يجب أن يبدأ بـ 05 أو 5."))
        return phone


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
        from main.models import Newsletter
        if Newsletter.objects.filter(email=email, is_active=True).exists():
            raise ValidationError(_("أنت مشترك بالفعل في النشرة الإخبارية."))
        return email

