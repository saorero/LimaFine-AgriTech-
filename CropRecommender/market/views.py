# VIEWS.PY
# farmers/views.pyy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import productListing, Message, ProductRequest, Order 
from .forms import ListingForm
from Social.models import UserProfile
from django.db.models import Q
import json
from django.contrib import messages
# from .utils import checkContent #confirms what is entered is valid
from django.utils.timezone import localtime

# Route optimizations
import requests
from django.conf import settings
import logging
# Set up logging
logger = logging.getLogger(__name__)

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
def optimize_delivery_route(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    user_profile = request.user.userprofile
    logger.debug(f"Optimizing delivery routes for farmer: {user_profile.user.username}")

    # Get pending or confirmed delivery orders
    orders = Order.objects.filter(
        listing__farmer=user_profile,
        status__in=['pending', 'confirmed'],
        deliveryMode='delivery'
    ).exclude(latitude__isnull=True, longitude__isnull=True).select_related('listing')

    if not orders:
        logger.warning("No valid delivery orders found for route optimization")
        return JsonResponse({
            'status': 'error',
            'message': 'No valid delivery orders found. Ensure orders have status "pending" or "confirmed", delivery mode "delivery", and valid latitude/longitude.'
        }, status=400)

    # Group orders by listing
    orders_by_listing = {}
    for order in orders:
        listing_id = order.listing.id
        if listing_id not in orders_by_listing:
            orders_by_listing[listing_id] = {
                'listing': order.listing,
                'orders': []
            }
        orders_by_listing[listing_id]['orders'].append(order)

    logger.debug(f"Grouped orders into {len(orders_by_listing)} listings")

    # Optimize a route for each listing
    routes = []
    api_key = settings.GOOGLE_MAPS_API_KEY
    url = "https://maps.googleapis.com/maps/api/directions/json"

    for listing_id, data in orders_by_listing.items():
        listing = data['listing']
        listing_orders = data['orders']

        # Skip listings without valid coordinates
        if listing.latitude is None or listing.longitude is None:
            logger.warning(f"Skipping listing {listing.productName} (ID: {listing_id}) due to missing coordinates")
            continue

        # Use farmer's location if set, otherwise use listing's location
        origin = (
            f"{user_profile.latitude},{user_profile.longitude}"
            if user_profile.latitude is not None and user_profile.longitude is not None
            else f"{listing.latitude},{listing.longitude}"
        )
        logger.debug(f"Optimizing route for listing: {listing.productName} (location: {listing.location}), origin: {origin}")

        # Prepare waypoints (order locations)
        waypoints = [f"{order.latitude},{order.longitude}" for order in listing_orders]
        if not waypoints:
            logger.warning(f"No valid waypoints for listing {listing.productName}")
            continue

        # Set destination as the last order's location (one-way route)
        destination = waypoints[-1] if len(waypoints) > 1 else origin
        logger.debug(f"Destination for one-way route: {destination}")

        # Call Google Maps Directions API for the optimized route
        params = {
            'origin': origin,
            'destination': destination,
            'waypoints': f"optimize:true|{('|').join(waypoints[:-1])}" if len(waypoints) > 1 else None,
            'key': api_key,
            'mode': 'driving',
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Google Maps API response for listing {listing.productName}: {data}")
        except requests.RequestException as e:
            logger.error(f"Failed to connect to Google Maps API for listing {listing.productName}: {str(e)}")
            continue

        if data['status'] != 'OK':
            logger.error(f"Google Maps API error for listing {listing.productName}: {data.get('error_message', 'Unknown error')}")
            continue

        # Extract optimized route
        try:
            route = data['routes'][0]
            waypoint_order = route.get('waypoint_order', list(range(len(waypoints) - 1)))
            legs = route['legs']
            total_distance = sum(leg['distance']['value'] for leg in legs) / 1000  # Convert meters to km
            total_duration = sum(leg['duration']['value'] for leg in legs) / 60  # Convert seconds to minutes

            # Calculate individual distance and time for each order
            optimized_orders = []
            for i, order in enumerate(listing_orders):
                # Use the optimized order for waypoint indices
                optimized_index = waypoint_order[i] if i < len(waypoint_order) else len(waypoint_order)
                order_location = f"{order.latitude},{order.longitude}"

                # Call Directions API for individual distance from origin to order
                individual_params = {
                    'origin': origin,
                    'destination': order_location,
                    'key': api_key,
                    'mode': 'driving',
                }
                try:
                    individual_response = requests.get(url, params=individual_params)
                    individual_response.raise_for_status()
                    individual_data = individual_response.json()
                    if individual_data['status'] == 'OK':
                        individual_leg = individual_data['routes'][0]['legs'][0]
                        individual_distance = individual_leg['distance']['value'] / 1000  # km
                        individual_duration = individual_leg['duration']['value'] / 60  # minutes
                        logger.debug(f"Individual estimate for order {order.id} to {order.location}: {individual_distance} km, {individual_duration} minutes")
                    else:
                        logger.warning(f"Individual API error for order {order.id}: {individual_data.get('error_message', 'Unknown error')}")
                        individual_distance = null
                        individual_duration = null
                except requests.RequestException as e:
                    logger.error(f"Failed to get individual distance for order {order.id}: {str(e)}")
                    individual_distance = null
                    individual_duration = null

                optimized_orders.append({
                    'order_id': order.id,
                    'product_name': order.listing.productName,
                    'quantity': order.quantity,
                    'location': order.location,
                    'latitude': order.latitude,
                    'longitude': order.longitude,
                    'customer': order.requester.user.username,
                    'individual_distance_km': individual_distance,
                    'individual_duration_minutes': individual_duration,
                })

            # Save waypoint order to orders
            for i, index in enumerate(waypoint_order + [len(waypoint_order)]):
                listing_orders[index].delivery_route = {'route_index': i, 'listing_id': listing_id}
                listing_orders[index].save()

            routes.append({
                'listing_id': listing_id,
                'listing_name': listing.productName,
                'listing_location': listing.location,
                'origin': origin,
                'orders': optimized_orders,
                'total_distance_km': total_distance,
                'total_duration_minutes': total_duration,
                'polyline': route['overview_polyline']['points'],
            })
            logger.info(f"Route optimization successful for listing {listing.productName}")
        except (KeyError, IndexError) as e:
            logger.error(f"Error processing Google Maps API response for listing {listing.productName}: {str(e)}")
            continue

    if not routes:
        logger.error("No routes could be optimized")
        return JsonResponse({
            'status': 'error',
            'message': 'No routes could be optimized. Ensure all listings have valid coordinates and orders have valid delivery locations.'
        }, status=400)

    logger.info(f"Optimized {len(routes)} routes")
    return JsonResponse({
        'status': 'success',
        'routes': routes
    })

@farmer_required
def update_farmer_location(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        logger.debug(f"Updating farmer location: latitude={latitude}, longitude={longitude}")

        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            logger.error(f"Invalid coordinates: latitude={latitude}, longitude={longitude}")
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid latitude or longitude values.'
            }, status=400)

        user_profile = request.user.userprofile
        user_profile.latitude = latitude
        user_profile.longitude = longitude
        user_profile.save()
        logger.info(f"Farmer location updated for user: {user_profile.user.username}")

        return JsonResponse({
            'status': 'success',
            'message': 'Farmer location updated successfully.'
        })
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Invalid request data: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f"Invalid request data: {str(e)}"
        }, status=400)
    


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


