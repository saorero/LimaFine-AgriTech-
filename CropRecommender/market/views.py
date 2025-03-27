# VIEWS.PY
# farmers/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from .models import productListing, Message
from .forms import ListingForm
from Social.models import UserProfile
from django.db.models import Q
import json
def farmer_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
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
    return redirect("main")

@farmer_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(productListing, id=listing_id, farmer=request.user.userprofile)
    if request.method == "POST":
        listing.delete()
        return redirect("main")
    return redirect("main")

@farmer_required
def toggle_availability(request, listing_id):
    listing = get_object_or_404(productListing, id=listing_id, farmer=request.user.userprofile)
    if request.method == "POST":
        listing.is_available = not listing.is_available
        listing.save()
    return redirect("main")

# 25/04
@login_required
def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        listing_id = data.get('listing_id')
        recipient_id = data.get('recipient_id')
        content = data.get('content').strip()

        print("Sending message")
        print(f"Sending message: listing_id={listing_id}, recipient_id={recipient_id}, content={content}")  # Debug

        if not content:
            return JsonResponse({'status': 'error', 'message': 'Message content cannot be empty'}, status=400)

        listing = get_object_or_404(productListing, id=listing_id)
        recipient = get_object_or_404(UserProfile, id=recipient_id)
        sender = request.user.userprofile

        print(f"Sender: {sender.user.username}, Recipient: {recipient.user.username}")  # Debug

        message = Message.objects.create(
            sender=sender,
            recipient=recipient,
            listing=listing,
            content=content
        )
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'content': message.content,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'sender': sender.user.username,
                'is_sender': True
            }
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)




@login_required
def get_conversations(request):
    user_profile = request.user.userprofile
    print(f"User: {user_profile.user.username}, Role: {user_profile.role}")  # Debug

    # Fetch messages where the user is either sender or recipient
    messages = Message.objects.filter(
        Q(sender=user_profile) | Q(recipient=user_profile)
    ).order_by('-timestamp')

    # Create a dictionary to store unique conversations
    conversation_dict = {}
    for msg in messages:
        # Create a unique key for the conversation (listing + other user)
        other_user = msg.sender if msg.recipient == user_profile else msg.recipient
        convo_key = f"{msg.listing.id}-{other_user.id}"

        if convo_key not in conversation_dict:
            conversation_dict[convo_key] = {
                'listing': msg.listing,
                'other_user': other_user,
                'last_message': msg
            }

    # Convert the dictionary to a list for the response
    conversation_list = []
    for convo in conversation_dict.values():
        listing = convo['listing']
        other_profile = convo['other_user']
        last_message = convo['last_message']

        conversation_list.append({
            'listing_id': listing.id,
            'listing_name': listing.productName,
            'listing_image': listing.get_image_url(),
            'other_user': other_profile.user.username,
            'other_user_id': other_profile.id,
            'last_message': last_message.content,
            'timestamp': last_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'unread': Message.objects.filter(
                listing=listing, recipient=user_profile, sender=other_profile, is_read=False
            ).exists()
        })

    return JsonResponse({'conversations': conversation_list})



@login_required
def get_messages(request, listing_id, other_user_id):
    user_profile = request.user.userprofile
    listing = get_object_or_404(productListing, id=listing_id)
    other_profile = get_object_or_404(UserProfile, id=other_user_id)

    messages = Message.objects.filter(
        listing=listing,
        sender__in=[user_profile, other_profile],
        recipient__in=[user_profile, other_profile]
    ).order_by('timestamp')

    # Mark messages as read
    Message.objects.filter(
        listing=listing, recipient=user_profile, sender=other_profile, is_read=False
    ).update(is_read=True)

    messages_data = [{
        'id': msg.id,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'is_sender': msg.sender == user_profile,
        'sender': msg.sender.user.username
    } for msg in messages]

    return JsonResponse({
        'listing_name': listing.productName,
        'listing_image': listing.get_image_url(),
        'other_user': other_profile.user.username,
        'messages': messages_data
    })
# 25/04

@login_required
def main(request):
    form = None
    listings = None
    marketplace_listings = productListing.objects.all()

    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("User profile not found. Please complete your profile.")

    if user_profile.role == 'farmer':
        if request.method == "POST":
            form = ListingForm(request.POST, request.FILES)
            if form.is_valid():
                listing = form.save(commit=False)
                listing.farmer = user_profile
                listing.save()
                return redirect("main")
        else:
            form = ListingForm(initial={'location': user_profile.county})
        listings = productListing.objects.filter(farmer=user_profile)
        query = request.GET.get('query', '').strip()
        if query:
            listings = listings.filter(productName__icontains=query)
        marketplace_listings = marketplace_listings.exclude(farmer=user_profile)

    marketplace_query = request.GET.get('marketplace_query', '').strip()
    if marketplace_query:
        marketplace_listings = marketplace_listings.filter(productName__icontains=marketplace_query)

    context = {
        'message': 'Market Place',
        'form': form,
        'listings': listings,
        'marketplace_listings': marketplace_listings,
    }
    return render(request, 'market.html', context)

