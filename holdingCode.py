{% extends "base2.html" %}
{% load widget_tweaks %}
{% load compress %}
{% load static %}
{% load tz %}

{% block content %}
{% if user.userprofile.role == 'farmer' %}
    {{ competitor_crop_pricing|json_script:"competitorCropPricing" }}
{% endif %}

<!-- Messages (Alerts) -->
{% if messages %}
    <div class="bg-teal-600 text-white p-4 rounded-2xl shadow-lg mb-6 mx-auto max-w-6xl">
        {% for message in messages %}
            <p class="text-sm">{{ message }}</p>
        {% endfor %}
    </div>
{% endif %}


<!-- Main Container -->
<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 "> 
    <!-- Header -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <h1 class="text-3xl font-bold text-teal-800 mb-6">{{ message }}</h1>

    <!-- Tabs and Icons -->
    <div class="flex items-center border-b-2 border-teal-200 mb-6">
        <div class="flex flex-wrap gap-2">
            <button id="dashboardTab" class="px-4 py-2 font-semibold text-teal-700 border-b-2 border-transparent hover:border-teal-600 focus:outline-none tab-button active-tab transition duration-300 rounded-t-lg">Dashboard</button>
            <button id="marketplaceTab" class="px-4 py-2 font-semibold text-teal-700 border-b-2 border-transparent hover:border-teal-600 focus:outline-none tab-button transition duration-300 rounded-t-lg">Marketplace</button>
            {% if user.userprofile.role == 'farmer' %}
                <button id="myProductsTab" class="px-4 py-2 font-semibold text-teal-700 border-b-2 border-transparent hover:border-teal-600 focus:outline-none tab-button transition duration-300 rounded-t-lg">My Products</button>
                <button id="productRequestTab" class="px-4 py-2 font-semibold text-teal-700 border-b-2 border-transparent hover:border-teal-600 focus:outline-none tab-button transition duration-300 rounded-t-lg">Product Requests</button>
            {% endif %}
            <button id="myRequestTab" class="px-4 py-2 font-semibold text-teal-700 border-b-2 border-transparent hover:border-teal-600 focus:outline-none tab-button transition duration-300 rounded-t-lg">My Requests</button>
        </div>
        <div class="ml-auto flex items-center gap-4">
            <button id="requestButton" class="p-2 text-teal-700 hover:bg-teal-100 rounded-full transition duration-300" title="Product Request">
                <i class="fa-solid fa-circle-question fa-lg"></i>
            </button>
            <button onclick="openChatModal()" class="p-2 text-teal-700 hover:bg-teal-100 rounded-full transition duration-300" title="Message Farmer">
                <i class="fas fa-envelope fa-lg"></i>
            </button>
        </div>
    </div>

    <!-- Dashboard Tab -->
    <div id="dashboardSection" class="tab-content">
        {% if user.userprofile.role == 'farmer' and order_analytics %}
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">
                <!-- Left Column -->
                <div class="lg:col-span-3 space-y-6">
                    <!-- Earnings Card -->
                    <div class="bg-gradient-to-r from-teal-600 to-teal-800 text-white p-6 rounded-2xl shadow-lg flex flex-col items-center justify-center transform hover:scale-105 transition-transform duration-300">
                        <h3 class="text-lg font-bold mb-2">Earnings</h3>
                        <div class="text-center">
                            <p class="text-sm font-semibold">Estimated</p>
                            <p class="text-xl font-bold">KES {{ earnings.estimated|floatformat:2 }}</p>
                            <p class="text-xs mt-1">From ongoing orders</p>
                        </div>
                        <div class="text-center mt-4">
                            <p class="text-sm font-semibold">Total</p>
                            <p class="text-xl font-bold">KES {{ earnings.total|floatformat:2 }}</p>
                            <p class="text-xs mt-1">From completed orders</p>
                        </div>
                    </div>

                    <!-- Competitor Analysis Card -->
                    <div class="bg-white p-4 rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-300">
                        <h3 class="text-xl font-semibold mb-3 text-teal-800"><i class="fas fa-balance-scale mr-2 text-teal-600"></i>Competitor Analysis</h3>
                        <p class="text-gray-700">Avg. Competitor Price: <span class="font-semibold text-teal-600">KES {{ competitor_analysis.avg_price|floatformat:2 }}</span></p>
                        <p class="text-gray-700">Your Avg. Price: <span class="font-semibold text-teal-600">KES {{ competitor_analysis.my_avg_price|floatformat:2 }}</span></p>
                        <p class="text-gray-700">Competing Listings: <span class="font-semibold text-teal-600">{{ competitor_analysis.listing_count }}</span></p>
                    </div>

                    <!-- Top Selling Products Card -->
                    <div class="bg-white p-4 rounded-2xl shadow-md cursor-pointer hover:shadow-lg transition-shadow duration-300" onclick="showTopProductsDetails()">
                        <h3 class="text-xl font-semibold mb-3 text-teal-800"><i class="fas fa-star mr-2 text-teal-600"></i>Top Selling Products</h3>
                        {% if top_products %}
                            {% for product in top_products %}
                                <p class="text-gray-700 text-sm">{{ product.name }}: <span class="font-semibold text-teal-600">KES {{ product.revenue|floatformat:2 }}</span> ({{ product.quantity }} sold)</p>
                            {% endfor %}
                        {% else %}
                            <p class="text-sm text-gray-600">No sales yet.</p>
                        {% endif %}
                    </div>
                </div>

                <!-- Middle Section -->
                <div class="lg:col-span-9 space-y-6">
                    <!-- Top Row -->
                    <div class="flex flex-col lg:flex-row gap-6">
                        <!-- Orders Made Card -->
                        <div class="bg-white p-4 rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-300 w-full lg:w-1/2">
                            <button id="farmerOrdersTab" class="w-full text-left text-xl font-semibold text-teal-800 hover:text-teal-600 focus:outline-none tab-button mb-3" onclick="showFarmerOrders()">
                                <i class="fas fa-shopping-cart mr-2 text-teal-600"></i>Orders Made
                            </button>
                            <p class="text-gray-700">New: <span class="font-semibold text-teal-600">{{ order_analytics.new }}</span></p>
                            <p class="text-gray-700">Pending: <span class="font-semibold text-teal-600">{{ order_analytics.pending }}</span></p>
                            <p class="text-gray-700">Confirmed: <span class="font-semibold text-teal-600">{{ order_analytics.confirmed }}</span></p>
                            <p class="text-gray-700">Completed: <span class="font-semibold text-teal-600">{{ order_analytics.completed }}</span></p>
                        </div>

                        <!-- Customer Engagement Card -->
                        <div class="bg-gradient-to-r from-teal-600 to-teal-800 text-white p-4 rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-300 w-full lg:w-1/2">
                            <h3 class="text-xl font-semibold mb-3 text-white"><i class="fas fa-users mr-2"></i>Customer Engagement</h3>
                            <p>Unique Customers: <span class="font-semibold">{{ customer_engagement.unique_customers }}</span></p>
                            <p>Unread Messages: <span class="font-semibold">{{ customer_engagement.unread_messages }}</span></p>
                        </div>
                    </div>

                    <!-- Competitor Crop Pricing Graph -->
                    <div class="bg-white p-6 rounded-2xl shadow-md">
                        <h3 class="text-xl font-semibold mb-3 text-teal-800"><i class="fas fa-chart-bar mr-2 text-teal-600"></i>Competitor Crop Pricing</h3>
                        <div class="relative w-full h-[200px]">
                            <canvas id="competitorCropPricingChart"></canvas>
                            <p id="noPricingData" class="absolute inset-0 flex items-center justify-center text-gray-600 hidden">No pricing data available for your crops.</p>
                        </div>
                    </div>

                    <!-- My Orders Button -->
                    <div class="flex justify-end mt-4">
                        <button id="myOrdersTab" class="px-6 py-3 font-semibold text-white bg-teal-700 rounded-full hover:bg-teal-800 transition-colors duration-300 tab-button" onclick="showMyOrders()">My Orders</button>
                    </div>
                </div>
            </div>
        {% endif %}
    </div>

    <!-- My Products Section -->
    <div id="myProductsSection" class="tab-content hidden">
        <div class="flex justify-end p-2">
            <button id="createListingTab" class="px-4 py-2 font-semibold text-white bg-teal-700 rounded-xl hover:bg-teal-600 transition duration-300 tab-button">Create Listing</button>
        </div>
        {% if user.userprofile.role == 'farmer' %}
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                {% if listings %}
                    {% for listing in listings %}
                        <div class="bg-white shadow-md rounded-lg overflow-hidden flex flex-col h-[19rem] hover:shadow-lg transition-shadow duration-300">
                            <div class="h-40 w-full overflow-hidden">
                                <img src="{{ listing.get_image_url }}" alt="{{ listing.productName }}" class="w-full h-full object-cover hover:scale-105 transition-transform duration-300">
                            </div>
                            <div class="p-4 flex flex-col flex-grow">
                                <h2 class="text-lg font-semibold text-teal-800 line-clamp-1">{{ listing.productName }}</h2>
                                <p class="text-gray-500 text-sm">{{ listing.get_productCategory_display }}</p>
                                <div class="mt-2">
                                    <p class="text-gray-700 font-bold">KES {{ listing.price }} / {{ listing.unit }}</p>
                                    <p class="text-gray-500 text-sm">Qty Left: {{ listing.quantity }} {{ listing.unit }}</p>
                                    <p class="text-gray-500 text-sm">{{ listing.location }}</p>
                                </div>
                                <p class="text-sm text-gray-600 mt-2 line-clamp-2 flex-grow">{{ listing.description }}</p>
                                <div class="mt-2 flex items-center justify-between">
                                    <form method="POST" action="{% url 'toggle_availability' listing.id %}" class="flex items-center">
                                        {% csrf_token %}
                                        <label class="relative inline-flex items-center cursor-pointer">
                                            <input type="checkbox" name="is_available" {% if listing.is_available %}checked{% endif %} class="sr-only peer" onchange="this.form.submit()">
                                            <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:bg-teal-600 transition-colors duration-200"></div>
                                            <div class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform duration-200 peer-checked:translate-x-5"></div>
                                        </label>
                                        <span class="ml-2 text-sm font-semibold {% if listing.is_available %}text-teal-600{% else %}text-red-600{% endif %}">
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

                                <p class="text-gray-500 text-sm">Listed: {{ listing.created_at|localtime|date:"Y-m-d H:i:s" }}</p>
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

    <!-- Create Listing Section -->
    <div id="createListingSection" class="tab-content hidden">
        {% if user.userprofile.role == 'farmer' %}
            <div class="bg-white p-6 rounded-2xl shadow-lg w-full">
                <h2 class="text-2xl font-bold mb-4 text-center text-teal-800">Create a New Listing</h2>
                <form method="POST" id="listingForm" class="space-y-4" enctype="multipart/form-data">
                    {% csrf_token %}
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Product Category</label>
                        {{ form.productCategory|add_class:"w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Product Name</label>
                        {{ form.productName|add_class:"w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Quantity</label>
                        {{ form.quantity|add_class:"w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Unit (e.g., kg)</label>
                        {{ form.unit|add_class:"w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Price (per unit)</label>
                        {{ form.price|add_class:"w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Description</label>
                        {{ form.description|add_class:"w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Location</label>
                        {{ form.location|add_class:"w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Upload Image (Optional)</label>
                        {{ form.image|add_class:"w-full p-2 border rounded-md" }}
                        <p class="text-sm text-gray-500 mt-1">If no image is uploaded, a default image will be used.</p>
                    </div>
                    <button type="submit" class="w-full bg-teal-700 text-white p-2 rounded-md hover:bg-teal-800 transition duration-300">Create Listing</button>
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
                    <input type="text" name="marketplace_query" value="{{ request.GET.marketplace_query }}" placeholder="Search marketplace by product name..." class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500">
                </div>
                <div class="flex items-end space-x-2">
                    <button type="submit" class="bg-teal-700 text-white p-2 rounded-md hover:bg-teal-600 transition duration-300">
                        <i class="fas fa-search"></i>
                    </button>
                    <a href="{% url 'main' %}" class="bg-gray-200 text-gray-700 p-2 rounded-md hover:bg-gray-300 transition duration-300" title="Clear Search">
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
                    <div class="bg-white shadow-md rounded-lg overflow-hidden flex flex-col h-[19rem] hover:shadow-lg transition-shadow duration-300">
                        <div class="h-40 w-full overflow-hidden">
                            <img src="{{ listing.get_image_url }}" alt="{{ listing.productName }}" class="w-full h-full object-cover hover:scale-105 transition-transform duration-300">
                        </div>
                        <div class="p-4 flex flex-col flex-grow">
                            <p class="text-gray-500 text-sm">{{ listing.get_productCategory_display }}</p>
                            <h2 class="text-lg font-semibold text-teal-800 line-clamp-1">{{ listing.productName }}</h2>
                            <p class="text-gray-500 text-sm">by @{{ listing.farmer.user.username }}</p>
                            <div class="mt-2">
                                <p class="text-gray-700 font-bold">KES {{ listing.price }} / {{ listing.unit }}</p>
                                <p class="text-gray-700 font-bold">Qty Left: {{ listing.quantity }}{{ listing.unit }}</p>
                                <p class="text-gray-500 text-sm">{{ listing.location }}</p>
                            </div>
                            <p class="text-sm text-gray-600 mt-2 line-clamp-2 flex-grow">{{ listing.description }}</p>
                            <div class="mt-2 flex items-center justify-between">
                                <span class="text-sm font-semibold {% if listing.is_available %}text-teal-600{% else %}text-red-600{% endif %}">
                                    {% if listing.is_available %}Available{% else %}Sold Out{% endif %}
                                </span>
                                <button onclick="openChatModal('{{ listing.id }}', '{{ listing.productName }}', '{{ listing.get_image_url }}', '{{ listing.farmer.id|default:0 }}')" class="text-teal-700 hover:text-teal-800" title="Message Farmer">
                                    <i class="fas fa-envelope"></i>
                                </button>
                                <button onclick="openOrderModal('{{ listing.id }}', '{{ listing.productName }}', '{{ listing.price }}', '{{ listing.quantity }}')" class="text-teal-700 hover:text-teal-800" title="Order Item">
                                    <i class="fa-solid fa-cart-shopping"></i>
                                </button>
                            </div>
                            <p class="text-gray-500 text-sm">Listed: {{ listing.created_at|localtime|date:"Y-m-d H:i:s" }}</p>
                        </div>
                    </div>
                {% endfor %}
            {% else %}
                <p class="text-gray-600 col-span-full">No listings found in the marketplace.</p>
            {% endif %}
        </div>
    </div>

    <!-- My Requests Section -->
    <div id="myRequestSection" class="tab-content hidden">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {% for request in my_requests %}
                <div class="bg-white shadow-md rounded-lg p-4 hover:shadow-lg transition-shadow duration-300">
                    <h3 class="text-lg font-semibold text-teal-800">{{ request.product_name }}</h3>
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

    <!-- Product Requests Section (Farmers Only) -->
    <div id="productRequestSection" class="tab-content hidden">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {% for request in product_requests %}
                <div class="bg-white shadow-md rounded-lg p-4 hover:shadow-lg transition-shadow duration-300">
                    <h3 class="text-lg font-semibold text-teal-800">{{ request.product_name }}</h3>
                    <p class="text-gray-600">{{ request.quantity }} {{ request.unit }}</p>
                    <p class="text-gray-600">{{ request.description }}</p>
                    <p class="text-gray-600">{{ request.location }}</p>
                    <p class="text-gray-500 text-sm">Requested by @{{ request.requester.user.username }}</p>
                    <p class="text-gray-500 text-sm">{{ request.created_at }}</p>
                    <button onclick="openChatModal(null, '{{ request.product_name }}', '', '{{ request.requester.id }}')" class="text-teal-700 hover:text-teal-800 mt-2" title="Message Requester">
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
        <h2 class="text-2xl font-semibold mb-4 text-teal-800">Received Orders</h2>
        <div class="bg-white shadow-md rounded-lg overflow-hidden">
            <table class="w-full">
                <thead class="bg-teal-100">
                    <tr>
                        <th class="p-2 text-left text-teal-800">Date</th>
                        <th class="p-2 text-left text-teal-800">Requester</th>
                        <th class="p-2 text-left text-teal-800">Crop</th>
                        <th class="p-2 text-left text-teal-800">Quantity</th>
                        <th class="p-2 text-left text-teal-800">Total (KES)</th>
                        <th class="p-2 text-left text-teal-800">Location</th>
                        <th class="p-2 text-left text-teal-800">Status</th>
                    </tr>
                </thead>
                <tbody id="farmerOrdersTable" class="text-gray-700"></tbody>
            </table>
        </div>
    </div>

    <!-- My Orders Section -->
    <div id="myOrdersSection" class="tab-content hidden">
        <h2 class="text-2xl font-semibold mb-4 text-teal-800">My Orders</h2>
        <div class="bg-white shadow-md rounded-lg overflow-hidden">
            <table class="w-full">
                <thead class="bg-teal-100">
                    <tr>
                        <th class="p-2 text-left text-teal-800">Farmer</th>
                        <th class="p-2 text-left text-teal-800">Crop</th>
                        <th class="p-2 text-left text-teal-800">Date</th>
                        <th class="p-2 text-left text-teal-800">Quantity</th>
                        <th class="p-2 text-left text-teal-800">Total (KES)</th>
                        <th class="p-2 text-left text-teal-800">Status</th>
                        <th class="p-2 text-left text-teal-800">Action</th>
                    </tr>
                </thead>
                <tbody id="myOrdersTable" class="text-gray-700"></tbody>
            </table>
        </div>
    </div>
</div>


{% endblock content %}

{% block modalsContent %}
    <!-- Edit Modal -->
    <!-- Edit Modal 2-->
    <div id="editModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center hidden z-50">
        <div class="bg-white p-6 rounded-2xl shadow-lg w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h2 class="text-2xl font-bold mb-4 text-teal-800">Edit Listing</h2>
            <form id="editForm" method="POST" enctype="multipart/form-data" class="space-y-4" action="/market/edit/{{ listing.id }}/">
                {% csrf_token %}
                <input type="hidden" name="listing_id" id="editListingId">
                <div>
                    <label class="block text-sm font-medium text-gray-700">Product Category</label>
                    {{ form.productCategory|add_class:"w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" }}
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Product Name</label>
                    <input type="text" name="productName" id="editProductName" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Quantity</label>
                    <input type="number" name="quantity" id="editQuantity" step="0.01" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Unit (e.g., kg)</label>
                    <input type="text" name="unit" id="editUnit" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Price (per unit)</label>
                    <input type="number" name="price" id="editPrice" step="0.01" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Description</label>
                    <textarea name="description" id="editDescription" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500"></textarea>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Location</label>
                    <input type="text" name="location" id="editLocation" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Upload Image (Optional)</label>
                    <input type="file" name="image" id="editImage" class="w-full p-2 border rounded-md">
                    <p class="text-sm text-gray-500 mt-1">Current Image: <img id="editCurrentImage" src="" alt="Current Image" class="w-16 h-16 object-cover rounded inline-block ml-2"></p>
                    <label class="mt-2 flex items-center">
                        <input type="checkbox" name="clear_image" id="editClearImage" class="mr-2">
                        <span class="text-sm text-gray-700">Clear current image</span>
                    </label>
                </div>
                <div class="flex space-x-4">
                    <button type="submit" class="w-full bg-teal-700 text-white p-2 rounded-md hover:bg-teal-800 transition duration-300">Save Changes</button>
                    <button type="button" onclick="closeEditModal()" class="w-full bg-gray-500 text-white p-2 rounded-md hover:bg-gray-600 transition duration-300">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Delete Modal -->
    <div id="deleteModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center hidden z-50">
        <div class="bg-white p-6 rounded-2xl shadow-lg w-full max-w-md">
            <h2 class="text-2xl font-bold mb-4 text-teal-800">Delete Listing</h2>
            <p class="text-lg mb-4">Are you sure you want to delete <strong id="deleteProductName"></strong>?</p>
            <p class="text-gray-600 mb-4">This action cannot be undone.</p>
            <form id="deleteForm" method="POST">
                {% csrf_token %}
                <input type="hidden" name="listing_id" id="deleteListingId">
                <div class="flex space-x-4">
                    <button type="submit" class="w-full bg-red-500 text-white p-2 rounded-md hover:bg-red-600 transition duration-300">Yes, Delete</button>
                    <button type="button" onclick="closeDeleteModal()" class="w-full bg-gray-500 text-white p-2 rounded-md hover:bg-gray-600 transition duration-300">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Chat Modal -->
    <div id="chatModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center hidden z-50">
        <div class="bg-white p-6 rounded-2xl shadow-lg w-full max-w-2xl max-h-[90vh] flex flex-col">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-xl font-bold text-teal-800">Messages</h2>
                <button onclick="closeChatModal()" class="text-gray-500 hover:text-gray-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div id="chatContainer" class="flex flex-1 overflow-hidden">
                <div id="conversationsList" class="w-1/3 border-r overflow-y-auto max-h-[70vh] bg-teal-50 p-2">
                    <div id="conversationItems" class="space-y-2"></div>
                </div>
                <div id="chatArea" class="w-2/3 flex flex-col hidden">
                    <div id="chatHeader" class="p-2 border-b flex items-center bg-teal-100">
                        <img id="chatListingImage" src="" alt="Listing" class="w-10 h-10 object-cover rounded mr-2" data-has-image="false">
                        <div>
                            <h3 id="chatListingName" class="font-semibold text-teal-800"></h3>
                            <p id="chatOtherUser" class="text-sm text-gray-500"></p>
                        </div>
                    </div>
                    <div id="messagesContainer" class="flex-1 p-4 overflow-y-auto max-h-[50vh]"></div>
                    <form id="messageForm" class="p-2 border-t">
                        <input type="hidden" id="chatListingId" name="listing_id">
                        <input type="hidden" id="chatRecipientId" name="recipient_id">
                        <div class="flex space-x-2">
                            <input type="text" id="messageInput" class="flex-1 p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" placeholder="Type a message...">
                            <button type="submit" class="bg-teal-700 text-white p-2 rounded-md hover:bg-teal-800 transition duration-300">
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
        <div class="bg-white p-6 rounded-2xl shadow-lg w-full max-w-md">
            <h2 class="text-2xl font-bold mb-4 text-teal-800">Request a Product</h2>
            <form id="requestForm" class="space-y-4">
                {% csrf_token %}
                <div>
                    <label class="block text-sm font-medium text-gray-700">Product Name</label>
                    <input type="text" id="requestProductName" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" required>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Quantity</label>
                    <input type="number" id="requestQuantity" step="0.01" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" required>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Unit (e.g., kg)</label>
                    <input type="text" id="requestUnit" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" value="kg">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Description (Optional)</label>
                    <textarea id="requestDescription" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500"></textarea>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Location</label>
                    <input type="text" id="requestLocation" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" required>
                </div>
                <div class="flex space-x-4">
                    <button type="submit" class="w-full bg-teal-700 text-white p-2 rounded-md hover:bg-teal-800 transition duration-300">Submit Request</button>
                    <button type="button" onclick="closeRequestModal()" class="w-full bg-gray-500 text-white p-2 rounded-md hover:bg-gray-600 transition duration-300">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Edit Request Modal -->
    <div id="editRequestModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center hidden z-50">
        <div class="bg-white p-6 rounded-2xl shadow-lg w-full max-w-md">
            <h2 class="text-2xl font-bold mb-4 text-teal-800">Edit Request</h2>
            <form id="editRequestForm" class="space-y-4">
                {% csrf_token %}
                <input type="hidden" id="editRequestId">
                <div>
                    <label class="block text-sm font-medium text-gray-700">Product Name</label>
                    <input type="text" id="editRequestProductName" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" required>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Quantity</label>
                    <input type="number" id="editRequestQuantity" step="0.01" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" required>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Unit (e.g., kg)</label>
                    <input type="text" id="editRequestUnit" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Description (Optional)</label>
                    <textarea id="editRequestDescription" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500"></textarea>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Location</label>
                    <input type="text" id="editRequestLocation" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" required>
                </div>
                <div class="flex space-x-4">
                    <button type="submit" class="w-full bg-teal-700 text-white p-2 rounded-md hover:bg-teal-800 transition duration-300">Save Changes</button>
                    <button type="button" onclick="closeEditRequestModal()" class="w-full bg-gray-500 text-white p-2 rounded-md hover:bg-gray-600 transition duration-300">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Delete Request Modal -->
    <div id="deleteRequestModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center hidden z-50">
        <div class="bg-white p-6 rounded-2xl shadow-lg w-full max-w-md">
            <h2 class="text-2xl font-bold mb-4 text-teal-800">Delete Request</h2>
            <p class="text-lg mb-4">Are you sure you want to delete <strong id="deleteRequestProductName"></strong>?</p>
            <p class="text-gray-600 mb-4">This action cannot be undone.</p>
            <form id="deleteRequestForm" method="POST">
                {% csrf_token %}
                <input type="hidden" id="deleteRequestId">
                <div class="flex space-x-4">
                    <button type="submit" class="w-full bg-red-500 text-white p-2 rounded-md hover:bg-red-600 transition duration-300">Yes, Delete</button>
                    <button type="button" onclick="closeDeleteRequestModal()" class="w-full bg-gray-500 text-white p-2 rounded-md hover:bg-gray-600 transition duration-300">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Order Modal -->
    <div id="orderModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center hidden z-50">
        <div class="bg-white p-6 rounded-2xl shadow-lg w-full max-w-md">
            <h2 class="text-xl font-semibold mb-4 text-teal-800">Place Order</h2>
            <form id="orderForm" class="space-y-4">
                <div>
                    <label class="block text-gray-700">Crop</label>
                    <input id="orderCrop" type="text" class="w-full p-2 border rounded-md bg-gray-100" readonly>
                </div>
                <div>
                    <label class="block text-gray-700">Quantity</label>
                    <input id="orderQuantity" type="number" step="0.01" min="0" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" required>
                </div>
                <div>
                    <label class="block text-gray-700">Total Price (KES)</label>
                    <input id="orderTotal" type="text" class="w-full p-2 border rounded-md bg-gray-100" readonly>
                </div>
                <div>
                    <label class="block text-gray-700">Location (County)</label>
                    <input id="orderLocation" type="text" class="w-full p-2 border rounded-md focus:ring-teal-500 focus:border-teal-500" required>
                </div>
                <div class="flex justify-end gap-2">
                    <button type="button" onclick="closeOrderModal()" class="px-4 py-2 bg-gray-300 rounded-md hover:bg-gray-400 transition duration-300">Cancel</button>
                    <button type="submit" class="px-4 py-2 bg-teal-700 text-white rounded-md hover:bg-teal-800 transition duration-300">Order</button>
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
    // function openEditModal(id, ProductName, productCategory, quantity, unit, price, description, location, imageUrl) {
    //     document.getElementById('editModal').classList.remove('hidden');
    //     document.getElementById('editListingId').value = id;
    //     document.getElementById('editProductName').value = ProductName;
    //     document.getElementById('editProductCategory').value = productCategory;
    //     document.getElementById('editQuantity').value = quantity;
    //     document.getElementById('editUnit').value = unit;
    //     document.getElementById('editPrice').value = price;
    //     document.getElementById('editDescription').value = description;
    //     document.getElementById('editLocation').value = location;
    //     document.getElementById('editCurrentImage').src = imageUrl;
    //     document.getElementById('editForm').action = `/market/edit/${id}/`;
    // }
    function openEditModal(id, productName, productCategory, quantity, unit, price, description, location, imageUrl) {
        document.getElementById('editModal').classList.remove('hidden');
        document.getElementById('editListingId').value = id;
        document.getElementById('editProductName').value = productName;
        // Set the productCategory select field
        const categorySelect = document.getElementById('id_productCategory'); // ID generated by Django form
        if (categorySelect) {
            categorySelect.value = productCategory;
        }
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


# MODELS
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import os
from Social.models import UserProfile
from storages.backends.gcloud import GoogleCloudStorage

# from .utils import checkContent #content validation function

# Create your models here.
# Table for the orders made for a productListing 08
class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
    )
    
    listing = models.ForeignKey('productListing', on_delete=models.CASCADE, related_name='orders')
    requester = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='orders_made')
    quantity = models.FloatField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    def clean(self):
        """Validate order details."""
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'Quantity must be greater than 0.'})
        if self.quantity > self.listing.quantity:
            raise ValidationError({'quantity': f'Quantity requested ({self.quantity}) exceeds available ({self.listing.quantity}).'})
        if self.total_price != (self.quantity * float(self.listing.price)):
            raise ValidationError({'total_price': 'Total price does not match quantity × listing price.'})

    def save(self, *args, **kwargs):
        """Override save to calculate total_price and reduce listing quantity."""
        if not self.pk:  # Only on creation
            self.total_price = self.quantity * float(self.listing.price)
            self.listing.quantity -= self.quantity
            if self.listing.quantity <= 0:
                self.listing.is_available = False
            self.listing.save()
        # self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} for {self.listing.productName} by {self.requester.user.username}"

# 08

# Table that store the requests made by users 
class ProductRequest(models.Model):
    productCategoryChoices = [
        ('fruits', 'Fruits'),
        ('vegetables', 'Vegetables'),
        ('cereals', 'Cereals'),
        ('legumes', 'Legumes'),
        ('other', 'Other Category'),
    ]
    requester = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='product_requests')
    productCategory = models.CharField(max_length=20, choices=productCategoryChoices, default='other') #handles productCategory
    product_name = models.CharField(max_length=100, blank=False)
    quantity = models.FloatField()
    unit = models.CharField(max_length=20, default="kg")
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product_name} requested by {self.requester.user.username}"
    
    # FOR VALIDATING CONTENT ENTERED Commented out for now
    def clean(self):
        """Override the clean method to validate content relevance before saving"""
        if not checkContent(self.product_name):
            raise ValidationError({'product_name': 'Product name is not related to agriculture. Please edit.'})

        if not checkContent(self.description):
            raise ValidationError({'description': 'Description is not agriculturally relevant. Please edit.'})

    def save(self, *args, **kwargs):
        """Override the save method to ensure validation before saving"""
        # self.clean()  # Ensure clean() is called before saving
        super().save(*args, **kwargs)  # Call the parent class's save method

# For farmers product productproductListing
class productListing(models.Model):
    farmer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'farmer'})
    # product Category choices
    productCategoryChoices = [
        ('fruits', 'Fruits'),
        ('vegetables', 'Vegetables'),
        ('cereals', 'Cereals'),
        ('legumes', 'Legumes'),
        ('other', 'Other Category'),
    ]
    productCategory = models.CharField(max_length=20, choices=productCategoryChoices, default='other')    
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



class Message(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_messages')
    listing = models.ForeignKey(productListing, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.user.username} to {self.recipient.user.username}"

# VIEWS
# VIEWS.PY
# farmers/views.py
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

# ORDERS VIEW 08 removed underscores from views
@login_required
def createOrder(request):
    if request.method == "POST":
        data = json.loads(request.body)
        listing_id = data.get('listing_id')
        quantity = float(data.get('quantity', 0))
        location = data.get('location', '').strip()

        if not listing_id or quantity <= 0 or not location:
            return JsonResponse({'status': 'error', 'message': 'Listing ID, quantity, and location are required.'}, status=400)

        listing = get_object_or_404(productListing, id=listing_id, is_available=True)
        requester = request.user.userprofile

        order = Order.objects.create(
            listing=listing,
            requester=requester,
            quantity=quantity,
            location=location,
        )
        return JsonResponse({
            'status': 'success',
            'order': {
                'id': order.id,
                'product_name': order.listing.productName,
                'quantity': order.quantity,
                'total_price': float(order.total_price),
                'location': order.location,
                # 'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'created_at': localtime(order.created_at).strftime('%Y-%m-%d %H:%M:%S'),
                'status': order.status,
            }
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# Farmer's Order Section
@farmer_required
def getFarmerOrders(request):
    user_profile = request.user.userprofile
    orders = Order.objects.filter(listing__farmer=user_profile).order_by('-created_at')
    orders_data = [{
        'id': order.id,
        # 'date': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'date': localtime(order.created_at).strftime('%Y-%m-%d %H:%M:%S'),
        'requester': order.requester.user.username,
        'crop': order.listing.productName,
        'quantity': order.quantity,
        'total': float(order.total_price),
        'location': order.location,
        'status': order.status,
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

# Requester's Orders
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
    }
    print("Context competitor_crop_pricing:", context.get('competitor_crop_pricing'))
    return render(request, 'market.html', context)


# FORMS.PY
# Handles the listig forms and any other form created
# farmers/forms.py
from django import forms
from .models import productListing
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


