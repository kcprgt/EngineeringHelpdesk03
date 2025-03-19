from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import Department

CustomUser = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'department', 'password1', 'password2']  # Fields to display in the form

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.department = self.cleaned_data['department']
        if commit:
            user.save()
        return user