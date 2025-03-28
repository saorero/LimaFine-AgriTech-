{% extends "base2.html" %}
{% load widget_tweaks %}
{% load compress %}
{% load static %}

{% block content %}
<div class="max-w-6xl mx-auto">
    <!-- Header -->
    <h1 class="text-3xl font-bold mb-6">{{ message }}</h1>

    <!-- Tabs and Messaging Icon -->
    <div class="flex border-b mb-6 items-center">
        <button id="dashboardTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-blue-600 focus:outline-none tab-button active-tab">Dashboard</button>
        <button id="createListingTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-blue-600 focus:outline-none tab-button">Create Listing</button>
        <button id="marketplaceTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-blue-600 focus:outline-none tab-button">Marketplace</button>        
        <button id="createRequestTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-blue-600 focus:outline-none tab-button">ProductRequests</button>        
        <button id="forecastTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-blue-600 focus:outline-none tab-button">Forecast</button>

    
        <div class="flex items-center gap-0 ml-auto">
            <button id="myRequestTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-blue-600 focus:outline-none tab-button">MyRequests</button> 
            <!-- Question Mark Button (Product Request) -->
            <button id="requestButton" onclick="alert('Button clicked!');" class="px-4 py-2 text-teal-700 hover:text-gray-200" title="Product Request">
                <i class="fa-solid fa-circle-question fa-lg"></i>
            </button>
        
            <!-- Message Button (Message Farmer) -->
            <button onclick="alert('Button clicked! DASHBOARD'); openChatModal()" class="px-4 py-2 text-teal-700 hover:text-gray-200" title="Message Farmer">
                <i class="fas fa-envelope fa-lg "></i>
            </button>
        </div>
        
        
    </div>

    <!-- Dashboard Section (for farmers only) -->
    <div id="dashboardSection" class="tab-content">
        {% if user.userprofile.role == 'farmer' %}
            <!-- Search Form -->
            <div class="mb-6">
                <form method="GET" class="flex space-x-4">
                    <div class="flex-1">
                        <input type="text" name="query" value="{{ request.GET.query }}" placeholder="Search your listings by product name..." class="w-full p-2 border rounded">
                    </div>
                    <div class="flex items-end space-x-2">
                        <button type="submit" class="bg-teal-700 text-white p-2 rounded hover:bg-teal-200 hover:text-black">
                            <i class="fas fa-search"></i>
                        </button>
                        <a href="{% url 'main' %}" class="bg-gray-200 text-white p-2 rounded hover:bg-gray-600" title="Clear Search">
                            <i class="fas fa-times"></i>
                        </a>
                    </div>
                </form>
                {% if request.GET.query %}
                    <p class="text-gray-600 mt-2">Showing results for: <strong>{{ request.GET.query }}</strong></p>
                {% endif %}
            </div>

            <!-- Listings Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                {% if listings %}
                    {% for listing in listings %}
                    <div class="bg-white shadow-md rounded-lg overflow-hidden flex flex-col h-[19rem] hover:shadow-lg transition-shadow duration-200 p-2 relative">
                        <div class="h-40 w-full overflow-hidden">
                            <img src="{{ listing.get_image_url }}" alt="{{ listing.productName }}" class="w-full h-full object-cover">
                        </div>
                        <div class="p-3 flex flex-col flex-grow">
                            <h2 class="text-lg font-semibold line-clamp-1">{{ listing.productName }}</h2>
                            <p class="text-gray-500 text-sm">{{ listing.get_productCategory_display }}</p>
                            <div class="mt-2">
                                <p class="text-gray-700 font-bold">KES: {{ listing.price }} per {{ listing.unit }}</p>
                                <p class="text-gray-500 text-sm">Quantity Left: {{ listing.quantity }} {{ listing.unit }}</p>
                                <p class="text-gray-500 text-sm">{{ listing.location }}</p>
                            </div>
                            <p class="text-sm text-gray-600 mt-2 line-clamp-2 flex-grow">{{ listing.description }}</p>
                            <div class="mt-2 flex items-center justify-between">
                                <form method="POST" action="{% url 'toggle_availability' listing.id %}" class="flex items-center">
                                    {% csrf_token %}
                                    <label class="relative inline-flex items-center cursor-pointer">
                                        <input type="checkbox" name="is_available" {% if listing.is_available %}checked{% endif %} class="sr-only peer" onchange="this.form.submit()">
                                        <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:bg-teal-700 transition-colors duration-200"></div>
                                        <div class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform duration-200 peer-checked:translate-x-5"></div>
                                    </label>
                                    <span class="ml-2 text-sm font-semibold {% if listing.is_available %}text-teal-700{% else %}text-red-600{% endif %}">
                                        {% if listing.is_available %}Available{% else %}Sold Out{% endif %}
                                    </span>
                                </form>
                                <div class="flex space-x-2">
                                    <button onclick="openEditModal('{{ listing.id }}', '{{ listing.productName }}', '{{ listing.productCategory }}', '{{ listing.quantity }}', '{{ listing.unit }}', '{{ listing.price }}', '{{ listing.description }}', '{{ listing.location }}', '{{ listing.get_image_url }}')" class="text-yellow-500 hover:text-yellow-600" title="Edit Listing">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button onclick="openDeleteModal('{{ listing.id }}', '{{ listing.productName }}')" class="text-red-500 hover:text-red-600" title="Delete Listing">
                                        <i class="fas fa-trash-alt"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-gray-600 col-span-full">No listings found. {% if request.GET.query %}Try adjusting your search query.{% else %}Use the "Create Listing" tab to add a new listing.{% endif %}</p>
                {% endif %}
            </div>
        {% else %}
            <p class="text-gray-600">This section is only available to farmers.</p>
        {% endif %}
    </div>

    <!-- Create Listing Section (for farmers only) -->
    <div id="createListingSection" class="tab-content hidden">
        {% if user.userprofile.role == 'farmer' %}
            <div class="bg-white p-6 rounded-lg shadow-lg w-full">
                <h2 class="text-2xl font-bold mb-4 text-center">Create a New Listing</h2>
                <form method="POST" id="listingForm" class="space-y-4" enctype="multipart/form-data">
                    {% csrf_token %}
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Product Category</label>
                        {{ form.productCategory|add_class:"w-full p-2 border rounded" }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Product Name</label>
                        {{ form.productName|add_class:"w-full p-2 border rounded" }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Quantity</label>
                        {{ form.quantity|add_class:"w-full p-2 border rounded" }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Unit (e.g., kg)</label>
                        {{ form.unit|add_class:"w-full p-2 border rounded" }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Price (per unit)</label>
                        {{ form.price|add_class:"w-full p-2 border rounded" }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Description</label>
                        {{ form.description|add_class:"w-full p-2 border rounded" }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Location</label>
                        {{ form.location|add_class:"w-full p-2 border rounded" }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Upload Image (Optional)</label>
                        {{ form.image|add_class:"w-full p-2 border rounded" }}
                        <p class="text-sm text-gray-500 mt-1">If no image is uploaded, a default image will be used based on the product name.</p>
                    </div>
                    <button type="submit" class="w-full bg-green-600 text-white p-2 rounded hover:bg-green-700">Create Listing</button>
                </form>
            </div>
        {% else %}
            <p class="text-gray-600">This section is only available to farmers.</p>
        {% endif %}
    </div>

    <!-- Marketplace Section -->
    <div id="marketplaceSection" class="tab-content hidden">
        <div class="mb-6">
            <form method="GET" class="flex space-x-4">
                <div class="flex-1">
                    <input type="text" name="marketplace_query" value="{{ request.GET.marketplace_query }}" placeholder="Search marketplace by product name..." class="w-full p-2 border rounded">
                </div>
                <div class="flex items-end space-x-2">
                    <button type="submit" class="bg-teal-700 text-white p-2 rounded hover:bg-teal-200 hover:text-black">
                        <i class="fas fa-search"></i>
                    </button>
                    <a href="{% url 'main' %}" class="bg-gray-200 text-white p-2 rounded hover:bg-gray-600" title="Clear Search">
                        <i class="fas fa-times"></i>
                    </a>
                </div>
            </form>
            {% if request.GET.marketplace_query %}
                <p class="text-gray-600 mt-2">Showing results for: <strong>{{ request.GET.marketplace_query }}</strong></p>
            {% endif %}
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {% if marketplace_listings %}
                {% for listing in marketplace_listings %}
                <div class="bg-white shadow-md rounded-lg overflow-hidden flex flex-col h-[19rem] hover:shadow-lg transition-shadow duration-200 p-2 relative">
                    <div class="h-40 w-full overflow-hidden">
                        <img src="{{ listing.get_image_url }}" alt="{{ listing.productName }}" class="w-full h-full object-cover">
                    </div>
                    <div class="p-3 flex flex-col flex-grow">
                        <p class="text-gray-500 text-sm">{{ listing.get_productCategory_display }}</p>
                        <h2 class="text-lg font-semibold line-clamp-1">{{ listing.productName }}</h2>
                        <p class="text-gray-500 text-sm">by @{{ listing.farmer.user.username }}</p>
                        
                        <div class="mt-2">
                            <p class="text-gray-700 font-bold">KES: {{ listing.price }} per {{ listing.unit }}</p>
                            <p class="text-gray-700 font-bold">Quantity left: {{ listing.quantity }}{{ listing.unit }}</p>
                            <p class="text-gray-500 text-sm">{{ listing.location }}</p>
                        </div>
                        <p class="text-sm text-gray-600 mt-2 line-clamp-2 flex-grow">{{ listing.description }}</p>
                        <div class="mt-2 flex items-center justify-between">
                            <span class="text-sm font-semibold {% if listing.is_available %}text-teal-700{% else %}text-red-600{% endif %}">
                                {% if listing.is_available %}Available{% else %}Sold Out{% endif %}
                            </span>
                           
                            <button onclick="alert('Button clicked! For MARKETPLACE'); openChatModal('{{ listing.id }}', '{{ listing.productName }}', '{{ listing.get_image_url }}', '{{ listing.farmer.id|default:0 }}')" class="text-blue-500 hover:text-blue-600" title="Message Farmer">
                                <i class="fas fa-envelope"></i>
                            </button>
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p class="text-gray-600 col-span-full">No listings found in the marketplace.</p>
            {% endif %}
        </div>
    </div>
</div>

<!-- MyRequests Section -->
<div id="myRequestSection" class="tab-content hidden">
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {% for request in my_requests %}
        <div class="bg-white shadow-md rounded-lg p-4">
            <h3 class="text-lg font-semibold">{{ request.product_name }}</h3>
            <p class="text-gray-600">{{ request.quantity }} {{ request.unit }}</p>
            <p class="text-gray-600">{{ request.description }}</p>
            <p class="text-gray-600">{{ request.location }}</p>
            <p class="text-gray-500 text-sm">{{ request.created_at }}</p>
            <div class="mt-2 flex space-x-2">
                <button onclick="openEditRequestModal({{ request.id }}, '{{ request.product_name }}', '{{ request.quantity }}', '{{ request.unit }}', '{{ request.description }}', '{{ request.location }}')" class="text-yellow-500 hover:text-yellow-600" title="Edit Request">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="openDeleteRequestModal({{ request.id }}, '{{ request.product_name }}')" class="text-red-500 hover:text-red-600" title="Delete Request">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        </div>
        {% empty %}
        <p class="text-gray-600 col-span-full">No requests yet. Use the Product Request button to create one.</p>
        {% endfor %}
    </div>
</div>

<!-- ProductRequests Section (Farmers Only) -->
{% if user.userprofile.role == 'farmer' %}
<div id="createRequestSection" class="tab-content hidden">
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {% for request in product_requests %}
        <!-- THIS PART IS NOT EVEN WORKING FIX THIS -->
        <div class="bg-white shadow-md rounded-lg p-4">
            <h3 class="text-lg font-semibold">{{ request.product_name }}</h3>
            <p class="text-gray-600">{{ request.quantity }}  {{ request.unit }}</p>
            <p class="text-gray-600">{{ request.description }}</p>
            <p class="text-gray-600">{{ request.location }}</p>
            <p class="text-gray-500 text-sm">Requested by @{{ request.requester.user.username }}</p>
            <p class="text-gray-500 text-sm">{{ request.created_at }}</p>
            <button onclick="alert('Button Clicked:- PRODUCT REQUEST'); openChatModal(null, '{{ request.product_name }}', '', '{{ request.requester.id }}')" class="text-blue-500 hover:text-blue-600 mt-2" title="Message Requester">
                <i class="fas fa-envelope"></i>
            </button>            

        </div>
        {% empty %}
        <p class="text-gray-600 col-span-full">No product requests available.</p>
        {% endfor %}
    </div>
</div>
{% endif %}
</div>

{% endblock content %}

{% block modalsContent %}
<!-- Existing Edit and Delete Modals  -->
   <!-- EDIT Modal -->
<div id="editModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center hidden z-50">
    <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-md max-h-[90vh] overflow-y-auto">
        <h2 class="text-2xl font-bold mb-4">Edit Listing</h2>
        <form id="editForm" method="POST" enctype="multipart/form-data" class="space-y-4">
            {% csrf_token %}
            <input type="hidden" name="listing_id" id="editListingId">
            <div>
                <label class="block text-sm font-medium text-gray-700">Product Category</label>
                <select name="productCategory" id="editProductCategory" class="w-full p-2 border rounded">
                    <option value="crop">Crop</option>
                    <option value="dairy">Dairy product</option>
                    <option value="meat">Meat product</option>
                </select>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Product Name</label>
                <input type="text" name="productName" id="editProductName" class="w-full p-2 border rounded">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Quantity</label>
                <input type="number" name="quantity" id="editQuantity" step="0.01" class="w-full p-2 border rounded">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Unit (e.g., kg)</label>
                <input type="text" name="unit" id="editUnit" class="w-full p-2 border rounded">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Price (per unit)</label>
                <input type="number" name="price" id="editPrice" step="0.01" class="w-full p-2 border rounded">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Description</label>
                <textarea name="description" id="editDescription" class="w-full p-2 border rounded"></textarea>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Location</label>
                <input type="text" name="location" id="editLocation" class="w-full p-2 border rounded">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Upload Image (Optional)</label>
                <input type="file" name="image" id="editImage" class="w-full p-2 border rounded">
                <p class="text-sm text-gray-500 mt-1">Current Image: <img id="editCurrentImage" src="" alt="Current Image" class="w-16 h-16 object-cover rounded inline-block ml-2"></p>
                <label class="mt-2 flex items-center">
                    <input type="checkbox" name="clear_image" id="editClearImage" class="mr-2">
                    <span class="text-sm text-gray-700">Clear current image</span>
                </label>
            </div>
            <div class="flex space-x-4">
                <button type="submit" class="w-full bg-yellow-500 text-white p-2 rounded hover:bg-yellow-600">Save Changes</button>
                <button type="button" onclick="closeEditModal()" class="w-full bg-gray-500 text-white p-2 rounded hover:bg-gray-600">Cancel</button>
            </div>
        </form>
    </div>
</div>

<!-- Delete Listing Modal -->
<div id="deleteModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center hidden z-50">
    <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4">Delete Listing</h2>
        <p class="text-lg mb-4">Are you sure you want to delete the listing for <strong id="deleteProductName"></strong>?</p>
        <p class="text-gray-600 mb-4">This action cannot be undone.</p>
        <form id="deleteForm" method="POST">
            {% csrf_token %}
            <input type="hidden" name="listing_id" id="deleteListingId">
            <div class="flex space-x-4">
                <button type="submit" class="w-full bg-red-500 text-white p-2 rounded hover:bg-red-600">Yes, Delete</button>
                <button type="button" onclick="closeDeleteModal()" class="w-full bg-gray-500 text-white p-2 rounded hover:bg-gray-600">Cancel</button>
            </div>
        </form>
    </div>
</div>

<!-- Chat Modal 25/04-->
<div id="chatModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center hidden z-50">
    <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-2xl max-h-[90vh] flex flex-col">
        <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">Messages</h2>
            <button onclick="closeChatModal()" class="text-gray-500 hover:text-gray-700">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div id="chatContainer" class="flex flex-1 overflow-hidden">
            <!-- Conversations List -->
            <div id="conversationsList" class="w-1/3 border-r overflow-y-auto max-h-[70vh]">
                <div id="conversationItems" class="space-y-2 p-2"></div>
            </div>
            <!-- Chat Area -->
            <div id="chatArea" class="w-2/3 flex flex-col hidden">
                <div id="chatHeader" class="p-2 border-b flex items-center">
                    <!-- data has image prevents the image from showing in product requests -->
                    <img id="chatListingImage" src="" alt="Listing" class="w-10 h-10 object-cover rounded mr-2 " data-has-image="false"> 
                    <div>
                        <h3 id="chatListingName" class="font-semibold"></h3>
                        <p id="chatOtherUser" class="text-sm text-gray-500"></p>
                    </div>
                </div>
                <div id="messagesContainer" class="flex-1 p-4 overflow-y-auto max-h-[50vh]"></div>
                <form id="messageForm" class="p-2 border-t">
                    <input type="hidden" id="chatListingId" name="listing_id">
                    <input type="hidden" id="chatRecipientId" name="recipient_id">
                    <div class="flex space-x-2">
                        <input type="text" id="messageInput" class="flex-1 p-2 border rounded" placeholder="Type a message...">
                        <button type="submit" class="bg-blue-500 text-white p-2 rounded hover:bg-blue-600">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<!-- Product Request Modal -->
<div id="requestModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center hidden z-50">
    <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4">Request a Product</h2>
        <form id="requestForm" class="space-y-4">
            {% csrf_token %}
            <div>
                <label class="block text-sm font-medium text-gray-700">Product Name</label>
                <input type="text" id="requestProductName" class="w-full p-2 border rounded" required>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Quantity</label>
                <input type="number" id="requestQuantity" step="0.01" class="w-full p-2 border rounded" required>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Unit (e.g., kg)</label>
                <input type="text" id="requestUnit" class="w-full p-2 border rounded" value="kg">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Description (Optional)</label>
                <textarea id="requestDescription" class="w-full p-2 border rounded"></textarea>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Location</label>
                <input type="text" id="requestLocation" class="w-full p-2 border rounded" required>
            </div>
            <div class="flex space-x-4">
                <button type="submit" class="w-full bg-teal-700 text-white p-2 rounded hover:bg-teal-800">Submit Request</button>
                <button type="button" onclick="closeRequestModal()" class="w-full bg-gray-500 text-white p-2 rounded hover:bg-gray-600">Cancel</button>
            </div>
        </form>
    </div>
</div>

<!-- Edit Request Modal -->
<div id="editRequestModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center hidden z-50">
    <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4">Edit Request</h2>
        <form id="editRequestForm" class="space-y-4">
            {% csrf_token %}
            <input type="hidden" id="editRequestId">
            <div>
                <label class="block text-sm font-medium text-gray-700">Product Name</label>
                <input type="text" id="editRequestProductName" class="w-full p-2 border rounded" required>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Quantity</label>
                <input type="number" id="editRequestQuantity" step="0.01" class="w-full p-2 border rounded" required>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Unit (e.g., kg)</label>
                <input type="text" id="editRequestUnit" class="w-full p-2 border rounded">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Description (Optional)</label>
                <textarea id="editRequestDescription" class="w-full p-2 border rounded"></textarea>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Location</label>
                <input type="text" id="editRequestLocation" class="w-full p-2 border rounded" required>
            </div>
            <div class="flex space-x-4">
                <button type="submit" class="w-full bg-yellow-500 text-white p-2 rounded hover:bg-yellow-600">Save Changes</button>
                <button type="button" onclick="closeEditRequestModal()" class="w-full bg-gray-500 text-white p-2 rounded hover:bg-gray-600">Cancel</button>
            </div>
        </form>
    </div>
</div>

<!-- Delete Request Modal -->
<div id="deleteRequestModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center hidden z-50">
    <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4">Delete Request</h2>
        <p class="text-lg mb-4">Are you sure you want to delete the request for <strong id="deleteRequestProductName"></strong>?</p>
        <p class="text-gray-600 mb-4">This action cannot be undone.</p>
        <form id="deleteRequestForm" method="POST">
            {% csrf_token %}
            <input type="hidden" id="deleteRequestId">
            <div class="flex space-x-4">
                <button type="submit" class="w-full bg-red-500 text-white p-2 rounded hover:bg-red-600">Yes, Delete</button>
                <button type="button" onclick="closeDeleteRequestModal()" class="w-full bg-gray-500 text-white p-2 rounded hover:bg-gray-600">Cancel</button>
            </div>
        </form>
    </div>
</div>
{% endblock modalsContent %}

{% block script %}
<script>
    const tabs = document.querySelectorAll('.tab-button');
    const contents = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active-tab', 'border-blue-600'));
            contents.forEach(c => c.classList.add('hidden'));
            tab.classList.add('active-tab', 'border-blue-600');
            document.getElementById(tab.id.replace('Tab', 'Section')).classList.remove('hidden');
        });
    });
   
    // Function to validate the quantity and quality entered in List creation
    function validateListingForm(event) {
        const quantity = document.querySelector("[name='quantity']")?.value;
        const price = document.querySelector("[name='price']")?.value;
        if (quantity <= 0 || price <= 0) {
            event.preventDefault(); // Prevent form submission
            alert("Quantity and Price must be greater than zero!");
        }
    }
    
     
    // Edit Modal Function ...prefilled with the values initiated
    function openEditModal(id, ProductName, productCategory, quantity, unit, price, description, location, imageUrl) {
        document.getElementById('editModal').classList.remove('hidden');
        document.getElementById('editListingId').value = id;
        document.getElementById('editProductName').value = ProductName;
        document.getElementById('editProductCategory').value = productCategory;
        document.getElementById('editQuantity').value = quantity;
        document.getElementById('editUnit').value = unit;
        document.getElementById('editPrice').value = price;
        document.getElementById('editDescription').value = description;
        document.getElementById('editLocation').value = location;
        document.getElementById('editCurrentImage').src = imageUrl;
        document.getElementById('editForm').action = `/market/edit/${id}/`;
    }

    function closeEditModal() {
        document.getElementById('editModal').classList.add('hidden');
        document.getElementById('editForm').reset();
        document.getElementById('editClearImage').checked = false;
    }

    // Delete Modal Function
    function openDeleteModal(id, ProductName) {
        document.getElementById('deleteModal').classList.remove('hidden');
        document.getElementById('deleteListingId').value = id;
        document.getElementById('deleteProductName').textContent = ProductName;
        document.getElementById('deleteForm').action = `/market/delete/${id}/`;
    }

    function closeDeleteModal() {
        document.getElementById('deleteModal').classList.add('hidden');
    }

    // Debounce function that limits API calls
    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    // Search functions for marketPlace and dahboard
    const dashboardSearchInput = document.querySelector('input[name="query"]');
    if (dashboardSearchInput) {
        dashboardSearchInput.addEventListener('input', debounce(function() {
            document.querySelector('#dashboardSection form').submit();
        }, 500));
    }
    const marketplaceSearchInput = document.querySelector('input[name="marketplace_query"]');
    if (marketplaceSearchInput) {
        marketplaceSearchInput.addEventListener('input', debounce(function() {
            document.querySelector('#marketplaceSection form').submit();
        }, 500));
    }

    // 25/04
    //Function for sending message to the server
    function sendMessage(event) {
            event.preventDefault(); // Prevent default form submission
            console.log('Message Debug, Sending Message');
            const listingId = document.getElementById('chatListingId')?.value;
            const recipientId = document.getElementById('chatRecipientId')?.value;
            const content = document.getElementById('messageInput')?.value;
            console.log(`Sending message: listingId=${listingId}, recipientId=${recipientId}, content=${content}`);//for debug

            // Ensure required fields are not empty
            if (!listingId || !recipientId || !content.trim()) {
                alert("Please enter a message before sending.");
                return;
            }
            //making post request to the server in the defined endpoint
            fetch('/market/messages/send/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value  // Ensure CSRF token is included
                },
                body: JSON.stringify({ listing_id: listingId, recipient_id: recipientId, content: content }) //Data sent to server
            })
            // Process response received from the endpoint
            .then(response => response.json())
            .then(data => {
                console.log('Response:', data);
                if (data.status === 'success') {
                    loadMessages(listingId, recipientId); //refresh the message to get latest message
                    document.getElementById('messageInput').value = ''; // Clear input after sending
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error sending message:', error);
            });
    }
   

    //TOWARDS THE END  Commented the original 27/03/ new open chat
//     function openChatModal(listingId = null, listingName = null, listingImage = null, recipientId = null) {
//     const chatModal = document.getElementById('chatModal');
//     chatModal.classList.remove('hidden');
//     console.log('Loading Convo'); //Debug
//     loadConversations();

//     const messageForm = document.getElementById('messageForm');
//     if (messageForm) {
//         messageForm.removeEventListener('submit', handleMessageSubmit);
//         messageForm.addEventListener('submit', handleMessageSubmit);
//     } else {
//         console.error('messageForm not found in DOM after opening chat modal');
//     }

//     if (recipientId) {
//         // Use 'none' for listingId if not provided (e.g., from ProductRequests)
//         const effectiveListingId = listingId || 'none';
//         fetch(`/market/messages/${effectiveListingId}/${recipientId}/`)
//             .then(response => response.json())
//             .then(data => {
//                 document.getElementById('chatArea').classList.remove('hidden');
//                 document.getElementById('chatListingId').value = effectiveListingId;
//                 document.getElementById('chatRecipientId').value = recipientId;
//                 document.getElementById('chatListingName').textContent = data.listing_name;
//                 document.getElementById('chatListingImage').src = data.listing_image;
//                 document.getElementById('chatOtherUser').textContent = `@${data.other_user}`;
//                 loadMessages(effectiveListingId, recipientId);
//             });
//     } else {
//         document.getElementById('chatArea').classList.add('hidden');
//     }
// }

    //TRYING THIS OUT TO LOOK LIKE THE ORIGINAL 28TH TO DELETE IF IT DOES NOT WORK
    // function openChatModal(listingId = null, listingName = null, listingImage = null, recipientId = null) {
    // const chatModal = document.getElementById('chatModal');
    // chatModal.classList.remove('hidden');
    // console.log('Loading Convo trial'); //Debug
    // loadConversations();

    // if ((listingId && recipientId) || (recipientId && listingName)) {
    //     // Use 'none' for listingId if not provided (e.g., from ProductRequests)
    //     const effectiveListingId = listingId || 'null';
    //     fetch(`/market/messages/${effectiveListingId}/${recipientId}/`)
    //         .then(response => response.json())
    //         .then(data => {
    //             document.getElementById('chatArea').classList.remove('hidden');
    //             document.getElementById('chatListingId').value = effectiveListingId;
    //             document.getElementById('chatRecipientId').value = recipientId;
    //             document.getElementById('chatListingName').textContent = data.listing_name;
    //             document.getElementById('chatListingImage').src = data.listing_image;
    //             document.getElementById('chatOtherUser').textContent = `@${data.other_user}`;
    //             loadMessages(effectiveListingId, recipientId);
    //         });
    // } else {
    //     document.getElementById('chatArea').classList.add('hidden');
    // }
    // }

    //28TH CHANGES
//     function openChatModal(listingId = null, listingName = null, listingImage = null, recipientId = null) {
//     const chatModal = document.getElementById('chatModal');
//     chatModal.classList.remove('hidden');
//     console.log('Opening chat modal with:', { listingId, listingName, listingImage, recipientId });
//     loadConversations();

//     if (recipientId) {  // Only require recipientId to proceed
//         const effectiveListingId = listingId || 'none';  // Use 'none' for product requests
//         fetch(`/market/messages/${effectiveListingId}/${recipientId}/`)
//             .then(response => {
//                 if (!response.ok) {
//                     throw new Error(`HTTP error! Status: ${response.status}`);
//                 }
//                 return response.json();
//             })
//             .then(data => {
//                 console.log('Fetch response:', data);
//                 document.getElementById('chatArea').classList.remove('hidden');
//                 document.getElementById('chatListingId').value = effectiveListingId;
//                 document.getElementById('chatRecipientId').value = recipientId;
//                 // Use provided listingName if available (e.g., product name), else fall back to server response
//                 document.getElementById('chatListingName').textContent = listingName || data.listing_name;
//                 document.getElementById('chatListingImage').src = listingImage || data.listing_image || '';
//                 document.getElementById('chatOtherUser').textContent = `@${data.other_user}`;
//                 loadMessages(effectiveListingId, recipientId);
//             })
//             .catch(error => {
//                 console.error('Error fetching messages:', error);
//                 alert('Failed to load chat. Check console for details.');
//             });
//     } else {
//         document.getElementById('chatArea').classList.add('hidden');
//     }
// }



function openChatModal(listingId = null, listingName = null, listingImage = null, recipientId = null) {
    const chatModal = document.getElementById('chatModal');
    chatModal.classList.remove('hidden');
    console.log('Opening chat modal with:', { listingId, listingName, listingImage, recipientId });
    loadConversations();

    if (recipientId) {
        const effectiveListingId = listingId || 'none';  // Ensure 'none' for product requests
        currentConversation = null;
        fetch(`/market/messages/${effectiveListingId}/${recipientId}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Fetch response:', data);
                document.getElementById('chatArea').classList.remove('hidden');
                document.getElementById('chatListingId').value = effectiveListingId;
                document.getElementById('chatRecipientId').value = recipientId;
                document.getElementById('chatListingName').textContent = listingName || data.listing_name;
                document.getElementById('chatListingImage').src = listingImage || data.listing_image || '';
                document.getElementById('chatOtherUser').textContent = `@${data.other_user}`;
                loadMessages(effectiveListingId, recipientId);
            })
            .catch(error => {
                console.error('Error fetching messages:', error);
                alert('Failed to load chat. Check console for details.');
            });
    } else {
        document.getElementById('chatArea').classList.add('hidden');
        currentConversation = null;
    }
}

//Original as of 28th at 12:45
function openChatModal(listingId = null, listingName = null, listingImage = null, recipientId = null) {
    const chatModal = document.getElementById('chatModal');
    chatModal.classList.remove('hidden');
    console.log('Opening chat modal with:', { listingId, listingName, listingImage, recipientId });
    loadConversations();

    if (recipientId) {
        const effectiveListingId = listingId || 'none';  // Use 'none' for product requests
        fetch(`/market/messages/${effectiveListingId}/${recipientId}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Fetch response:', data);
                document.getElementById('chatArea').classList.remove('hidden');
                document.getElementById('chatListingId').value = effectiveListingId;
                document.getElementById('chatRecipientId').value = recipientId;
                document.getElementById('chatListingName').textContent = listingName || data.listing_name;
                document.getElementById('chatListingImage').src = listingImage || data.listing_image || '';
                document.getElementById('chatOtherUser').textContent = `@${data.other_user}`;
                loadMessages(effectiveListingId, recipientId);
            })
            .catch(error => {
                console.error('Error fetching messages:', error);
                alert('Failed to load chat. Check console for details.');
            });
    } else {
        document.getElementById('chatArea').classList.add('hidden');
    }
}

function handleMessageSubmit(e) {
    e.preventDefault();
    const listingId = document.getElementById('chatListingId').value || 'none';  // Default to 'none'
    const recipientId = document.getElementById('chatRecipientId').value;
    const content = document.getElementById('messageInput').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    console.log(`Preparing to send: listingId=${listingId}, recipientId=${recipientId}, content="${content}"`);

    if (!recipientId || !content) {
        console.error('Invalid form data:', { listingId, recipientId, content });
        alert('Please ensure all fields are filled correctly.');
        return;
    }

    fetch('/market/messages/send/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            listing_id: listingId === 'none' ? null : listingId,
            recipient_id: recipientId,
            content: content
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(`HTTP error! Status: ${response.status}: ${text}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.status === 'success') {
            loadMessages(listingId, recipientId);
            document.getElementById('messageInput').value = '';
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Fetch error:', error.message);
        alert('Failed to send message. Check the console for details.');
    });
}

//END OF 28 CHANGES

//28TH loadmessage
function loadMessages(listingId, recipientId) {
    const effectiveListingId = listingId || 'none';  // Ensure it's never undefined
    const conversationKey = `${effectiveListingId}-${recipientId}`;
    if (currentConversation === conversationKey) {
        console.log('Skipping duplicate loadMessages call for:', conversationKey);
        return;
    }
    currentConversation = conversationKey;

    fetch(`/market/messages/${effectiveListingId}/${recipientId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('chatOtherUser').textContent = `@${data.other_user}`;
            const messagesContainer = document.getElementById('messagesContainer');
            messagesContainer.innerHTML = '';
            data.messages.forEach(msg => {
                const msgDiv = document.createElement('div');
                msgDiv.className = `mb-2 ${msg.is_sender ? 'text-right' : 'text-left'}`;
                msgDiv.innerHTML = `
                    <div class="inline-block p-2 rounded-lg ${msg.is_sender ? 'bg-blue-100' : 'bg-gray-100'}">
                        <p class="text-sm">${msg.content}</p>
                        <p class="text-xs text-gray-500">${msg.timestamp}</p>
                    </div>
                `;
                messagesContainer.appendChild(msgDiv);
            });
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        })
        .catch(error => {
            console.error('Error loading messages:', error);
        });
}

// Original Load message
// function loadMessages(listingId, recipientId) {
//     fetch(`/market/messages/${listingId}/${recipientId}/`)
//         .then(response => response.json())
//         .then(data => {
//             document.getElementById('chatOtherUser').textContent = `@${data.other_user}`;
//             const messagesContainer = document.getElementById('messagesContainer');
//             messagesContainer.innerHTML = '';
//             data.messages.forEach(msg => {
//                 const msgDiv = document.createElement('div');
//                 msgDiv.className = `mb-2 ${msg.is_sender ? 'text-right' : 'text-left'}`;
//                 msgDiv.innerHTML = `
//                     <div class="inline-block p-2 rounded-lg ${msg.is_sender ? 'bg-blue-100' : 'bg-gray-100'}">
//                         <p class="text-sm">${msg.content}</p>
//                         <p class="text-xs text-gray-500">${msg.timestamp}</p>
//                     </div>
//                 `;
//                 messagesContainer.appendChild(msgDiv);
//             });
//             messagesContainer.scrollTop = messagesContainer.scrollHeight;
//         });
// }
    //ENDS HERE 27
    // Chat Modal Functions for Messaging original chatmodal not modified but working nicely
    // function openChatModal(listingId = null, listingName = null, listingImage = null, recipientId = null) {
    //     console.log("hello")
    //     document.getElementById('chatModal').classList.remove('hidden');
    //     loadConversations();        
    //     if (listingId && recipientId) {
    //         // If a specific chat is provided, open that conversation
    //         fetch(`/market/messages/${listingId}/${recipientId}/`)
    //             .then(response => response.json())
    //             .then(data => {
    //                 document.getElementById('chatArea').classList.remove('hidden');
    //                 document.getElementById('chatListingId').value = listingId;
    //                 document.getElementById('chatRecipientId').value = recipientId;
    //                 document.getElementById('chatListingName').textContent = data.listing_name;
    //                 document.getElementById('chatListingImage').src = data.listing_image;
    //                 document.getElementById('chatOtherUser').textContent = `@${data.other_user}`;
    //                 loadMessages(listingId, recipientId);
    //             });
    //     } else {
    //         // If no specific listing, ensure chat area is hidden until a conversation is selected
    //         document.getElementById('chatArea').classList.add('hidden');
    //     }
    // }

    function closeChatModal() {
        document.getElementById('chatModal').classList.add('hidden');
        document.getElementById('chatArea').classList.add('hidden');
    }

    function loadConversations() {
        console.log("Load conversation function ...")
        fetch('/market/messages/conversations/')
            .then(response => response.json())
            .then(data => {
                const conversationItems = document.getElementById('conversationItems');
                conversationItems.innerHTML = '';
                let unreadCount = 0;
                data.conversations.forEach(convo => {
                    if (convo.unread) unreadCount++;
                    const item = document.createElement('div');
                    item.className = `p-2 hover:bg-gray-100 cursor-pointer ${convo.unread ? 'font-bold' : ''}`;
                    item.innerHTML = `
                        <div class="flex items-center">
                            <img src="${convo.listing_image}" alt="${convo.listing_name}" class="w-8 h-8 object-cover rounded mr-2">
                            <div>
                                <p class="text-sm">${convo.listing_name}</p>
                                <p class="text-xs text-gray-500">@${convo.other_user}: ${convo.last_message.substring(0, 20)}...</p>
                            </div>
                        </div>
                    `;
                    item.onclick = () => openConversation(convo.listing_id, convo.listing_name, convo.listing_image, convo.other_user_id);
                    conversationItems.appendChild(item);
                });
                const badge = document.getElementById('unreadBadge');
                if (unreadCount > 0) {
                    badge.textContent = unreadCount;
                    badge.classList.remove('hidden');
                } else {
                    badge.classList.add('hidden');
                }
            });
    }

    function openConversation(listingId, listingName, listingImage, recipientId) {
        document.getElementById('chatArea').classList.remove('hidden');
        document.getElementById('chatListingId').value = listingId;
        document.getElementById('chatRecipientId').value = recipientId;
        document.getElementById('chatListingName').textContent = listingName;
        document.getElementById('chatListingImage').src = listingImage;
        document.getElementById('chatOtherUser').textContent = `@${recipientId}`; // Replace with actual username via API response
        loadMessages(listingId, recipientId);
    }

    function loadMessages(listingId, recipientId) {
        fetch(`/market/messages/${listingId}/${recipientId}/`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('chatOtherUser').textContent = `@${data.other_user}`;
                const messagesContainer = document.getElementById('messagesContainer');
                messagesContainer.innerHTML = '';
                data.messages.forEach(msg => {
                    const msgDiv = document.createElement('div');
                    msgDiv.className = `mb-2 ${msg.is_sender ? 'text-right' : 'text-left'}`;
                    msgDiv.innerHTML = `
                        <div class="inline-block p-2 rounded-lg ${msg.is_sender ? 'bg-blue-100' : 'bg-gray-100'}">
                            <p class="text-sm">${msg.content}</p>
                            <p class="text-xs text-gray-500">${msg.timestamp}</p>
                        </div>
                    `;
                    messagesContainer.appendChild(msgDiv);
                });
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            });
    }
      
// PRODUCT REQUEST
// Product Request Modal Functions
document.getElementById('requestButton').addEventListener('click', () => openRequestModal());
    function openRequestModal() {
        document.getElementById('requestModal').classList.remove('hidden');
    }
    function closeRequestModal() {
        document.getElementById('requestModal').classList.add('hidden');
        document.getElementById('requestForm').reset();
    }

    // document.getElementById('requestForm').addEventListener('submit', function(e) {
    //     e.preventDefault();
    //     const productName = document.getElementById('requestProductName').value;
    //     const quantity = document.getElementById('requestQuantity').value;
    //     const unit = document.getElementById('requestUnit').value;
    //     const description = document.getElementById('requestDescription').value;
    //     const location = document.getElementById('requestLocation').value;
    //     const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    //     console.log('Creating request')
    //     fetch('/market/request/create/', {
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/json',
    //             'X-CSRFToken': csrfToken
    //         },
    //         body: JSON.stringify({ product_name: productName, quantity: quantity, unit: unit, description: description, location: location })
    //     })
    //     .then(response => response.json())
    //     .then(data => {
    //         if (data.status === 'success') {
    //             closeRequestModal();
    //             loadMyRequests(); // Refresh MyRequests tab
    //         } else {
    //             alert(data.message);
    //         }
    //     })
    //     .catch(error => console.error('Error:', error));
    // });

    function submitRequestForm(event) { //NOW Function
    event.preventDefault(); // Prevent default form submission

    // Get form data
    const productName = document.getElementById('requestProductName').value;
    const quantity = document.getElementById('requestQuantity').value;
    const unit = document.getElementById('requestUnit').value;
    const description = document.getElementById('requestDescription').value;
    const location = document.getElementById('requestLocation').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    console.log('Creating request');

    // Send data via Fetch API
    fetch('/market/request/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            product_name: productName,
            quantity: quantity,
            unit: unit,
            description: description,
            location: location
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            closeRequestModal(); // Close modal
            loadMyRequests(); // Refresh the MyRequests tab
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Attach function to the form submit event
// document.getElementById('requestForm').addEventListener('submit', submitRequestForm); NOW

    // Edit Request Modal Functions
    function openEditRequestModal(id, productName, quantity, unit, description, location) {
        document.getElementById('editRequestModal').classList.remove('hidden');
        document.getElementById('editRequestId').value = id;
        document.getElementById('editRequestProductName').value = productName;
        document.getElementById('editRequestQuantity').value = quantity;
        document.getElementById('editRequestUnit').value = unit;
        document.getElementById('editRequestDescription').value = description;
        document.getElementById('editRequestLocation').value = location;
    }
    function closeEditRequestModal() {
        document.getElementById('editRequestModal').classList.add('hidden');
    }

    document.getElementById('editRequestForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const id = document.getElementById('editRequestId').value;
        const productName = document.getElementById('editRequestProductName').value;
        const quantity = document.getElementById('editRequestQuantity').value;
        const unit = document.getElementById('editRequestUnit').value;
        const description = document.getElementById('editRequestDescription').value;
        const location = document.getElementById('editRequestLocation').value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(`/market/request/edit/${id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ product_name: productName, quantity: quantity, unit: unit, description: description, location: location })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                closeEditRequestModal();
                loadMyRequests();
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Delete Request Modal Functions
    function openDeleteRequestModal(id, productName) {
        document.getElementById('deleteRequestModal').classList.remove('hidden');
        document.getElementById('deleteRequestId').value = id;
        document.getElementById('deleteRequestProductName').textContent = productName;
    }
    function closeDeleteRequestModal() {
        document.getElementById('deleteRequestModal').classList.add('hidden');
    }

    document.getElementById('deleteRequestForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const id = document.getElementById('deleteRequestId').value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(`/market/request/delete/${id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                closeDeleteRequestModal();
                loadMyRequests();
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Load Requests Dynamically
    function loadMyRequests() {
        fetch('/market/my_requests/')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('myRequestSection').querySelector('.grid');
                container.innerHTML = '';
                if (data.requests.length === 0) {
                    container.innerHTML = '<p class="text-gray-600 col-span-full">No requests yet. Use the Product Request button to create one.</p>';
                } else {
                    data.requests.forEach(req => {
                        const div = document.createElement('div');
                        div.className = 'bg-white shadow-md rounded-lg p-4';
                        div.innerHTML = `
                            <h3 class="text-lg font-semibold">${req.product_name}</h3>
                            <p class="text-gray-600">${req.quantity} ${req.unit}</p>
                            <p class="text-gray-600">${req.description}</p>
                            <p class="text-gray-600">${req.location}</p>
                            <p class="text-gray-500 text-sm">${req.created_at}</p>
                            <div class="mt-2 flex space-x-2">
                                <button onclick="openEditRequestModal(${req.id}, '${req.product_name}', '${req.quantity}', '${req.unit}', '${req.description}', '${req.location}')" class="text-yellow-500 hover:text-yellow-600" title="Edit Request">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button onclick="openDeleteRequestModal(${req.id}, '${req.product_name}')" class="text-red-500 hover:text-red-600" title="Delete Request">
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </div>
                        `;
                        container.appendChild(div);
                    });
                }
            });
    }

    function loadProductRequests() {
        console.log("loads product request")//debug
        fetch('/market/product_requests/')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('createRequestSection').querySelector('.grid');
                container.innerHTML = '';
                if (data.requests.length === 0) {
                    container.innerHTML = '<p class="text-gray-600 col-span-full">No product requests available.</p>';
                } else {
                    data.requests.forEach(req => {
                        const div = document.createElement('div');
                        div.className = 'bg-white shadow-md rounded-lg p-4';
                        div.innerHTML = `
                            <h3 class="text-lg font-semibold">${req.product_name}</h3>
                            <p class="text-gray-600">${req.quantity} ${req.unit}</p> 
                            <p class="text-gray-600">${req.description}</p>
                            <p class="text-gray-600">${req.location}</p>
                            <p class="text-gray-500 text-sm">Requested by @${req.requester}</p>
                            <p class="text-gray-500 text-sm">${req.created_at}</p>
                            <button onclick="openChatModal(null, '${req.product_name}', '', ${req.requester_id})" class="text-blue-500 hover:text-blue-600 mt-2" title="Message Requester">
                                <i class="fas fa-envelope"></i>
                            </button>
                        `;
                        container.appendChild(div);
                    });
                }
            });
    }

    // Tab Click Handlers for Requests
    document.getElementById('myRequestTab').addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active-tab', 'border-blue-600'));
        contents.forEach(c => c.classList.add('hidden'));
        document.getElementById('myRequestTab').classList.add('active-tab', 'border-blue-600');
        document.getElementById('myRequestSection').classList.remove('hidden');
        loadMyRequests();
    });

    const createRequestTab = document.getElementById('createRequestTab');
    if (createRequestTab) {
        createRequestTab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active-tab', 'border-blue-600'));
            contents.forEach(c => c.classList.add('hidden'));
            createRequestTab.classList.add('active-tab', 'border-blue-600');
            document.getElementById('createRequestSection').classList.remove('hidden');
            loadProductRequests();
        });
    }