# MESSAGES
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
                # 'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': localtime(message.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
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
            # 'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'timestamp': localtime(msg.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
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

@login_required
def getConversations(request):
    user_profile = request.user.userprofile
    # print(f"User: {user_profile.user.username}, Role: {user_profile.role}")

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
            # 'timestamp': convo['last_message'].timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'timestamp': localtime(convo['last_message'].timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'unread': Message.objects.filter(
                listing=convo['listing'],
                recipient=user_profile,
                sender=convo['other_user'],
                is_read=False
            ).exists()
        } for convo in conversation_dict.values()
    ]

    return JsonResponse({'conversations': conversation_list})


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

        # # Validating the product_name and description whether they are agriculturally inclined
        # if not checkContent(product_name):
        #     return JsonResponse({'status': 'error', 'message': 'Product name is not related to agriculture. Please edit.'}, status=400)

        # if not checkContent(description):
        #     return JsonResponse({'status': 'error', 'message': 'Description is not agriculturally relevant. Please edit.'}, status=400)
        # # Validation ends here

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
                # 'created_at': product_request.created_at.strftime('%Y-%m-%d %H:%M:%S')
                'created_at': localtime(product_request.created_at).strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def edit_product_request(request, request_id):
    product_request = get_object_or_404(ProductRequest, id=request_id, requester=request.user.userprofile)

    if request.method == "POST":
        data = json.loads(request.body)

        # Get the new values from the request
        product_name = data.get('product_name', product_request.product_name).strip()
        quantity = float(data.get('quantity', product_request.quantity))
        unit = data.get('unit', product_request.unit).strip()
        description = data.get('description', product_request.description).strip()
        location = data.get('location', product_request.location).strip()

        
        # Update the product_request with validated values
        product_request.product_name = product_name
        product_request.quantity = quantity
        product_request.unit = unit
        product_request.description = description
        product_request.location = location

        try:
            # Validate and save
            # product_request.clean()  # Validate the object uncomment this
            product_request.save()  # Save to the database
            return JsonResponse({'status': 'success', 'message': 'Request updated successfully'})
        except ValidationError as e:
            # Handle validation errors
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

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
        # 'created_at': req.created_at.strftime('%Y-%m-%d %H:%M:%S')
        'created_at': localtime(req.created_at).strftime('%Y-%m-%d %H:%M:%S')
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
        # 'created_at': req.created_at.strftime('%Y-%m-%d %H:%M:%S')
        'created_at': localtime(req.created_at).strftime('%Y-%m-%d %H:%M:%S')
    } for req in requests]
    return JsonResponse({'requests': requests_data})

