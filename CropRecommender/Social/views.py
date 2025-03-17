from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login

from .forms import SignUpForm, PostForm #import theSignUp form class defined in forms.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm #Django predefined Authentication logic/class
from django.contrib.auth.decorators import login_required #user needs to be logged in
from .models import Post, UserProfile, Like, Comment #models/table importation
from django.http import JsonResponse #for likes

# Create your views here.
# Sign up form called in this function
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')  # Redirect to login after signup
    else:
        form = SignUpForm()

    return render(request, 'auth.html', {
        'form': form,
        'title': 'Sign Up',
        'button_text': 'Sign Up',
        'is_login': False
    })

# LOGIN 
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('feed')  # Redirect after login

    else:
        form = AuthenticationForm()

    return render(request, 'auth.html', {
        'form': form,
        'title': 'Login',
        'button_text': 'Login',
        'is_login': True
    })

# Log out
def user_logout(request):
    logout(request)
    return redirect('login')


# SECOND SECTION
@login_required
def follow_user(request, user_id):
    profile_to_follow = get_object_or_404(UserProfile, user__id=user_id)
    request.user.userprofile.following.add(profile_to_follow)
    return redirect('feed')


# SECTION 2.1 17th endpoints to get followed and following users List and also to unfollow users
@login_required
def getFollowers(request, user_id):
    print(f"Debug: Fetching followers for user_id {user_id}") 
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    followers = [{"id": u.user.id, "username": u.user.username} for u in user_profile.followers.all()]
    return JsonResponse({"followers": followers})

@login_required
def getFollowing(request, user_id):
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    following = [{"id": u.user.id, "username": u.user.username} for u in user_profile.following.all()]
    return JsonResponse({"following": following})

@login_required
def unfollowUser(request, user_id):
    user_to_unfollow = get_object_or_404(UserProfile, user_id=user_id)
    user_profile = request.user.userprofile  # Get the current user's profile

    if user_to_unfollow in user_profile.following.all():
        user_profile.following.remove(user_to_unfollow)
        return JsonResponse({"success": True, "message": f"Unfollowed {user_to_unfollow.user.username}"})
        # return console.log("Unfollowed user successfully")
    return JsonResponse({"success": False, "message": "User not found in following list"}, status=400)


# Social media feed
@login_required
def feed(request):
    filter_type = request.GET.get('filter', 'all')

    # Filter posts based on 'following' filter
    if filter_type == 'following':
        following = request.user.userprofile.following.all()
        posts = Post.objects.filter(user__userprofile__in=following).order_by('-created_at')
    
    elif filter_type == 'mePosts':  # New filter for user's own posts
        posts = Post.objects.filter(user=request.user).order_by('-created_at')

    else:
        posts = Post.objects.all().order_by('-created_at')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # Handle file uploads
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()

    # Get filter role from the GET request, default is 'all'
    filter_role = request.GET.get('role', 'all')

    # Get all user profiles excluding the current user
    all_profiles = UserProfile.objects.exclude(user=request.user)
    following_ids = request.user.userprofile.following.values_list('id', flat=True)

    # Suggest people who are not already followed and apply the role filter
    if filter_role == 'all':
        suggestions = all_profiles.exclude(id__in=following_ids)[:5]  # Show all suggestions
    else:
        suggestions = all_profiles.exclude(id__in=following_ids).filter(role=filter_role)[:5]  # Filter by role

    # List of available roles for the filter (adjust as needed)
    all_roles = ['trader', 'farmer', 'researcher']

    return render(request, 'social.html', {
        'posts': posts,
        'form': form,
        'filter_type': filter_type,
        'suggestions': suggestions,
        'action': 'feed',
        'all_roles': all_roles,  # Add roles to the context for the filter dropdown
        'filter_role': filter_role,  # Add the selected role filter to the context
         })

# editing posts and deleting
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('feed')
    else:
        form = PostForm(instance=post)
    
    return render(request, 'social.html', {'form': form, 'post': post, 'action': 'edit'})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('feed')

    return render(request, 'social.html', {'post': post, 'action': 'delete'})


# THIRD SECTION Post Icon logic 13 (Like and comment)
@login_required
def likePost(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # confirm tge user has not liked the post
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete() #unlike post
        liked = False
    else:
        
        liked = True 
    return JsonResponse({'liked': liked, 'likesCount': post.totalLikes()})

# # To handle the comment section of posts 17
@login_required
def addComment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id) #gets the post being commented on
        content = request.POST.get("content")
        parentId = request.POST.get("parentId")  # To handle replies

        # prevents empty comment
        if not content:
            return JsonResponse({"error": "Comment cannot be empty"}, status=400)

        parentComment = None
        if parentId:
            try:
                parentComment = Comment.objects.get(id=parentId)
            except Comment.DoesNotExist:
                return JsonResponse({"error": "No parent comment"}, status=404)

        # DB of comment creation, new row
        comment = Comment.objects.create(
            user=request.user,
            post=post,
            content=content,
            parent=parentComment #if its a reply
        )

        return JsonResponse({
            "id": comment.id,  # for DOM Manipulation
            "user": request.user.username,
            "content": comment.content,
            "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
            "parentId": parentId if parentId else None, #if its a reply
        })
    return JsonResponse({"error": "Invalid request"}, status=400)

# View for the profile modal
def profileView(request):
    user_profile = UserProfile.objects.get(user=request.user)
    data = {
        'username': user_profile.user.username,
        # 'email': user_profile.user.email,
        'county': user_profile.county,
        'phoneNo': user_profile.phoneNo,
        'role': user_profile.get_role_display(),  # Get human-readable role
        # 'followers': user_profile.followers.count(),
    }
    return JsonResponse(data)  # Send JSON response
