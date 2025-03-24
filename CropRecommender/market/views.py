# farmers/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import productListing
from .forms import ListingForm
from Social.models import UserProfile

# Filters out to only allow farmers access specific pages Decorator
def farmer_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            # Retrieves user profile
            profile = request.user.userprofile
            if profile.role != 'farmer':
                return HttpResponseForbidden("Only farmers can access this page.")
        except UserProfile.DoesNotExist:
            return HttpResponseForbidden("User profile not found. Please complete your profile.")
        return view_func(request, *args, **kwargs)
    return wrapper

@farmer_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(productListing, id=listing_id, farmer=request.user.userprofile)
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            if 'clear_image' in request.POST and not request.FILES.get('image'):
                listing.image.delete()
                listing.image = None
            form.save()
            return redirect("main")
    # If not a POST request, we don't need to render a separate template since the form is in the modal
    return redirect("main")

@farmer_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(productListing, id=listing_id, farmer=request.user.userprofile)
    if request.method == "POST":
        listing.delete()
        return redirect("main")
    # If not a POST request, we don't need to render a separate template since the confirmation is in the modal
    return redirect("main")

@farmer_required
def toggle_availability(request, listing_id):
    listing = get_object_or_404(productListing, id=listing_id, farmer=request.user.userprofile)
    if request.method == "POST":
        listing.is_available = not listing.is_available
        listing.save()
    return redirect("main")

@farmer_required
def main(request):
    # Handle product listing creation
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.farmer = request.user.userprofile
            listing.save()
            # Redirect to the same page with a query parameter to show the dashboard
            return redirect("main")
    else:
        form = ListingForm(initial={'location': request.user.userprofile.county})

    # Fetch listings for the dashboard
    listings = productListing.objects.filter(farmer=request.user.userprofile)

    # Search Logic by product name or category
    query = request.GET.get('query', '').strip()
    if query:
        listings = listings.filter(productName__icontains=query) #partial matching cases
   #end of SEARCH LOGIC

    # Pass both the form and listings to the template
    context = {
        'message': 'Market Place',
        'form': form,
        'listings': listings,
    }
    return render(request, 'market.html', context)