# END OF REQUEST VIEWS

# ORDERS VIEWs changed to handle the exact location of the user when ordering
@login_required
def createOrder(request):
    if request.method == "POST":
        data = json.loads(request.body)
        listing_id = data.get('listing_id')
        quantity = float(data.get('quantity', 0))
        location = data.get('location', '').strip()
        latitude = data.get('latitude')  # New field
        longitude = data.get('longitude')  # New field
        delivery_mode = data.get('deliveryMode', 'pickup')

        if not listing_id or quantity <= 0 or not location:
            return JsonResponse({'status': 'error', 'message': 'Listing ID, quantity, and location are required.'}, status=400)

        # Validate delivery_mode
        if delivery_mode not in dict(Order.ORDER_DELIVERY_CHOICES).keys():
            return JsonResponse({'status': 'error', 'message': 'Invalid delivery mode.'}, status=400)

        listing = get_object_or_404(productListing, id=listing_id, is_available=True)
        requester = request.user.userprofile

        order = Order.objects.create(
            listing=listing,
            requester=requester,
            quantity=quantity,
            location=location,
            latitude=float(latitude) if latitude else None,  # Store latitude
            longitude=float(longitude) if longitude else None,  # Store longitude
            deliveryMode=delivery_mode,
        )
        return JsonResponse({
            'status': 'success',
            'order': {
                'id': order.id,
                'product_name': order.listing.productName,
                'quantity': order.quantity,
                'total_price': float(order.total_price),
                'location': order.location,
                'latitude': order.latitude,
                'longitude': order.longitude,
                'delivery_mode': order.deliveryMode,
                'created_at': localtime(order.created_at).strftime('%Y-%m-%d %H:%M:%S'),
                'status': order.status,
            }
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# Farmer's Order Section (received orders by the farmer)
@farmer_required
def getFarmerOrders(request):
    user_profile = request.user.userprofile
    orders = Order.objects.filter(listing__farmer=user_profile).order_by('-created_at')
    orders_data = [{
        'id': order.id,
        'date': localtime(order.created_at).strftime('%Y-%m-%d %H:%M:%S'),
        'requester': order.requester.user.username,
        'crop': order.listing.productName,
        'quantity': order.quantity,
        'total': float(order.total_price),
        'location': order.location,
        'status': order.status,
        'deliveryMode': order.deliveryMode,
        'phone_number': order.requester.phoneNo,
    } for order in orders]
    return JsonResponse({'orders': orders_data})

@farmer_required
def updateOrderStatus(request, order_id):
    order = get_object_or_404(Order, id=order_id, listing__farmer=request.user.userprofile)
    if request.method == "POST":
        data = json.loads(request.body)
        new_status = data.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return JsonResponse({'status': 'success', 'message': 'Order status updated'})
        return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# MyOrders (the orders i have made)
@login_required
def getMyOrders(request):
    user_profile = request.user.userprofile
    orders = Order.objects.filter(requester=user_profile).order_by('-created_at')
    orders_data = [{
        'id': order.id,
        'farmer': order.listing.farmer.user.username,
        'crop': order.listing.productName,
        # 'date': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'date': localtime(order.created_at).strftime('%Y-%m-%d %H:%M:%S'),
        'quantity': order.quantity,
        'total': float(order.total_price),
        'status': order.status,
        'deliveryMode': order.deliveryMode,
        'can_delete': order.status in ('new', 'pending'),
    } for order in orders]
    return JsonResponse({'orders': orders_data})

@login_required
def deleteOrder(request, order_id):
    order = get_object_or_404(Order, id=order_id, requester=request.user.userprofile)
    if request.method == "POST":
        if order.status in ('new', 'pending'):
            listing = order.listing
            listing.quantity += order.quantity  # Restore quantity
            if listing.quantity > 0:
                listing.is_available = True
            listing.save()
            order.delete()
            return JsonResponse({'status': 'success', 'message': 'Order deleted'})
        return JsonResponse({'status': 'error', 'message': 'Cannot delete order in this status'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# END of ORDERS


# 25/04
# views.py (updated main function)
@login_required
def main(request):
    form = None
    listings = None
    marketplace_listings = productListing.objects.filter(is_available=True)
    my_requests = ProductRequest.objects.filter(requester=request.user.userprofile, is_active=True)
    product_requests = ProductRequest.objects.filter(is_active=True).exclude(requester=request.user.userprofile) if request.user.userprofile.role == 'farmer' else []

    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("User profile not found. Please complete your profile.")

    # Initialize variables
    order_analytics = None
    my_order_analytics = None
    earnings = None
    top_products = None
    inventory_status = None
    customer_engagement = None
    competitor_analysis = None
    competitor_crop_pricing = None  # New variable for bar graph data

    if user_profile.role == 'farmer':
        orders = Order.objects.filter(listing__farmer=user_profile)
        order_analytics = {
            'new': orders.filter(status='new').count(),
            'pending': orders.filter(status='pending').count(),
            'confirmed': orders.filter(status='confirmed').count(),
            'completed': orders.filter(status='completed').count(),
        }
        estimated_earnings = sum(float(order.total_price) for order in orders.filter(status__in=['new', 'pending', 'confirmed']))
        total_earnings = sum(float(order.total_price) for order in orders.filter(status='completed'))
        earnings = {'estimated': estimated_earnings, 'total': total_earnings}

        top_products_qs = orders.filter(status='completed').values('listing__productName').annotate(
            total_revenue=Sum('total_price'),
            total_quantity=Sum('quantity')
        ).order_by('-total_revenue')[:3]
        top_products = [{'name': p['listing__productName'], 'revenue': float(p['total_revenue']), 'quantity': p['total_quantity']} for p in top_products_qs]

        LOW_STOCK_THRESHOLD = 5 #in units
        listings_qs = productListing.objects.filter(farmer=user_profile, is_available=True)
        inventory_status = {
            'total_quantity': sum(l.quantity for l in listings_qs),
            'low_stock_count': listings_qs.filter(quantity__lt=LOW_STOCK_THRESHOLD).count(),
            'threshold': LOW_STOCK_THRESHOLD,
        }
        customer_engagement = {
            'unique_customers': orders.values('requester').distinct().count(),
            'unread_messages': Message.objects.filter(recipient=user_profile, is_read=False).count(),
        }
        farmer_categories = listings_qs.values_list('productCategory', flat=True).distinct()
        competitor_listings = productListing.objects.filter(is_available=True, productCategory__in=farmer_categories).exclude(farmer=user_profile)
        competitor_analysis = {
            'avg_price': float(competitor_listings.aggregate(Avg('price'))['price__avg'] or 0),
            'listing_count': competitor_listings.count(),
            'my_avg_price': float(listings_qs.aggregate(Avg('price'))['price__avg'] or 0),
        }

        # New: Competitor Crop Pricing for Bar Graph
        
        my_crops = listings_qs.values_list('productName', flat=True).distinct()  # Unique crops listed by this farmer
        county = user_profile.county  # Farmer's county
        competitor_crop_pricing = {}
        for crop in my_crops:
            # Get prices from other farmers in the same county for this crop, only available listings
            other_farmers_listings = productListing.objects.filter(
                is_available=True,  # Only available listings
                productName__iexact=crop,  # Case-insensitive match for crop name
                farmer__county=county
            ).exclude(farmer=user_profile).values('farmer__user__username', 'price').distinct()

            # My price for this crop
            my_price_qs = listings_qs.filter(productName__iexact=crop, is_available=True).aggregate(Avg('price'))
            my_price = float(my_price_qs['price__avg'] or 0) if my_price_qs['price__avg'] else 0

            # Build pricing data
            prices = {f"@{listing['farmer__user__username']}": float(listing['price']) for listing in other_farmers_listings}
            if my_price > 0:  # Only include "Me" if I have an available listing for this crop
                prices['Me'] = my_price
            if prices:  # Only add to the result if there’s data
                competitor_crop_pricing[crop] = prices

        # Product Listing
        if request.method == "POST":
            form = ListingForm(request.POST, request.FILES)
            if form.is_valid():
                listing = form.save(commit=False)
                listing.farmer = user_profile
                listing.save()
                return redirect("main")
            else:
                messages.error(request, form.errors.as_text())
        else:
            form = ListingForm(initial={'location': user_profile.county})

        listings = productListing.objects.filter(farmer=user_profile)
        query = request.GET.get('query', '').strip()
        if query:
            listings = listings.filter(productName__icontains=query)
        marketplace_listings = marketplace_listings.exclude(farmer=user_profile)

    my_orders = Order.objects.filter(requester=user_profile)
    my_order_analytics = {
        'new': my_orders.filter(status='new').count(),
        'pending': my_orders.filter(status='pending').count(),
        'confirmed': my_orders.filter(status='confirmed').count(),
        'completed': my_orders.filter(status='completed').count(),
    }

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
        'order_analytics': order_analytics,
        'my_order_analytics': my_order_analytics,
        'earnings': earnings,
        'top_products': top_products,
        'inventory_status': inventory_status,
        'customer_engagement': customer_engagement,
        'competitor_analysis': competitor_analysis,
        'competitor_crop_pricing': competitor_crop_pricing,  # New context variable
        # 'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY, #passing the googlemaps api key to market.html
    }
    print("Context competitor_crop_pricing:", context.get('competitor_crop_pricing'))
    return render(request, 'market.html', context)


