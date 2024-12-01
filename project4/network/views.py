from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import json, re


from .models import User, Post


def index(request):
    posts = Post.objects.all().order_by('-timestamp')

    # Process each post to replace mentions with links
    for post in posts:
        post.content = replace_mentions_with_links(post.content)

    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'network/index.html', {
        'page_obj': page_obj
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    

@login_required
def new_post(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Post.objects.create(user=request.user, content=content)
        return redirect("index")
    else:
        return HttpResponse("Invalid request method.", status=405)
    

def all_posts(request):
    posts = Post.objects.all().order_by('-timestamp')

    # Process each post to replace mentions with links
    for post in posts:
        post.content = replace_mentions_with_links(post.content)

    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'network/all_posts.html', {
        'page_obj': page_obj
    })


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=profile_user).order_by("-timestamp")
    is_following = profile_user in request.user.following.all() if request.user.is_authenticated else False

    for post in posts:
        post.content = replace_mentions_with_links(post.content)

    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "posts": page_obj,
        "is_following": is_following
    })


@login_required
def toggle_follow(request, username):
    profile_user = get_object_or_404(User, username=username)
    if profile_user == request.user:
        return JsonResponse({"error": "You cannot follow yourself."}, status=400)

    if profile_user in request.user.following.all():
        request.user.following.remove(profile_user)
        is_following = False
    else:
        request.user.following.add(profile_user)
        is_following = True

    return JsonResponse({"is_following": is_following, "follower_count": profile_user.follower_count()})


@login_required
def following_posts(request):
    # Get the users the current user is following
    following_users = request.user.following.all()

    # Retrieve posts made by the users being followed
    posts = Post.objects.filter(user__in=following_users).order_by("-timestamp")
    for post in posts:
        post.content = replace_mentions_with_links(post.content)
    
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/following.html", {
        "posts": page_obj
    })


@csrf_exempt
def edit_post(request, post_id):
    if request.method == "PUT":
        try:
            post = Post.objects.get(id=post_id, user=request.user)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found or you are not authorized to edit this post."}, status=404)

        data = json.loads(request.body)
        content = data.get("content", "").strip()

        if not content:
            return JsonResponse({"error": "Post content cannot be empty."}, status=400)

        post.content = content
        post.save()
        return JsonResponse({"message": "Post updated successfully."})

    return JsonResponse({"error": "Invalid request method."}, status=400)


def like_post(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=400)

    post = Post.objects.get(id=post_id)
    user = request.user

    # Toggle like status
    if user in post.likes.all():
        post.likes.remove(user)  # Unlike if already liked
    else:
        post.likes.add(user)  # Like if not already liked

    return JsonResponse({
        "like_count": post.like_count(),
        "is_liked": user in post.likes.all()
    })


# Function to replace mentions with links
def replace_mentions_with_links(content):
    pattern = r'@(\w+)'  # Matches @username
    def repl(match):
        username = match.group(1)
        try:
            user = User.objects.get(username=username)
            return f'<a href="/profile/{user.username}">@{username}</a>'
        except User.DoesNotExist:
            return match.group(0)  # If the user doesn't exist, keep the mention as plain text
    return re.sub(pattern, repl, content)