{% extends "base2.html" %}
{% load widget_tweaks %}
{% load compress %}
{% load static %}
{% block content %}

{% if user.userprofile.role == 'farmer' %}
    {{ competitor_crop_pricing|json_script:"competitorCropPricing" }}
{% endif %}

<!-- Content filtration Error Displaying -->
{% if messages %}
    <div class="bg-teal-700 text-white p-4 rounded">
        {% for message in messages %}
            <p>{{ message }}</p>
        {% endfor %}
    </div>
{% endif %}

<div class="max-w-6xl mx-auto">
    <!-- Header -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <h1 class="text-3xl font-bold mb-6">{{ message }}</h1>
    <!-- Tabs and Messaging Icon -->
    <div class="flex border-b mb-6 items-center">
        <button id="dashboardTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-teal-700 focus:outline-none tab-button active-tab">Dashboard</button>        
        <button id="marketplaceTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-teal-700 focus:outline-none tab-button">Marketplace</button>
        {% if user.userprofile.role == 'farmer' %}
        <button id="myProductsTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-teal-700 focus:outline-none tab-button active-tab">Products(m)</button>
        <!-- <button id="createListingTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-teal-700 focus:outline-none tab-button">Create Listing</button> -->
        <button id="productRequestTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-teal-700 focus:outline-none tab-button">ProductRequests</button> 
        <!-- <button id="farmerOrdersTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-teal-700 focus:outline-none tab-button">Orders</button> -->
        {% endif %}              
        <div class="flex items-center gap-0 ml-auto">
            <!-- <button id="myOrdersTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-teal-700 focus:outline-none tab-button">MyOrders</button> -->
            <button id="myRequestTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-teal-700 focus:outline-none tab-button">MyRequests</button> 
            <!-- Question Mark Button (Product Request) -->
            <button id="requestButton" onclick="alert('Button clicked!');" class="px-4 py-2 text-teal-700 hover:text-gray-200" title="Product Request">
                <i class="fa-solid fa-circle-question fa-lg"></i>
            </button>
        
            <!-- Message Button (Message Farmer) -->
            <button onclick="alert('Button clicked! myProducts'); openChatModal()" class="px-4 py-2 text-teal-700 hover:text-gray-200" title="Message Farmer">
                <i class="fas fa-envelope fa-lg "></i>
            </button>
        </div>      
        
    </div>

    <!-- dashboard Tab -->
    <div id="dashboardSection" class="tab-content">
        {% if user.userprofile.role == 'farmer' and order_analytics %}
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">
                <!-- Left Column: Earnings, Competitor Analysis, Top Selling Products -->
                <div class="lg:col-span-3 space-y-6">
                    <!-- Earnings Card -->
                    <div class="bg-gradient-to-r from-teal-600 to-teal-800 text-white p-6 rounded-full shadow-lg flex flex-col items-center justify-center w-64 h-64 mx-auto transform hover:scale-105 transition-transform duration-300">
                        <h3 class="text-lg font-bold mb-2">Earnings</h3>
                        <div class="text-center">
                            <p class="text-sm font-semibold">Estimated</p>
                            <p class="text-xl font-bold">KES {{ earnings.estimated|floatformat:2 }}</p>
                            <p class="text-xs mt-1">From ongoing orders</p>
                        </div>
                        <div class="text-center mt-3">
                            <p class="text-sm font-semibold">Total</p>
                            <p class="text-xl font-bold">KES {{ earnings.total|floatformat:2 }}</p>
                            <p class="text-xs mt-1">From completed orders</p>
                        </div>
                    </div>

                    <!-- Competitor Analysis Card -->
                    <div class="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
                        <h3 class="text-xl font-semibold mb-3"><i class="fas fa-balance-scale mr-2 text-teal-700"></i>Competitor Analysis</h3>
                        <p class="text-gray-700">Avg. Competitor Price: <span class="font-semibold">KES {{ competitor_analysis.avg_price|floatformat:2 }}</span></p>
                        <p class="text-gray-700">Your Avg. Price: <span class="font-semibold">KES {{ competitor_analysis.my_avg_price|floatformat:2 }}</span></p>
                        <p class="text-gray-700">Competing Listings: <span class="font-semibold">{{ competitor_analysis.listing_count }}</span></p>
                    </div>

                    <!-- Top Selling Products Card (Clickable) -->
                    <div class="bg-white p-6 rounded-lg shadow-md cursor-pointer hover:shadow-lg transition-shadow duration-300" onclick="showTopProductsDetails()">
                        <h3 class="text-xl font-semibold mb-3"><i class="fas fa-star mr-2 text-teal-700"></i>Top Selling Products</h3>
                        {% if top_products %}
                            {% for product in top_products %}
                                <p class="text-gray-700 text-sm">{{ product.name }}: <span class="font-semibold">KES {{ product.revenue|floatformat:2 }}</span> ({{ product.quantity }} sold)</p>
                            {% endfor %}
                        {% else %}
                            <p class="text-sm text-gray-600">No sales yet.</p>
                        {% endif %}
                    </div>
                </div>

                <!-- Middle Section: Orders Made, Customer Engagement, Competitor Crop Pricing -->
                <div class="lg:col-span-9 space-y-6">
                    <!-- Top Row: Orders Made and Customer Engagement -->
                    <div class="flex flex-col lg:flex-row gap-6">
                        <!-- Orders Made Card -->
                        <div class="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 w-full lg:w-1/2">
                            <button id="farmerOrdersTab" class="w-full text-left text-xl font-semibold text-gray-700 hover:text-teal-700 focus:outline-none tab-button mb-3" onclick="showFarmerOrders()">
                                <i class="fas fa-shopping-cart mr-2 text-teal-700"></i>Orders Made
                            </button>
                            <p class="text-gray-700">New: <span class="font-semibold">{{ order_analytics.new }}</span></p>
                            <p class="text-gray-700">Pending: <span class="font-semibold">{{ order_analytics.pending }}</span></p>
                            <p class="text-gray-700">Confirmed: <span class="font-semibold">{{ order_analytics.confirmed }}</span></p>
                            <p class="text-gray-700">Completed: <span class="font-semibold">{{ order_analytics.completed }}</span></p>
                        </div>

                        <!-- Customer Engagement Card (Diamond Shape) -->
                        <div class="relative w-full lg:w-1/2">
                            <div class="bg-white p-6 shadow-md hover:shadow-lg transition-shadow duration-300 transform rotate-45 w-64 h-64 flex items-center justify-center mx-auto">
                                <div class="transform -rotate-45 text-center">
                                    <h3 class="text-xl font-semibold mb-3"><i class="fas fa-users mr-2 text-teal-700"></i>Customer Engagement</h3>
                                    <p class="text-gray-700">Unique Customers: <span class="font-semibold">{{ customer_engagement.unique_customers }}</span></p>
                                    <p class="text-gray-700">Unread Messages: <span class="font-semibold">{{ customer_engagement.unread_messages }}</span></p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Competitor Crop Pricing Graph (Middle, Wide, Short) -->
                    <div class="bg-white p-6 rounded-lg shadow-md">
                        <h3 class="text-xl font-semibold mb-3"><i class="fas fa-chart-bar mr-2 text-teal-700"></i>Competitor Crop Pricing</h3>
                        <div class="relative w-full h-[200px]">
                            <canvas id="competitorCropPricingChart"></canvas>
                            <p id="noPricingData" class="absolute inset-0 flex items-center justify-center text-gray-600 hidden">No pricing data available for your crops.</p>
                        </div>
                    </div>

                    <!-- My Orders Button (Bottom Right) -->
                    <div class="flex justify-end mt-4">
                        <button id="myOrdersTab" class="px-6 py-3 font-semibold text-white bg-teal-700 rounded-full hover:bg-teal-800 transition-colors duration-300 tab-button" onclick="showMyOrders()">My Orders</button>
                    </div>
                </div>
            </div>
        {% endif %}
    </div>

    <!-- myProducts Section PRODUCTS that i have created are in this section-->
    <div id="myProductsSection" class="tab-content">
        <div class="flex justify-end p-2">
            <button id="createListingTab" class="p-2 font-semibold text-white border-b-2 border-transparent hover:bg-teal-200 hover:text-black focus:outline-none tab-button bg-teal-700 rounded-xl">Create Listing</button>
        </div>
        {% if user.userprofile.role == 'farmer' %}                       
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

    <!-- Create a product Listing Section (for farmers only) -->
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
            <!-- Search form -->
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
                            <button onclick="alert('Button clicked! From MARKETPLACE'); openChatModal('{{ listing.id }}', '{{ listing.productName }}', '{{ listing.get_image_url }}', '{{ listing.farmer.id|default:0 }}')" class="text-blue-500 hover:text-blue-600" title="Message Farmer">
                                <i class="fas fa-envelope"></i>
                            </button>
                            <!-- Order Button -->
                            <button onclick="openOrderModal('{{ listing.id }}', '{{ listing.productName }}', '{{ listing.price }}', '{{ listing.quantity }}')" class="text-teal-700 hover:text-teal-800" title="Order Item">
                                <i class="fa-solid fa-cart-shopping"></i>
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
                    <button onclick="openEditRequestModal('{{ request.id }}', '{{ request.product_name }}', '{{ request.quantity }}', '{{ request.unit }}', '{{ request.description }}', '{{ request.location }}')" class="text-yellow-500 hover:text-yellow-600" title="Edit Request">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="openDeleteRequestModal('{{ request.id }}', '{{ request.product_name }}')" class="text-red-500 hover:text-red-600" title="Delete Request">
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
    <div id="productRequestSection" class="tab-content hidden">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {% for request in product_requests %}        
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

    <!-- Farmer Orders Section -->
    <div id="farmerOrdersSection" class="tab-content hidden">
        <h2 class="text-2xl font-semibold mb-4">Received Orders</h2>
        <table class="w-full bg-white shadow-md rounded-lg overflow-hidden">
            <thead class="bg-gray-200">
                <tr>
                    <th class="p-2 text-left">Date</th>
                    <th class="p-2 text-left">Requester</th>
                    <th class="p-2 text-left">Crop</th>
                    <th class="p-2 text-left">Quantity</th>
                    <th class="p-2 text-left">Total (KES)</th>
                    <th class="p-2 text-left">Location</th>
                    <th class="p-2 text-left">Status</th>
                </tr>
            </thead>
            <tbody id="farmerOrdersTable"></tbody>
        </table>
    </div>

    <!-- My Orders Section -->
    <div id="myOrdersSection" class="tab-content hidden">
        <h2 class="text-2xl font-semibold mb-4">My Orders</h2>
        <table class="w-full bg-white shadow-md rounded-lg overflow-hidden">
            <thead class="bg-gray-200">
                <tr>
                    <th class="p-2 text-left">Farmer</th>
                    <th class="p-2 text-left">Crop</th>
                    <th class="p-2 text-left">Date</th>
                    <th class="p-2 text-left">Quantity</th>
                    <th class="p-2 text-left">Total (KES)</th>
                    <th class="p-2 text-left">Status</th>
                    <th class="p-2 text-left">Action</th>
                </tr>
            </thead>
            <tbody id="myOrdersTable"></tbody>
        </table>
    </div>
    
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

    <!-- Order Modal -->
    <div id="orderModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center hidden">
        <div class="bg-white p-6 rounded-lg w-full max-w-md">
            <h2 class="text-xl font-semibold mb-4">Place Order</h2>
            <form id="orderForm">
                <div class="mb-4">
                    <label class="block text-gray-700">Crop</label>
                    <input id="orderCrop" type="text" class="w-full p-2 border rounded" readonly>
                </div>
                <div class="mb-4">
                    <label class="block text-gray-700">Quantity</label>
                    <input id="orderQuantity" type="number" step="0.01" min="0" class="w-full p-2 border rounded" required>
                </div>
                <div class="mb-4">
                    <label class="block text-gray-700">Total Price (KES)</label>
                    <input id="orderTotal" type="text" class="w-full p-2 border rounded" readonly>
                </div>
                <div class="mb-4">
                    <label class="block text-gray-700">Location (County)</label>
                    <input id="orderLocation" type="text" class="w-full p-2 border rounded" required>
                </div>
                <div class="flex justify-end gap-2">
                    <button type="button" onclick="closeOrderModal()" class="px-4 py-2 bg-gray-300 rounded">Cancel</button>
                    <button type="submit" class="px-4 py-2 bg-teal-700 text-white rounded">Order</button>
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

    // Search functions for marketPlace 
    const marketplaceSearchInput = document.querySelector('input[name="marketplace_query"]');
    if (marketplaceSearchInput) {
        marketplaceSearchInput.addEventListener('input', debounce(function() {
            document.querySelector('#marketplaceSection form').submit();
        }, 500));
    }

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
      
    // PRODUCT REQUEST Functions    
    function openRequestModal() {
        document.getElementById('requestModal').classList.remove('hidden');
    }
    function closeRequestModal() {
        document.getElementById('requestModal').classList.add('hidden');
        document.getElementById('requestForm').reset();
    }
  
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
    function editRequest(event){
        event.preventDefault();
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
    }
    // Delete Request Modal Functions
    function openDeleteRequestModal(id, productName) {
        document.getElementById('deleteRequestModal').classList.remove('hidden');
        document.getElementById('deleteRequestId').value = id;
        document.getElementById('deleteRequestProductName').textContent = productName;
    }
    function closeDeleteRequestModal() {
        document.getElementById('deleteRequestModal').classList.add('hidden');
    }
    //Producr request deletion function
    function deleteRequest(event) {
        event.preventDefault();
        
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
    }
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
                const container = document.getElementById('productRequestSection').querySelector('.grid');
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

    // END OF PRODUCT REQUEST

    // ORDERS
    let currentListingId = null;
        function openOrderModal(listingId, productName, price, maxQuantity) {
            currentListingId = listingId;
            document.getElementById('orderCrop').value = productName;
            document.getElementById('orderQuantity').max = maxQuantity;
            document.getElementById('orderQuantity').addEventListener('input', () => {
                const quantity = parseFloat(document.getElementById('orderQuantity').value) || 0;
                document.getElementById('orderTotal').value = (quantity * price).toFixed(2);
            });
            document.getElementById('orderModal').classList.remove('hidden');
        }

        function closeOrderModal() {
            document.getElementById('orderModal').classList.add('hidden');
            document.getElementById('orderForm').reset();
            currentListingId = null;
        }

        document.getElementById('orderForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const quantity = parseFloat(document.getElementById('orderQuantity').value);
            const location = document.getElementById('orderLocation').value;
            const response = await fetch('/market/createOrder/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
                body: JSON.stringify({ listing_id: currentListingId, quantity, location }),
            });
            const data = await response.json();
            if (data.status === 'success') {
                alert('Order placed successfully!');
                closeOrderModal();
            } else {
                alert(data.message);
            }
        });

        // Farmer Orders
        async function showFarmerOrders() {
            const response = await fetch('/market/farmerOrders/');
            const data = await response.json();
            const tbody = document.getElementById('farmerOrdersTable');
            tbody.innerHTML = '';
            data.orders.forEach(order => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="p-2">${order.date}</td>
                    <td class="p-2">${order.requester}</td>
                    <td class="p-2">${order.crop}</td>
                    <td class="p-2">${order.quantity}</td>
                    <td class="p-2">${order.total.toFixed(2)}</td>
                    <td class="p-2">${order.location}</td>
                    <td class="p-2">
                        <select onchange="updateOrderStatus(${order.id}, this.value)" class="p-1 border rounded">
                            <option value="new" ${order.status === 'new' ? 'selected' : ''}>New</option>
                            <option value="pending" ${order.status === 'pending' ? 'selected' : ''}>Pending</option>
                            <option value="confirmed" ${order.status === 'confirmed' ? 'selected' : ''}>Confirmed</option>
                            <option value="completed" ${order.status === 'completed' ? 'selected' : ''}>Completed</option>
                        </select>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        async function updateOrderStatus(orderId, status) {
            const response = await fetch(`/market/updateOrderStatus/${orderId}/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
                body: JSON.stringify({ status }),
            });
            const data = await response.json();
            if (data.status !== 'success') alert(data.message);
        }

        // My Orders
        async function showMyOrders() {
            const response = await fetch('/market/myOrders/');
            const data = await response.json();
            const tbody = document.getElementById('myOrdersTable');
            tbody.innerHTML = '';
            data.orders.forEach(order => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="p-2">${order.farmer}</td>
                    <td class="p-2">${order.crop}</td>
                    <td class="p-2">${order.date}</td>
                    <td class="p-2">${order.quantity}</td>
                    <td class="p-2">${order.total.toFixed(2)}</td>
                    <td class="p-2">${order.status}</td>
                    <td class="p-2">
                        ${order.can_delete ? `<button onclick="deleteOrder(${order.id})" class="text-red-600"><i class="fas fa-trash"></i></button>` : ''}
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        async function deleteOrder(orderId) {
            if (confirm('Are you sure you want to delete this order?')) {
                const response = await fetch(`/market/deleteOrder/${orderId}/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
                });
                const data = await response.json();
                if (data.status === 'success') {
                    showMyOrders();
                    alert('Order deleted successfully!');
                } else {
                    alert(data.message);
                }
            }
        }

        // CSRF Token Helper (ensure this is available in your template or via Django)
        function getCsrfToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]').value;
        }
    

    // ORDERS

    // Dashboard functions
    // New: Competitor Crop Pricing Chart Logic
    function initializeCompetitorCropPricingChart() {
        const ctx = document.getElementById('competitorCropPricingChart')?.getContext('2d');
        const noDataMessage = document.getElementById('noPricingData');

        if (!ctx) {
            console.error("Canvas element 'competitorCropPricingChart' not found.");
            return;
        }

        const competitorCropPricingElement = document.getElementById('competitorCropPricing');
        if (!competitorCropPricingElement) {
            console.error("Competitor crop pricing data element not found.");
            if (noDataMessage) noDataMessage.classList.remove('hidden');
            return;
        }

        const competitorCropPricing = JSON.parse(competitorCropPricingElement.textContent || '{}');
        if (!competitorCropPricing || Object.keys(competitorCropPricing).length === 0) {
            console.warn("No competitor pricing data available.");
            if (noDataMessage) noDataMessage.classList.remove('hidden');
            return;
        }

        // Prepare chart data
        const crops = Object.keys(competitorCropPricing);
        const allFarmers = new Set();
        crops.forEach(crop => {
            Object.keys(competitorCropPricing[crop]).forEach(farmer => allFarmers.add(farmer));
        });
        const farmerLabels = Array.from(allFarmers);

        const datasets = crops.map((crop, index) => {
            const prices = farmerLabels.map(farmer => competitorCropPricing[crop][farmer] || 0);
            return {
                label: crop,
                data: prices,
                backgroundColor: `rgba(${75 + index * 50 % 255}, ${192 - index * 20 % 255}, ${175 - index * 30 % 255}, 0.7)`,
                borderColor: `rgba(${75 + index * 50 % 255}, ${192 - index * 20 % 255}, ${175 - index * 30 % 255}, 1)`,
                borderWidth: 1,
            };
        });

        // Destroy existing chart if it exists to prevent overlap
        if (window.competitorCropPricingChart instanceof Chart) {
            window.competitorCropPricingChart.destroy();
        }

        window.competitorCropPricingChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: farmerLabels,
                datasets: datasets,
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Price (KES)' },
                        ticks: {
                            callback: value => `KES ${value}`,
                        },
                    },
                    x: {
                        title: { display: true, text: 'Farmers' },
                    },
                },
                plugins: {
                    legend: { position: 'top' },
                    // title: {
                    //     display: true,
                    //     text: `Crop Pricing Comparison in ${userCounty || 'Your County'}`, // userCounty should be passed from Django
                    // },
                    tooltip: {
                        callbacks: {
                            label: context => `${context.dataset.label}: KES ${context.raw.toFixed(2)}`,
                        },
                    },
                },
            },
        });

        if (noDataMessage) noDataMessage.classList.add('hidden');
    }


    //Ensure DOM has loaded before calling certain function that handle different logic
    document.addEventListener("DOMContentLoaded", function () {
          
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

            // Request button
            document.getElementById('requestButton').addEventListener('click', () => openRequestModal());
            //Handle messages            
            document.getElementById('messageForm').addEventListener('submit', handleMessageSubmit);
            //Handles product request deletion
            document.getElementById('deleteRequestForm').addEventListener('submit', deleteRequest);
            // Handles productRequest edit
            document.getElementById('editRequestForm').addEventListener('submit', editRequest);

             // Initial Tab ORDERS
            document.getElementById('dashboardTab').click();

            // Chart
           // Initialize the new chart
           {% if user.userprofile.role == 'farmer' %}
                if (document.getElementById('competitorCropPricing')) {
                    initializeCompetitorCropPricingChart();
                } else {
                    console.error("competitorCropPricing element not found at DOM load time.");
                }
            {% endif %}
                    
            
      
    });
 
   // setInterval(loadConversations, 10000);    // Auto-refresh conversations every 10 seconds (optional) you will uncomment this 
</script>
{% endblock script %}