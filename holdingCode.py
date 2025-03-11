<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if action == 'edit' %}Edit Post{% elif action == 'delete' %}Delete Post{% else %}Social Feed{% endif %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
    <div class="flex h-screen">
        <!-- Sidebar -->
        <div id="sidebar" class="w-64 bg-white shadow-lg p-4 transition-all duration-300">
            <button onclick="toggleSidebar()" class="mb-4">&#9776;</button>
            <ul>
                <li class="my-2 flex items-center py-4 "><span class="mr-2">🏠</span><span id="home-text">Home</span></li>
                <li class="my-3 flex items-center py-4"><span class="mr-2">⛅</span><span id="forecast-text">Forecast</span></li>
                <li class="my-3 flex items-center py-4"><span class="mr-2">📖</span><span id="learning-text">Learning Hub</span></li>
                <li class="my-3 flex items-center py-4 cursor-pointer" onclick="togglePostPopup()">
                    <span class="mr-2">✍️</span><span id="post-text">Post</span>
                </li>
                <li class="my-3 flex items-center py-4"><span class="mr-2">🚪</span><span id="logout-text"><a href="{% url 'logout' %}">Logout</a></span></li>
            </ul>
        </div>
        
        <div class="flex-1 flex flex-col">
            <!-- Header -->
            <header class="bg-white shadow-md p-4 flex justify-between items-center">
                <h2>Welcome, {{ user.username }}!</h2>
                <div class="flex items-center">
                    <button onclick="toggleProfilePopup()" class="mr-2">👤</button>
                </div>
            </header>

            <!-- Main Content -->
            <div class="flex flex-1 p-4">
                <!-- Feed -->
                <div class="flex-1 bg-white shadow-lg p-4 mr-4">
                    <div class="flex justify-end space-x-3 mb-4">
                        <a href="?filter=all" class="p-2 {% if filter_type == 'all' %}bg-blue-500 text-white{% else %}bg-gray-200 text-black{% endif %} rounded">All Posts</a>
                        <a href="?filter=following" class="p-2 {% if filter_type == 'following' %}bg-blue-500 text-white{% else %}bg-gray-200 text-black{% endif %} rounded">Following Posts</a>
                    </div>

                    {% if action == 'edit' %}
                        <h2>Edit Post</h2>
                        <form method="post">
                            {% csrf_token %}
                            {{ form.as_p }}
                            <button type="submit" class="bg-blue-500 text-white px-4 py-2 mt-2 rounded">Save</button>
                        </form>
                    {% elif action == 'delete' %}
                        <h2>Delete Post</h2>
                        <p>Are you sure you want to delete this post?</p>
                        <p>{{ post.content }}</p>
                        <form method="post">
                            {% csrf_token %}
                            <button type="submit" class="bg-red-500 text-white px-4 py-2 mt-2 rounded">Delete</button>
                        </form>
                    {% else %}
                        <!-- <button onclick="togglePostPopup()" class="bg-blue-500 text-white px-4 py-2 rounded">Create Post</button> -->
                        {% for post in posts %}
                            <div class="border p-4 mt-4">
                                <p><strong>{{ post.user.username }}</strong> ({{ post.created_at }}):</p>
                                <p>{{ post.content }}</p>
                                {% if post.user == user %}
                                    <a href="{% url 'edit_post' post.id %}" class="text-blue-500">Edit</a> |
                                    <a href="{% url 'delete_post' post.id %}" class="text-red-500">Delete</a>
                                {% endif %}
                            </div>
                        {% empty %}
                            <p>No posts yet.</p>
                        {% endfor %}
                    {% endif %}
                </div>
                
                <!-- People to Follow -->
                <div class="w-64 bg-white shadow-lg p-4">
                     <!-- Follow & Followers -->
                    <div class="flex items-center space-x-4 mb-4">
                        <p><strong>Followers:</strong> {{ user.userprofile.followers.count }}</p>
                        <p><strong>Following:</strong> {{ user.userprofile.following.count }}</p>
                    </div>

                    <h1><strong>Suggestions</strong></h1>
                    {% for profile in suggestions %}
                        <p>
                            {{ profile.user.username }} ({{ profile.role }})
                            <a href="{% url 'follow_user' profile.user.id %}" class="text-green-500">Follow</a>
                        </p>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    <!-- Post Popup -->
    <div id="post-popup" class="hidden fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center">
        <div class="bg-white p-6 rounded shadow-lg w-96">
            <h2 class="mb-2">Create Post</h2>
            <form method="post">
                {% csrf_token %}
                {{ form.media }}
                <textarea name="content" class="w-full h-24 border p-2 rounded focus:outline-none focus:ring focus:border-blue-500" placeholder="What's on your mind?" autofocus></textarea>
                <div class="flex justify-end mt-4">
                    <button type="submit" class="bg-green-500 text-white px-4 py-2 rounded">Post</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Profile Popup -->
    <div id="profile-popup" class="hidden fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center">
        <div class="bg-white p-6 rounded shadow-lg">
            <h2>Profile Details</h2>
            <p>Username: <span id="profile-username">{{ user.username }}</span></p>
            <button onclick="toggleProfilePopup()" class="bg-red-500 text-white px-4 py-2 mt-2 rounded">Close</button>
        </div>
    </div>

    <script>
        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('w-16');
            let textElements = ['home-text', 'forecast-text', 'learning-text', 'post-text', 'logout-text'];
            textElements.forEach(id => document.getElementById(id).classList.toggle('hidden'));
        }

        // Toggle the visibility of the post popup
        function togglePostPopup() {
            document.getElementById('post-popup').classList.toggle('hidden');
        }
        // Close the post popup when clicking anywhere outside the form
        document.addEventListener('click', function (event) {
            const postPopup = document.getElementById('post-popup');
            const postPopupContent = postPopup.querySelector('.bg-white');
            const postTextButton = document.getElementById('post-text');

            // Check if the click was outside the post popup and the "Post" button
            if (!postPopupContent.contains(event.target) && event.target !== postTextButton) {
                postPopup.classList.add('hidden');
            }
        });

        function toggleProfilePopup() {
            document.getElementById('profile-popup').classList.toggle('hidden');
        }
    </script>
</body>
</html>