// END OF PRODUCT REQUEST


    //Ensure DOM has loaded before calling certain function that handle different logic
    document.addEventListener("DOMContentLoaded", function () {
            //MESSAGING, when the send icon is sent executes first
            const messageForm = document.getElementById('messageForm');
            if (messageForm) {
                messageForm.addEventListener('submit', sendMessage); //calls sendMessage function
            } else {
                console.error("messageForm not found in the DOM.");
            }

            // LISTING FORM
            const listingForm = document.getElementById("listingForm");
            if (listingForm) {
                listingForm.addEventListener("submit", validateListingForm);
            } else {
                console.error("listingForm not found in the DOM.");
            }

            //Product Request
            const requestForm = document.getElementById('requestForm'); 
            if (requestForm) {
                requestForm.addEventListener("submit", submitRequestForm);
            } else {
                console.error("requestForm not found in the DOM.");
            }

            //MESSAGING FROM REQUESTS MADE 28TH CHANGE
            // Attach the handler (ensure this is inside your DOMContentLoaded listener)
            document.getElementById('messageForm').addEventListener('submit', handleMessageSubmit);



    });
 
    setInterval(loadConversations, 10000);    // Auto-refresh conversations every 10 seconds (optional)



</script>
{% endblock script %}





**********************************************************************************************************************************
VIEWS.PY
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

