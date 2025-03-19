{% extends "base2.html" %}  
{% load static %}
{% block content %}
        <div class="flex-1 flex flex-col">
            <!--Social Page top-->
            <div class="bg-gray-200 shadow-md p-4 flex justify-between items-center">
                <h2>Welcome, {{ user.username }}!</h2>
                <div class="flex items-center">
                    <button onclick="toggleProfilePopup()" class="mr-2">👤</button>
                </div>
            </div>

            <!-- Main Content -->
            <div class="flex flex-1 p-4">               
                <!-- Center display Div for posts -->
                <div class="flex-1 bg-white shadow-2xl p-4 mr-4 rounded-t-3xl">
                    <!-- Div for Filtering displayed posts -->                    
                    <div class="flex justify-start space-x-3 mb-4">     
                        <li class="flex items-center cursor-pointer rounded-2xl bg-gray-200 p-2 " onclick="togglePostPopup()">
                            <i class="fa-solid fa-marker "></i><span id="post-text">Post</span>
                        </li>                                 
                        <a href="?filter=following" class="p-2 {% if filter_type == 'following' %}bg-teal-700 text-white{% else %}bg-gray-200 text-black{% endif %} rounded-2xl">Following</a>
                        <a href="?filter=mePosts" class="p-2 {% if filter_type == 'mePosts' %}bg-teal-700 text-white{% else %}bg-gray-200 text-black{% endif %} rounded-2xl">My Posts</a>
                        <a href="?filter=all" class="p-2 {% if filter_type == 'all' %}bg-teal-700 text-white{% else %}bg-gray-200 text-black{% endif %} rounded-2xl">All</a>  
                    </div>
            
                   
                        <!-- Displays the posts at the center-->
                        {% for post in posts %}
                        <!-- Displays the content of each post -->
                        <div class="border-b-4 border-teal-700 p-4 mt-2 mb-2 flex flex-col rounded-3xl bg-gray-200 border-l-2">
    
                            <!-- Post Content and Edit/Delete button Div -->
                            <div class="flex justify-between items-start">
                                <!-- Content for post -->
                                <div class="shadow-2xl rounded-3xl p-4 bg-gray-100 flex-1">
                                    <p><strong>@{{ post.user.username }}</strong> <span class="text-xs">({{ post.created_at }})</span></p>
                                    <p>{{ post.content }}</p>
                        
                                    <!-- Uploaded files are displayed if there is an uploaded file in the post -->
                                    {% if post.file %}
                                        {% if post.file.url|lower|slice:'-3:' == 'pdf' %}
                                            <a href="{{ post.file.url }}" target="_blank" class="text-teal-700 underline">View File</a>
                                        {% else %}
                                            <img src="{{ post.file.url }}" alt="Uploaded Image" class="mt-2 max-w-full h-auto rounded">
                                        {% endif %}
                                    {% endif %}
                                </div>
                        
                                <!-- Edit & delete buttons (Only for the post owner) -->
                                {% if post.user == user %}
                                    <div class="flex space-x-3">
                                        <button onclick="openPopup('edit-popup-{{ post.id }}')" class="text-teal-700 ml-3 hover:text-teal-300" alt="edit" title="Edit">
                                            <i class="fa-solid fa-pen-to-square"></i>
                                        </button> 
                                        <button onclick="openPopup('delete-popup-{{ post.id }}')" class="text-teal-700 hover:text-red-600" alt="Delete" title="Delete">
                                            <i class="fa-solid fa-trash-can"></i>
                                        </button>
                                    </div>
                                {% endif %}
                            </div>
                        
                            <!-- Comment, like and flag post row (another row)-->
                            <div class="flex justify-end items-center mt-3 space-x-6 text-gray-600">
                                <!-- Like button -->
                                <button onclick="likePost({{ post.id }})" class="hover:text-red-500 flex items-center">
                                    <i id="like-icon-{{ post.id }}" class="fa-solid fa-heart"></i><span id="like-count-{{ post.id }}" class="ml-1">{{ post.totalLikes }}</span>
                                </button>
                               
                                <!-- Comment button for opening post comment section-->
                                <button onclick="openCommentPopup({{ post.id }})" class="hover:text-teal-500 flex items-center">
                                    <i class="fa-solid fa-comment"></i>
                                    <span id="comment-count-{{ post.id }}" class="ml-1">{{ post.comments.count }}</span>Comments
                                </button>                                  
                                
                                <!-- flag button -->
                                <button class="hover:text-yellow-500 flex items-center"><i class="fa-solid fa-flag"></i><span class="ml-1">Report</span></button>                                    
                                                                   
                            </div>

                            <!-- Comments Section (Hidden by default) -->
                            <div id="comment-popup-{{ post.id }}" class="hidden mt-4">
                                
                                <div class="flex justify-start space-x-3">
                                    <button onclick="closeCommentPopup({{ post.id }})" class="hover:text-teal-700 flex items-center text-black" title="Close Comments"><i class="fa-regular fa-circle-xmark"></i></button> <!-- Closes the comment section -->
                                    <button onclick="openCommentModal({{ post.id }}) " class="hover:bg-teal-700 hover:text-white flex items-center bg-gray-300 rounded-3xl p-2">MeComment</button> <!-- Allows one to comment -->  
                                </div>
                                
                                                                                                   
                                <!-- Display Comments -->
                                {% for comment in post.comments.all %}
                                    {% if not comment.parent %} <!-- Only show top-level comments -->
                                        <div id="comment-{{ comment.id }}" class="p-2 bg-gray-100 rounded-lg mt-2">
                                            <p><strong>@{{ comment.user.username }}</strong> ({{ comment.created_at }}):</p>
                                            <p>{{ comment.content }}</p>
                                            <button onclick="openReplyModal({{ post.id }}, {{ comment.id }})" class="text-teal-500">Reply</button>

                                            <!-- Replies to this comment -->
                                            <div id="replies-{{ comment.id }}" class="ml-6">
                                                {% for reply in comment.replies.all %}
                                                    <div class="p-2 bg-gray-300 rounded-lg mt-2">
                                                        <p><strong>@{{ reply.user.username }}</strong> ({{ reply.created_at }}):</p>
                                                        <p>{{ reply.content }}</p>
                                                    </div>
                                                {% endfor %}
                                            </div>
                                        </div>
                                    {% endif %}
                                {% endfor %}
                            </div>                        
                        </div>                           
                                                  
                        <!-- Edit Post Popup modal-->
                        <div id="edit-popup-{{ post.id }}" class="hidden fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center">
                                <div class="bg-white p-6 rounded-xl shadow-lg w-96 backdrop-blur-xl">
                                    <h1 class="italic">Post editing...</h1>
                                    <form method="post" action="{% url 'edit_post' post.id %}">
                                        {% csrf_token %}
                                        <textarea name="content" class="w-full h-24 border rounded focus:outline-none focus:ring focus:border-teal-500">{{ post.content }}</textarea>
                                        <div class="flex justify-end mt-4">                                            
                                            <button type="button" onclick="closePopup('edit-popup-{{ post.id }}')" class="text-teal-700 mr-2" title="Cancel"><i class="fa-regular fa-circle-xmark"></i></button>
                                            <button type="submit" class="bg-teal-200 text-black px-2 py-2 rounded-3xl hover:bg-teal-700 hover:text-white">Save</button>
                                        </div>
                                    </form>
                                </div>
                        </div>
            
                        <!-- Delete Post Popup modal -->
                        <div id="delete-popup-{{ post.id }}" class="hidden fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center">
                                <div class="bg-white p-6 rounded-xl shadow-lg w-96 backdrop-blur-xl">
                                    <h1 class="italic">Are you sure you want to delete?</h1>
                                    <p class=" text-teal-600">{{ post.content }}</p>
                                    <form method="post" action="{% url 'delete_post' post.id %}">
                                        {% csrf_token %}
                                        <div class="flex justify-end mt-4">
                                            <button type="button" onclick="closePopup('delete-popup-{{ post.id }}')" class="text-teal-700 mr-2" title="Cancel"><i class="fa-regular fa-circle-xmark"></i></button>
                                            <button type="submit" class="bg-teal-200 text-black px-2 py-2 rounded-3xl hover:bg-red-700">Delete</button>
                                        </div>
                                    </form>
                                </div>
                        </div>
            
                        {% empty %}
                            <p>No posts yet.</p>
                        {% endfor %}                  
                </div> 
                
                <!-- People to Follow logic-->
                <div class="w-64 bg-white shadow-lg p-4 rounded-3xl">                    
                    <!-- Follow & Followers -->                    
                        <div class="flex items-center space-x-4 mb-4 text-teal-700  p-1 ">                         
                            <button onclick="toggleFollowers({{ user.id }})" class="hover:bg-teal-700 hover:text-white rounded-2xl p-1">Followers:{{ user.userprofile.followers.count }} </button>                   
                            <button onclick="toggleFollowing({{ user.id }})" class="hover:bg-teal-700 hover:text-white rounded-2xl p-1">Following:{{ user.userprofile.following.count }}</button>
                        </div>

                        <!-- Followers List -->
                        <div id="followers-list" class="hidden mt-2 p-4 bg-gray-100 rounded">
                            <h3 class="font-semibold">Followers</h3>
                            <ul id="followers-container"></ul>
                        </div>

                        <!-- Following List -->
                        <div id="following-list" class="hidden mt-2 p-4 bg-gray-100 rounded">
                            <h3 class="font-semibold">Following</h3>
                            <ul id="following-container"></ul>
                        </div>
                        <!-- NOW -->
                    <h1><strong>People to follow</strong></h1>

                    <!-- Filter by role logic-->
                    <form method="GET" class="m-4">
                        <label for="role" class="mr-2 shadow-xl ">Filter by Role:</label>
                        <select name="role" id="role" class="px-4 py-2 rounded focus:outline-none focus:ring-0">
                            <option value="all" {% if filter_role == 'all' %}selected{% endif %}>All</option>
                            {% for role in all_roles %}
                                <option value="{{ role }}" {% if filter_role == role %}selected{% endif %}>{{ role }}</option>
                            {% endfor %}
                        </select>
                        <button type="submit" class=" text-teal-700 px-2 rounded ml-8"><i class="fa-solid fa-filter"></i></button>
                    </form>
                    <div class="bg-teal-200 shadow-xl rounded-xl p-3 ">
                        <!-- Display filtered suggestions -->
                        {% for profile in suggestions %}
                            <p>
                                {{ profile.user.username }} - {{ profile.role }}
                                <a href="{% url 'follow_user' profile.user.id %}" class="text-teal-700 ml-8">
                                    <i class="fa-solid fa-circle-check"></i>
                                </a>
                            </p>
                        {% empty %}
                            <p>No suggestions available for the selected role.</p>
                        {% endfor %}
                    </div>
                    


                </div>
            </div>
        </div>
{% endblock content %}
   
