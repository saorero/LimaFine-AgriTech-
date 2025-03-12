{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if action == 'edit' %}Edit Post{% elif action == 'delete' %}Delete Post{% else %}Social Feed{% endif %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet" />
</head>
<body class="bg-gray-300">
    <div class="flex flex-col md:flex-row h-screen">
        
        <!-- Sidebar -->
        <div id="sidebar" class="w-full md:w-56 bg-teal-700 shadow-lg p-4 fixed md:relative z-50">
            <button onclick="toggleSidebar()" class="text-white mb-4 md:hidden">&#9776;</button>
            <ul class="text-white">
                <li class="my-2 flex items-center py-4"><i class="fa-solid fa-house fa-xl mr-2"></i><a href="{% url 'Homepage' %}" id="home-text">Home</a></li>
                <li class="my-2 flex items-center py-4"><i class="fa-solid fa-cloud-sun-rain fa-xl mr-2"></i><span id="forecast-text">Forecast</span></li>
                <li class="my-2 flex items-center py-4"><i class="fa-solid fa-book fa-xl mr-2"></i><span id="learning-text">Learning Hub</span></li>
                <li class="my-2 flex items-center py-4"><i class="fa-solid fa-comments fa-xl mr-2"></i><span id="botText">AgriBot</span></li>
                <li class="my-2 flex items-center py-4"><i class="fa-solid fa-cart-shopping fa-xl mr-2"></i><span id="marketText">Market</span></li>
                <li class="my-2 flex items-center py-4 cursor-pointer" onclick="togglePostPopup()">
                    <i class="fa-solid fa-marker fa-xl mr-2"></i><span id="post-text">Post</span>
                </li>
                <li class="my-2 flex items-center py-4"><i class="fa-solid fa-right-from-bracket fa-xl mr-2"></i><a href="{% url 'logout' %}" id="logout-text">Logout</a></li>
            </ul>
        </div>
        
        <div class="flex-1 flex flex-col">
            <!-- Header -->
            <header class="bg-white shadow-md p-4 flex justify-between items-center">
                <h2>Welcome, {{ user.username }}!</h2>
                <button onclick="toggleProfilePopup()">👤</button>
            </header>

            <!-- Main Content -->
            <div class="flex flex-col md:flex-row flex-1 p-4 space-y-4 md:space-y-0 md:space-x-4">
                
                <!-- Feed -->
                <div class="flex-1 bg-white shadow-2xl p-4 rounded-xl">
                    <div class="flex justify-end space-x-3 mb-4">
                        <a href="?filter=all" class="p-2 {% if filter_type == 'all' %}bg-teal-700 text-white{% else %}bg-gray-200 text-black{% endif %} rounded-2xl">All</a>
                        <a href="?filter=following" class="p-2 {% if filter_type == 'following' %}bg-teal-700 text-white{% else %}bg-gray-200 text-black{% endif %} rounded-2xl">Following</a>
                    </div>
                    
                    {% for post in posts %}
                        <div class="border-b-4 border-teal-700 p-4 mt-2 mb-2 flex flex-col md:flex-row items-start justify-between rounded-3xl bg-gray-200 border-l-2">
                            <div class="shadow-2xl rounded-3xl p-4 bg-gray-100 w-full">
                                <p><strong>@{{ post.user.username }}</strong> <span class="text-xs">({{ post.created_at }})</span></p>
                                <p>{{ post.content }}</p>
                                {% if post.file %}
                                    {% if post.file.url|lower|slice:'-3:' == 'pdf' %}
                                        <a href="{{ post.file.url }}" target="_blank" class="text-teal-700 underline">View File</a>
                                    {% else %}
                                        <img src="{{ post.file.url }}" alt="Uploaded Image" class="mt-2 max-w-full h-auto rounded">
                                    {% endif %}
                                {% endif %}
                            </div>
                            
                            {% if post.user == user %}
                                <div class="flex space-x-3 mt-2 md:mt-0">
                                    <button onclick="openPopup('edit-popup-{{ post.id }}')" class="text-teal-700"><i class="fa-solid fa-pen-to-square"></i></button> 
                                    <button onclick="openPopup('delete-popup-{{ post.id }}')" class="text-teal-700 hover:text-red-600"><i class="fa-solid fa-trash-can"></i></button>
                                </div>
                            {% endif %}
                        </div>
                    {% empty %}
                        <p>No posts yet.</p>
                    {% endfor %}
                </div> 

                <!-- People to Follow -->
                <div class="w-full md:w-64 bg-white shadow-lg p-4 rounded-3xl">
                    <div class="flex justify-between mb-4">
                        <p><strong>Followers:</strong> {{ user.userprofile.followers.count }}</p>
                        <p><strong>Following:</strong> {{ user.userprofile.following.count }}</p>
                    </div>
                    <h1><strong>People to follow</strong></h1>
                    <form method="GET" class="my-4">
                        <label for="role">Filter by Role:</label>
                        <select name="role" id="role" class="px-2 py-1 rounded">
                            <option value="all">All</option>
                            {% for role in all_roles %}
                                <option value="{{ role }}">{{ role }}</option>
                            {% endfor %}
                        </select>
                        <button type="submit" class="text-teal-700 px-2 ml-2"><i class="fa-solid fa-filter"></i></button>
                    </form>
                    <div class="bg-teal-200 shadow-xl rounded-xl p-3">
                        {% for profile in suggestions %}
                            <p>{{ profile.user.username }} - {{ profile.role }}
                                <a href="{% url 'follow_user' profile.user.id %}" class="text-teal-700 ml-8">
                                    <i class="fa-solid fa-circle-check"></i>
                                </a>
                            </p>
                        {% empty %}
                            <p>No suggestions available.</p>
                        {% endfor %}
                    </div>
                </div>

            </div>
        </div>
    </div>

    <script>
        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('hidden');
        }
        function toggleProfilePopup() {
            document.getElementById('profile-popup').classList.toggle('hidden');
        }
        function togglePostPopup() {
            document.getElementById('post-popup').classList.toggle('hidden');
        }
        function openPopup(id) {
            document.getElementById(id).classList.remove('hidden');
        }
        function closePopup(id) {
            document.getElementById(id).classList.add('hidden');
        }
    </script>

</body>
</html>
# THE CODE THAT IS RESPONSIVE FOLLOW SOME FEATURES FROM HERE