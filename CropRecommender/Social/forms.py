# Created by @Keyo to include the logic behid the form
from django import forms #Custom forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Post #importing the custom table that stores users and posts
from django.core.exceptions import ValidationError #For validations i.e password

# Function to validate the password entered by the user in SignUp form
def validatePassword(value):
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if value.isdigit():
        raise ValidationError("Password cannot be entirely numeric.")


class SignUpForm(UserCreationForm):
    county = forms.CharField(max_length=100)
    phoneNo = forms.CharField(max_length=15)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'input-field'}), 
        help_text='', #removes the default django's help text
        validators=[validatePassword]  # Custom validation for password
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'input-field'}),
        help_text='',  # Removes default help text
    )
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
        help_texts = { 'username': '',}# Removes default help text for username
        
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                county=self.cleaned_data['county'],
                phoneNo=self.cleaned_data['phoneNo'],
                role=self.cleaned_data['role']
            )
        return user

# Post creation
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']