{% block modalsContent %}    
    <!-- Post Popup Modal -->
    <div id="post-popup" class="hidden fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center">
        <div class="bg-white p-6 rounded-xl shadow-lg w-96 backdrop-blur-sm">
            <h2 class="text-teal-700"> <strong>Create Post</strong></h2>
            <form method="post" enctype="multipart/form-data">  <!-- Enable file uploads enctype -->
                {% csrf_token %} 
                {{ form.media }}
                <textarea name="content" class="w-full h-24  p-2 rounded focus:outline-none focus:ring focus:border-teal-500" placeholder="What's on your mind?" autofocus></textarea>
                
                <!-- File Upload Input -->
                <div class="relative w-full mt-2">
                    <input type="file" name="file" id="fileUpload" class="hidden" onchange="updateFileName(this)">
                    <label for="fileUpload" class="cursor-pointer flex items-center justify-center p-2 rounded-lg bg-teal-700 text-white-700 hover:bg-teal-300">
                        <i class="fa-solid fa-cloud-arrow-up text-2xl"></i>
                        <span id="fileName" class="ml-2 text-sm text-white ">Upload File (.png, .pdf)</span>
                    </label>
                </div> 
          
                <div class="flex justify-end mt-4">
                    <button type="submit" class="bg-teal-700 text-white px-3 py-2 rounded">Post</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Profile Popup Modal-->
    <div id="profile-popup" class="hidden fixed inset-0  bg-gray-100 bg-opacity-50 flex items-center justify-center ">
            <div class="bg-white p-4 shadow-xl w-80 backdrop-blur-xl rounded-3xl">
    
                <h2 class="text-teal-700 text-center font-bold">Profile Details</h2>
                <p><strong>Username:</strong> <span id="profile-username"></span></p>               
                <p><strong>County:</strong> <span id="profile-county"></span></p>
                <p><strong>Phone Number:</strong> <span id="profile-phone"></span></p>
                <p><strong>Role:</strong> <span id="profile-role"></span></p>
                       
                <div class="flex justify-end space-x-3 ">
                    <div class="flex items-center space-x-2">
                        <i class="fa-solid fa-right-from-bracket"></i>
                        <a href="{% url 'logout' %}" id="logout-text" class="text-teal-700">Logout</a>
                    </div>
                    <button onclick="toggleProfilePopup()" class="hover:bg-teal-700 hover:text-white text-black  p-2 rounded-2xl"><i class="fa-regular fa-circle-xmark"></i></button>
                </div>
            </div>
    </div>

   
    <!-- Comment Modal Popup -->
    <div id="comment-modal" class="hidden fixed inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50">
        <div class="bg-white p-4 rounded-lg shadow-lg w-96">
            <h2 class="text-lg font-bold mb-2">Write a Comment</h2>
            <textarea id="comment-modal-input" class="w-full p-2 border rounded" placeholder="Write a comment..."></textarea>
            <div class="flex justify-end mt-3 space-x-3">
                <button onclick="submitComment()" class="hover:bg-teal-700 text-teal-700  rounded-3xl  hover:text-white" title="submit"><i class="fa-solid fa-circle-check fa-xl"></i></button>
                <button onclick="closeCommentModal()" class=" hover:bg-teal-700 text-teal-700 rounded-3xl  hover:text-white"><i class="fa-regular fa-circle-xmark fa-xl"></i></button>
            </div>
        </div>
    </div>

    <!-- Reply Modal PopUp-->
        <div id="reply-modal" class="hidden fixed inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50">
            <div class="bg-white p-4 rounded-lg shadow-lg w-96">
                <h2 class="text-lg font-bold mb-2">Write a Reply</h2>
                <textarea id="reply-modal-input" class="w-full p-2 border rounded" placeholder="Write a reply..."></textarea>
                <div class="flex justify-end mt-3 space-x-1">
                    <button onclick="submitReply()" class="hover:bg-teal-700 text-teal-700  rounded-3xl  hover:text-white p-2" title="submit"><i class="fa-solid fa-circle-check fa-xl"></i></button>
                    <button onclick="closeReplyModal()" class="ml-2 hover:bg-teal-700 text-teal-700 hover:text-white px-4 py-2 rounded-3xl"><i class="fa-regular fa-circle-xmark fa-xl"></i></button>
                </div>
            </div>
        </div>
{% endblock modalsContent %}  



   
{% block script %}