@login_required
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

# END OF 28 MODIFICATIONS

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



****************************************************************************************************************************
models.py
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import os
from Social.models import UserProfile
from storages.backends.gcloud import GoogleCloudStorage

# Create your models here.
# Table that store the requests made by users 
class ProductRequest(models.Model):
    requester = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='product_requests')
    product_name = models.CharField(max_length=100, blank=False)
    quantity = models.FloatField()
    unit = models.CharField(max_length=20, default="kg")
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product_name} requested by {self.requester.user.username}"

# For farmers product productproductListing
class productListing(models.Model):
    farmer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'farmer'})
    # product Category choices
    productCategoryChoices = (
        ('crop', 'Crop'),
        ('dairy', 'Dairy product'),
        ('meat', 'Meat product'),
    )
    productCategory = models.CharField(max_length=20, choices=productCategoryChoices, default='crop')    
    productName = models.CharField(max_length=100, blank=False)    
    quantity = models.FloatField()
    unit = models.CharField(max_length=20, default="kg")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='productListingsImages/', blank=True, null=True, storage=GoogleCloudStorage())

    # If location is not defined choose the deafult user loccation from farmers profile
    def save(self, *args, **kwargs):
        if not self.location:
            self.location = self.farmer.county
        super().save(*args, **kwargs)

    def get_image_url(self):
        # if image is uploaded fetch the image url 
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            # if image not uploaded then use the ones available in static
            product_image_name = self.productName.lower() + ".jpg"
            static_image_path = f"Images/crops/{product_image_name}"
            static_root = os.path.join(settings.STATICFILES_DIRS[0], static_image_path)
            if os.path.exists(static_root):
            
                return f"/static/Images/crops/{product_image_name}"
            return "/static/Images/crops/default.jpg"

    def __str__(self):#easy identification in admin tomatoes by akeyo
        return f"{self.productName} by {self.farmer.user.username}"

# Messaging feature module-for farmers a table to store messages
# class Message(models.Model):
#     sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_messages')
#     recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_messages')
#     listing = models.ForeignKey(productListing, on_delete=models.CASCADE, related_name='messages')
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Message from {self.sender.user.username} to {self.recipient.user.username} about {self.listing.productName}"

# farmers/models.py
class Message(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_messages')
    listing = models.ForeignKey(productListing, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.user.username} to {self.recipient.user.username}"

