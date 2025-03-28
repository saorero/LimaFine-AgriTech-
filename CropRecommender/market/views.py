# VIEWS.PY
# farmers/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from .models import productListing, Message, ProductRequest
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
def editListing(request, listing_id):
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
def deleteListing(request, listing_id):
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


# 28 MODIFICATIONS
@login_required
def sendMessage(request):
    if request.method == "POST":
        data = json.loads(request.body)
        listing_id = data.get('listing_id')  # Can be 'none', None, or an integer
        recipient_id = data.get('recipient_id')
        content = data.get('content').strip()

        print("Sending message")
        print(f"Sending message: listing_id={listing_id}, recipient_id={recipient_id}, content={content}")

        if not content:
            return JsonResponse({'status': 'error', 'message': 'Message content cannot be empty'}, status=400)

        # Handle listing_id
        listing = None
        if listing_id and listing_id != 'none':  # Only fetch if it's not 'none' or None
            listing = get_object_or_404(productListing, id=listing_id)

        recipient = get_object_or_404(UserProfile, id=recipient_id)
        sender = request.user.userprofile

        print(f"Sender: {sender.user.username}, Recipient: {recipient.user.username}")

        message = Message.objects.create(
            sender=sender,
            recipient=recipient,
            listing=listing,  # Will be None for product requests
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
def getMessages(request, listing_id, other_user_id):
    user_profile = request.user.userprofile
    other_profile = get_object_or_404(UserProfile, id=other_user_id)

    # Treat 'none', 'null', or empty string as no listing
    if listing_id in ('none', 'null', ''):
        messages = Message.objects.filter(
            Q(sender=user_profile, recipient=other_profile) | Q(sender=other_profile, recipient=user_profile),
            listing__isnull=True
        ).order_by('timestamp')
        listing_name = "Product Request"
        listing_image = ''
    else:
        listing = get_object_or_404(productListing, id=listing_id)
        messages = Message.objects.filter(
            Q(sender=user_profile, recipient=other_profile) | Q(sender=other_profile, recipient=user_profile),
            listing=listing
        ).order_by('timestamp')
        listing_name = listing.productName
        listing_image = listing.get_image_url()

    messages_data = [
        {
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sender': msg.sender.user.username,
            'is_sender': msg.sender == user_profile
        } for msg in messages
    ]

    Message.objects.filter(recipient=user_profile, sender=other_profile, is_read=False).update(is_read=True)

    return JsonResponse({
        'listing_name': listing_name,
        'listing_image': listing_image,
        'other_user': other_profile.user.username,
        'messages': messages_data
    })



# @login_required
def getConversations(request):
    user_profile = request.user.userprofile
    print(f"User: {user_profile.user.username}, Role: {user_profile.role}")

    messages = Message.objects.filter(
        Q(sender=user_profile) | Q(recipient=user_profile)
    ).order_by('-timestamp')

    conversation_dict = {}
    for msg in messages:
        other_user = msg.sender if msg.recipient == user_profile else msg.recipient
        listing_id = msg.listing.id if msg.listing else 'none'
        convo_key = f"{listing_id}-{other_user.id}"

        if convo_key not in conversation_dict:
            conversation_dict[convo_key] = {
                'listing': msg.listing,
                'other_user': other_user,
                'last_message': msg
            }

    conversation_list = [
        {
            'listing_id': convo['listing'].id if convo['listing'] else None,
            'listing_name': convo['listing'].productName if convo['listing'] else "Product Request",
            'listing_image': convo['listing'].get_image_url() if convo['listing'] else '',
            'other_user': convo['other_user'].user.username,
            'other_user_id': convo['other_user'].id,
            'last_message': convo['last_message'].content,
            'timestamp': convo['last_message'].timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'unread': Message.objects.filter(
                listing=convo['listing'],
                recipient=user_profile,
                sender=convo['other_user'],
                is_read=False
            ).exists()
        } for convo in conversation_dict.values()
    ]

    return JsonResponse({'conversations': conversation_list})


# # END OF 28 MODIFICATIONS

# 25/04 MESSAGING ORIGINAL
# @login_required
# def sendMessage(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         listing_id = data.get('listing_id')  # Can be None
#         recipient_id = data.get('recipient_id')
#         content = data.get('content').strip()

#         print("Sending message")
#         print(f"Sending message: listing_id={listing_id}, recipient_id={recipient_id}, content={content}")

#         if not content:
#             return JsonResponse({'status': 'error', 'message': 'Message content cannot be empty'}, status=400)

#         # Handle listing_id being None
#         listing = None
#         if listing_id:
#             listing = get_object_or_404(productListing, id=listing_id)

#         recipient = get_object_or_404(UserProfile, id=recipient_id)
#         sender = request.user.userprofile

#         print(f"Sender: {sender.user.username}, Recipient: {recipient.user.username}")

#         message = Message.objects.create(
#             sender=sender,
#             recipient=recipient,
#             listing=listing,  # Can be None for product requests
#             content=content
#         )
#         return JsonResponse({
#             'status': 'success',
#             'message': {
#                 'id': message.id,
#                 'content': message.content,
#                 'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
#                 'sender': sender.user.username,
#                 'is_sender': True
#             }
#         })
#     return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# COMMENTED OUT ON 28 the original i had by morning
# @login_required
# def getConversations(request):
#     user_profile = request.user.userprofile
#     print(f"User: {user_profile.user.username}, Role: {user_profile.role}")

#     # Fetch messages where the user is either sender or recipient
#     messages = Message.objects.filter(
#         Q(sender=user_profile) | Q(recipient=user_profile)
#     ).order_by('-timestamp')

#     # Create a dictionary to store unique conversations
#     conversation_dict = {}
#     for msg in messages:
#         other_user = msg.sender if msg.recipient == user_profile else msg.recipient
#         # Use listing_id or 'none' if no listing, combined with other_user.id
#         listing_id = msg.listing.id if msg.listing else 'none'
#         convo_key = f"{listing_id}-{other_user.id}"

#         if convo_key not in conversation_dict:
#             conversation_dict[convo_key] = {
#                 'listing': msg.listing,
#                 'other_user': other_user,
#                 'last_message': msg
#             }

#     # Convert to list for response
#     conversation_list = []
#     for convo in conversation_dict.values():
#         listing = convo['listing']
#         other_profile = convo['other_user']
#         last_message = convo['last_message']

#         conversation_list.append({
#             'listing_id': listing.id if listing else None,
#             'listing_name': listing.productName if listing else "Product Request",
#             'listing_image': listing.get_image_url() if listing else '',  # Empty string if no listing
#             'other_user': other_profile.user.username,
#             'other_user_id': other_profile.id,
#             'last_message': last_message.content,
#             'timestamp': last_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
#             'unread': Message.objects.filter(
#                 listing=listing,  # Works with None too
#                 recipient=user_profile,
#                 sender=other_profile,
#                 is_read=False
#             ).exists()
#         })

#     return JsonResponse({'conversations': conversation_list})

# @login_required
# def getMessages(request, listing_id, other_user_id):
#     user_profile = request.user.userprofile
#     other_profile = get_object_or_404(UserProfile, id=other_user_id)

#     # If listing_id is 'none', fetch messages without a listing
#     if listing_id == 'none':
#         messages = Message.objects.filter(
#             Q(sender=user_profile, recipient=other_profile) | Q(sender=other_profile, recipient=user_profile),
#             listing__isnull=True
#         ).order_by('timestamp')
#     else:
#         listing = get_object_or_404(productListing, id=listing_id)
#         messages = Message.objects.filter(
#             Q(sender=user_profile, recipient=other_profile) | Q(sender=other_profile, recipient=user_profile),
#             listing=listing
#         ).order_by('timestamp')

#     messages_data = []
#     for msg in messages:
#         messages_data.append({
#             'id': msg.id,
#             'content': msg.content,
#             'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
#             'sender': msg.sender.user.username,
#             'is_sender': msg.sender == user_profile
#         })

#     # Mark messages as read
#     Message.objects.filter(recipient=user_profile, sender=other_profile, is_read=False).update(is_read=True)

#     return JsonResponse({
#         'listing_name': listing.productName if listing_id != 'none' else "Product Request",
#         'listing_image': listing.get_image_url() if listing_id != 'none' else '',
#         'other_user': other_profile.user.username,
#         'messages': messages_data
#     })

# COMMENTED OUT ON 28 the original i had by morning


# COMMENTED OUT ON 27 first original series
# def sendMessage(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         listing_id = data.get('listing_id')
#         recipient_id = data.get('recipient_id')
#         content = data.get('content').strip()

#         print("Sending message")
#         print(f"Sending message: listing_id={listing_id}, recipient_id={recipient_id}, content={content}")  # Debug

#         if not content:
#             return JsonResponse({'status': 'error', 'message': 'Message content cannot be empty'}, status=400)

#         listing = get_object_or_404(productListing, id=listing_id)
#         recipient = get_object_or_404(UserProfile, id=recipient_id)
#         sender = request.user.userprofile

#         print(f"Sender: {sender.user.username}, Recipient: {recipient.user.username}")  # Debug

#         message = Message.objects.create(
#             sender=sender,
#             recipient=recipient,
#             listing=listing,
#             content=content
#         )
#         return JsonResponse({
#             'status': 'success',
#             'message': {
#                 'id': message.id,
#                 'content': message.content,
#                 'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
#                 'sender': sender.user.username,
#                 'is_sender': True
#             }
#         })
#     return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# @login_required
# def getConversations(request):
#     user_profile = request.user.userprofile
#     print(f"User: {user_profile.user.username}, Role: {user_profile.role}")  # Debug

#     # Fetch messages where the user is either sender or recipient
#     messages = Message.objects.filter(
#         Q(sender=user_profile) | Q(recipient=user_profile)
#     ).order_by('-timestamp')

#     # Create a dictionary to store unique conversations
#     conversation_dict = {}
#     for msg in messages:
#         # Create a unique key for the conversation (listing + other user)
#         other_user = msg.sender if msg.recipient == user_profile else msg.recipient
#         convo_key = f"{msg.listing.id}-{other_user.id}"

#         if convo_key not in conversation_dict:
#             conversation_dict[convo_key] = {
#                 'listing': msg.listing,
#                 'other_user': other_user,
#                 'last_message': msg
#             }

#     # Convert the dictionary to a list for the response
#     conversation_list = []
#     for convo in conversation_dict.values():
#         listing = convo['listing']
#         other_profile = convo['other_user']
#         last_message = convo['last_message']

#         conversation_list.append({
#             'listing_id': listing.id,
#             'listing_name': listing.productName,
#             'listing_image': listing.get_image_url(),
#             'other_user': other_profile.user.username,
#             'other_user_id': other_profile.id,
#             'last_message': last_message.content,
#             'timestamp': last_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
#             'unread': Message.objects.filter(
#                 listing=listing, recipient=user_profile, sender=other_profile, is_read=False
#             ).exists()
#         })

#     return JsonResponse({'conversations': conversation_list})


# @login_required
# def getMessages(request, listing_id, other_user_id):
#     user_profile = request.user.userprofile
#     listing = get_object_or_404(productListing, id=listing_id)
#     other_profile = get_object_or_404(UserProfile, id=other_user_id)

#     messages = Message.objects.filter(
#         listing=listing,
#         sender__in=[user_profile, other_profile],
#         recipient__in=[user_profile, other_profile]
#     ).order_by('timestamp')

#     # Mark messages as read
#     Message.objects.filter(
#         listing=listing, recipient=user_profile, sender=other_profile, is_read=False
#     ).update(is_read=True)

#     messages_data = [{
#         'id': msg.id,
#         'content': msg.content,
#         'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
#         'is_sender': msg.sender == user_profile,
#         'sender': msg.sender.user.username
#     } for msg in messages]

#     return JsonResponse({
#         'listing_name': listing.productName,
#         'listing_image': listing.get_image_url(),
#         'other_user': other_profile.user.username,
#         'messages': messages_data
#     })
# END OF MESSAGING

#REQUESTS START VIEWS 27/03

@login_required
def create_product_request(request):
    
    if request.method == "POST":
        data = json.loads(request.body)
        product_name = data.get('product_name').strip()
        quantity = float(data.get('quantity', 0))
        unit = data.get('unit', 'kg').strip()
        description = data.get('description', '').strip()
        location = data.get('location').strip()
        print(f"Creating request: {product_name}, {quantity}, {unit}, {description}, {location}")  # Debug
        if not product_name or quantity <= 0 or not location:
            return JsonResponse({'status': 'error', 'message': 'Product name, quantity, and location are required.'}, status=400)

        requester = request.user.userprofile
        product_request = ProductRequest.objects.create(
            requester=requester,
            product_name=product_name,
            quantity=quantity,
            unit=unit,
            description=description,
            location=location
        )
        return JsonResponse({
            'status': 'success',
            'request': {
                'id': product_request.id,
                'product_name': product_request.product_name,
                'quantity': product_request.quantity,
                'unit': product_request.unit,
                'description': product_request.description,
                'location': product_request.location,
                'created_at': product_request.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def edit_product_request(request, request_id):
    product_request = get_object_or_404(ProductRequest, id=request_id, requester=request.user.userprofile)
    if request.method == "POST":
        data = json.loads(request.body)
        product_request.product_name = data.get('product_name', product_request.product_name).strip()
        product_request.quantity = float(data.get('quantity', product_request.quantity))
        product_request.unit = data.get('unit', product_request.unit).strip()
        product_request.description = data.get('description', product_request.description).strip()
        product_request.location = data.get('location', product_request.location).strip()
        product_request.save()
        return JsonResponse({'status': 'success', 'message': 'Request updated successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def delete_product_request(request, request_id):
    product_request = get_object_or_404(ProductRequest, id=request_id, requester=request.user.userprofile)
    if request.method == "POST":
        product_request.delete()
        return JsonResponse({'status': 'success', 'message': 'Request deleted successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# Function to filter out Requests based on the logged in user
@login_required
def get_my_requests(request):
    user_profile = request.user.userprofile
    requests = ProductRequest.objects.filter(requester=user_profile, is_active=True).order_by('-created_at')
    requests_data = [{
        'id': req.id,
        'product_name': req.product_name,
        'quantity': req.quantity,
        'unit': req.unit,
        'description': req.description,
        'location': req.location,
        'created_at': req.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for req in requests]
    return JsonResponse({'requests': requests_data})

@login_required
def get_product_requests(request):
    if request.user.userprofile.role != 'farmer':
        return JsonResponse({'requests': []})  # Non-farmers see nothing
    requests = ProductRequest.objects.filter(is_active=True).exclude(requester=request.user.userprofile).order_by('-created_at')
    requests_data = [{
        'id': req.id,
        'product_name': req.product_name,
        'quantity': req.quantity,
        'unit': req.unit,
        'description': req.description,
        'location': req.location,
        'requester': req.requester.user.username,
        'requester_id': req.requester.id,
        'created_at': req.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for req in requests]
    return JsonResponse({'requests': requests_data})

# END OF REQUEST VIEWS


# 25/04
@login_required
def main(request):
    form = None
    listings = None
    marketplace_listings = productListing.objects.all()
    my_requests = ProductRequest.objects.filter(requester=request.user.userprofile, is_active=True)
    product_requests = ProductRequest.objects.filter(is_active=True).exclude(requester=request.user.userprofile) if request.user.userprofile.role == 'farmer' else []

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
        'my_requests': my_requests,
        'product_requests': product_requests,
    }
    return render(request, 'market.html', context)