<script>
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
       
        fetch('/social/profile/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('profile-username').textContent = data.username;
            //document.getElementById('profile-email').textContent = data.email;
            document.getElementById('profile-county').textContent = data.county;
            document.getElementById('profile-phone').textContent = data.phoneNo;
            document.getElementById('profile-role').textContent = data.role;
            // document.getElementById('profile-followers').textContent = data.followers;

           
        });
    }

    // Handles the display of the file name
    function updateFileName(input) {
    const fileName = input.files.length > 0 ? input.files[0].name : "Upload File";
    document.getElementById("fileName").textContent = fileName;
    }


    // DELETE AND EDIT FUNCTIONALITIES
    function openPopup(popupId) {
        document.getElementById(popupId).classList.remove('hidden');
    }

    function closePopup(popupId) {
        document.getElementById(popupId).classList.add('hidden');
    }

        // Liking functionalities
    function likePost(postId) {
        fetch(`/social/like/${postId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.liked) {
                document.getElementById(`like-icon-${postId}`).classList.add("text-red-500");
            } else {
                document.getElementById(`like-icon-${postId}`).classList.remove("text-red-500");
            }
            document.getElementById(`like-count-${postId}`).innerText = data.likesCount;
        })
        .catch(error => console.error('Error:', error));
    }

    // COMMENT HANDLING 13

            let currentPostId = null;
            let currentCommentId = null;

            // Open Comment Modal
            function openCommentModal(postId) {
                currentPostId = postId;
                document.getElementById("comment-modal").classList.remove("hidden");
            }

            // Close Comment Modal
            function closeCommentModal() {
                document.getElementById("comment-modal").classList.add("hidden");
                document.getElementById("comment-modal-input").value = "";
            }

            // Submit Comment
            function submitComment() {
                let content = document.getElementById("comment-modal-input").value;
                let csrfToken = "{{ csrf_token }}";

                fetch(`/social/comment/${currentPostId}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: `content=${encodeURIComponent(content)}`
                })
                .then(response => response.json())
                .then(data => {
                    if (!data.error) {
                        // Append new comment to comment section dynamically
                        let commentSection = document.getElementById(`comment-popup-${currentPostId}`);
                        let newComment = `
                            <div class="ml-4 p-2 bg-gray-200 rounded-lg mt-2">
                                <p><strong>@${data.user}</strong> (${data.created_at}):</p>
                                <p>${data.content}</p>
                                <button onclick="openReplyModal(${data.parentId || 'null'})" class="text-teal-500">Reply</button>
                            </div>`;
                        commentSection.insertAdjacentHTML("beforeend", newComment);

                        // Update comment count
                        let commentCount = document.getElementById(`comment-count-${currentPostId}`);
                        commentCount.innerText = parseInt(commentCount.innerText) + 1;

                        closeCommentModal();
                    }
                })
                .catch(error => console.error("Error:", error));
            }


            // Open Reply Modal
            function openReplyModal(postId, commentId) {
                currentPostId = postId;  // Store post ID for reply
                currentCommentId = commentId;  // Store comment ID
                document.getElementById("reply-modal").classList.remove("hidden");
            }


            // Close Reply Modal
            function closeReplyModal() {
                document.getElementById("reply-modal").classList.add("hidden");
                document.getElementById("reply-modal-input").value = "";
            }

            // Submit Reply
            function submitReply() {
                let content = document.getElementById("reply-modal-input").value;
                let csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;  // Get CSRF token dynamically

                if (!content) {
                    alert("Reply content cannot be empty!");
                    return;
                }

                if (!currentPostId || !currentCommentId) {
                    console.error("Error: Missing post or comment ID.");
                    return;
                }

                fetch(`/social/comment/${currentPostId}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: `content=${encodeURIComponent(content)}&parentId=${currentCommentId}`
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then(data => {
                    if (!data.error) {
                        // Append new reply dynamically under the parent comment
                        let parentCommentReplies = document.getElementById(`replies-${currentCommentId}`);
                        if (!parentCommentReplies) {
                            // If the replies container doesn't exist, create it
                            const parentComment = document.getElementById(`comment-${currentCommentId}`);
                            parentComment.insertAdjacentHTML("beforeend", `<div id="replies-${currentCommentId}" class="ml-6"></div>`);
                            parentCommentReplies = document.getElementById(`replies-${currentCommentId}`);
                        }

                        let newReply = `
                            <div class="p-2 bg-gray-300 rounded-lg mt-2">
                                <p><strong>@${data.user}</strong> (${data.created_at}):</p>
                                <p>${data.content}</p>
                            </div>
                        `;
                        parentCommentReplies.insertAdjacentHTML("beforeend", newReply);

                        closeReplyModal();
                    } else {
                        console.error("Error from server:", data.error);
                        alert("Failed to submit reply: " + data.error);
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                    alert("An error occurred while submitting the reply.");
                });
            }


        function openCommentPopup(postId) {
        document.getElementById(`comment-popup-${postId}`).classList.remove("hidden");
        }

        function closeCommentPopup(postId) {
            document.getElementById(`comment-popup-${postId}`).classList.add("hidden");
        }
// SECTION FOR FOLLOWING LIST AND FOLLOWERS LIST AND UNFOLLOWING

// Toggle followers list
function toggleFollowers(userId) {
    let followersList = document.getElementById("followers-list");
    let container = document.getElementById("followers-container");

    if (!followersList.classList.contains("hidden")) {
        followersList.classList.add("hidden");
        return;
    }

    fetch(`/social/followers/${userId}/`)
        .then(response => response.json())
        .then(data => {
            container.innerHTML = data.followers.length 
                ? data.followers.map(user => `<li>@${user.username}</li>`).join("")
                : "<p>No followers yet.</p>";
            followersList.classList.remove("hidden");
        })
        .catch(error => console.error("Error fetching followers:", error));
}

// Toggle following list with unfollow option
function toggleFollowing(userId) {
    let followingList = document.getElementById("following-list");
    let container = document.getElementById("following-container");

    if (!followingList.classList.contains("hidden")) {
        followingList.classList.add("hidden");
        return;
    }

    fetch(`/social/following/${userId}/`)
        .then(response => response.json())
        .then(data => {
            container.innerHTML = data.following.length 
                ? data.following.map(user => `
                    <li>
                        @${user.username} 
                        <button onclick="unfollowUser(${user.id})" class="text-red-500">Unfollow</button>
                    </li>
                `).join("")
                : "<p>Not following anyone.</p>";
            followingList.classList.remove("hidden");
        })
        .catch(error => console.error("Error fetching following list:", error));
}

// Unfollow user
function unfollowUser(userId) {

    fetch(`/social/unfollow/${userId}/`, { method: "POST",
        headers: {
                "X-CSRFToken": getCookie("csrftoken"), // Ensure you send CSRF token getCookie functionality
                "Content-Type": "application/json"
            },
            credentials: "include" // Ensures cookies are sent with request

     })

    
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                toggleFollowing(userId);
                // alert(data.message);
            }
        })
        .catch(error => console.error("Error unfollowing user:", error));
}

//  Function to extract CSRF token from cookies and add it to Unfollow request headers SPECIAL FUNCTION
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}  

</script>

{% endblock script %}