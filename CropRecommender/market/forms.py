# Handles the listig forms and any other form created
# farmers/forms.py
from django import forms
from .models import productListing

class ListingForm(forms.ModelForm):
    class Meta:
        model = productListing
        fields = [ "productCategory","productName", "quantity", "unit", "price", "description", "location", "image"]
        widgets = {
            'location': forms.TextInput(attrs={'placeholder': 'Farmers definedd county if left blank'}),
            'productCategory': forms.Select(),  # Renders as a dropdown
        }