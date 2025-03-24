<!-- templates/market.html -->
{% extends "base2.html" %}
{% load widget_tweaks %}
{% load compress %}
{% load static %}

{% block content %}
<div class="max-w-6xl mx-auto">
    <!-- Header -->
    <h1 class="text-3xl font-bold mb-6">{{ message }}</h1>

    <!-- Tabs for switching between Create Listing and Dashboard -->
    <div class="flex border-b mb-6">
        <button id="dashboardTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-blue-600 focus:outline-none tab-button active-tab">Dashboard</button>
        <button id="createListingTab" class="px-4 py-2 font-semibold text-gray-700 border-b-2 border-transparent hover:border-blue-600 focus:outline-none tab-button">Create Listing</button>
    </div>

    <!-- Dashboard Section -->
    <div id="dashboardSection" class="tab-content grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {% if listings %}
            {% for listing in listings %}
            <div class="bg-white shadow-md rounded-lg overflow-hidden flex flex-col h-[19rem] hover:shadow-lg transition-shadow duration-200 p-2 relative">
                <!-- Image with fixed height -->
                <div class="h-40 w-full overflow-hidden">
                    <img src="{{ listing.get_image_url }}" alt="{{ listing.productName }}" class="w-full h-full object-cover">
                </div>
                
                <!-- Card content with flex-grow to fill remaining space -->
                <div class="p-3 flex flex-col flex-grow">
                    <h2 class="text-lg font-semibold line-clamp-1">{{ listing.productName }}</h2>
                    <p class="text-gray-500 text-sm">{{ listing.quantity }} <span class="text-sm">{{ listing.unit }}</span></p>
                    
                    <div class="mt-2">
                        <p class="text-gray-700 font-bold">KES: {{ listing.price }}</p>
                        <p class="text-gray-500 text-sm">{{ listing.location }}</p>
                    </div>
                    
                    <!-- Description with line clamping -->
                    <p class="text-sm text-gray-600 mt-2 line-clamp-2 flex-grow">{{ listing.description }}</p>
                    
                    <!-- Availability toggle and action icons -->
                    <div class="mt-2 flex items-center justify-between">
                        <!-- Toggle Switch for Availability -->
                        <form method="POST" action="{% url 'toggle_availability' listing.id %}" class="flex items-center">
                            {% csrf_token %}
                            <label class="relative inline-flex items-center cursor-pointer">
                                <input type="checkbox" name="is_available" {% if listing.is_available %}checked{% endif %} class="sr-only peer" onchange="this.form.submit()">
                                <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:bg-green-600 transition-colors duration-200"></div>
                                <div class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform duration-200 peer-checked:translate-x-5"></div>
                            </label>
                            <span class="ml-2 text-sm font-semibold {% if listing.is_available %}text-green-600{% else %}text-red-600{% endif %}">
                                {% if listing.is_available %}Available{% else %}Sold Out{% endif %}
                            </span>
                        </form>

                        <!-- Edit and Delete Icons -->
                        <div class="flex space-x-2">
                            <button onclick="openEditModal({{ listing.id }}, '{{ listing.productName }}', '{{ listing.productCategory }}', '{{ listing.quantity }}', '{{ listing.unit }}', '{{ listing.price }}', '{{ listing.description }}', '{{ listing.location }}', '{{ listing.get_image_url }}')" class="text-yellow-500 hover:text-yellow-600" title="Edit Listing">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="openDeleteModal({{ listing.id }}, '{{ listing.productName }}')" class="text-red-500 hover:text-red-600" title="Delete Listing">
                                <i class="fas fa-trash-alt"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <p class="text-gray-600 col-span-full">You haven't created any listings yet. Use the "Create Listing" tab to add a new listing.</p>
        {% endif %}
    </div>

    <!-- Create Listing Section -->
    <div id="createListingSection" class="tab-content hidden">
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
    </div>

    <!-- Edit Listing Modal -->
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
</div>
{% endblock content %}

{% block script %}
<script>
    const tabs = document.querySelectorAll('.tab-button');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active-tab', 'border-blue-600'));
            contents.forEach(c => c.classList.add('hidden'));

            tab.classList.add('active-tab', 'border-blue-600');
            const sectionId = tab.id.replace('Tab', 'Section');
            document.getElementById(sectionId).classList.remove('hidden');
        });
    });

    document.getElementById("listingForm").addEventListener("submit", function(e) {
        const quantity = document.querySelector("[name='quantity']").value;
        const price = document.querySelector("[name='price']").value;
        if (quantity <= 0 || price <= 0) {
            e.preventDefault();
            alert("Quantity and Price must be greater than zero!");
        }
    });

    // Edit Modal Functions
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

    // Delete Modal Functions
    function openDeleteModal(id, ProductName) {
        document.getElementById('deleteModal').classList.remove('hidden');
        document.getElementById('deleteListingId').value = id;
        document.getElementById('deleteProductName').textContent = ProductName;
        document.getElementById('deleteForm').action = `/market/delete/${id}/`;
    }

    function closeDeleteModal() {
        document.getElementById('deleteModal').classList.add('hidden');
    }
</script>
{% endblock script %}