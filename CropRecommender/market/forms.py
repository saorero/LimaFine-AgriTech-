# Handles the listig forms and any other form created
# farmers/forms.py
from django import forms
from .models import productListing, ProductRequest
# from .utils import checkContent 
class ListingForm(forms.ModelForm):
    class Meta:
        model = productListing
        fields = [ "productCategory","productName", "quantity", "unit", "price", "description", "location", "image"]
        widgets = {
            'location': forms.TextInput(attrs={'placeholder': 'Farmers definedd county if left blank'}),
            'productCategory': forms.Select(),  # Renders as a dropdown
        }
    # Validating the fields to see if they have agricultural content
    def clean(self):
        cleaned_data = super().clean()
        product_name = cleaned_data.get('productName', '').strip()
        description = cleaned_data.get('description', '').strip()

        # if not checkContent(product_name):
        #     raise forms.ValidationError({"productName": "Product name does not seem related to agriculture. Please edit."})

        # if not checkContent(description):
        #     raise forms.ValidationError({"description": "Description does not seem related to agriculture. Please edit."})

        return cleaned_data


