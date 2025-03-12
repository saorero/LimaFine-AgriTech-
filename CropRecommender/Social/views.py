from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login

from .forms import SignUpForm, PostForm #import theSignUp form class defined in forms.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm #Django predefined Authentication logic/class
from django.contrib.auth.decorators import login_required #user needs to be logged in
from .models import Post, UserProfile
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

@login_required
def unfollow_user(request, user_id):
    profile_to_unfollow = get_object_or_404(UserProfile, user__id=user_id)
    request.user.userprofile.following.remove(profile_to_unfollow)
    return redirect('feed')




# def feed(request):
#     filter_type = request.GET.get('filter', 'all')

#     # Filter posts based on 'following' filter
#     if filter_type == 'following':
#         following = request.user.userprofile.following.all()
#         posts = Post.objects.filter(user__userprofile__in=following).order_by('-created_at')
#     else:
#         posts = Post.objects.all().order_by('-created_at')

#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.user = request.user
#             post.save()
#             return redirect('feed')
#     else:
#         form = PostForm()

#     # Get filter role from the GET request, default is 'all'
#     filter_role = request.GET.get('role', 'all')

#     # Get all user profiles excluding the current user
#     all_profiles = UserProfile.objects.exclude(user=request.user)
#     following_ids = request.user.userprofile.following.values_list('id', flat=True)

#     # Suggest people who are not already followed and apply the role filter
#     if filter_role == 'all':
#         suggestions = all_profiles.exclude(id__in=following_ids)[:5]  # Show all suggestions
#     else:
#         suggestions = all_profiles.exclude(id__in=following_ids).filter(role=filter_role)[:5]  # Filter by role

#     # List of available roles for the filter (adjust as needed)
#     all_roles = ['trader', 'farmer', 'researcher']

#     return render(request, 'social.html', {
#         'posts': posts,
#         'form': form,
#         'filter_type': filter_type,
#         'suggestions': suggestions,
#         'action': 'feed',
#         'all_roles': all_roles,  # Add roles to the context for the filter dropdown
#         'filter_role': filter_role,  # Add the selected role filter to the context
#     })

def feed(request):
    filter_type = request.GET.get('filter', 'all')

    # Filter posts based on 'following' filter
    if filter_type == 'following':
        following = request.user.userprofile.following.all()
        posts = Post.objects.filter(user__userprofile__in=following).order_by('-created_at')
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

