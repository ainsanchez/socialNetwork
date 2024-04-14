import time

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import strip_tags

from .forms import NewPost
from .models import User, userPost


def index(request):
    #return render(request, "network/index.html")
    # Create a New userPost
    if request.method == "POST":
        user = User.objects.get(pk=request.user.id)
        form = NewPost(request.POST)
        content = strip_tags(NewPost(request.POST)["content"])
        entry = userPost(user=user, content=content)
        if form.is_valid():
            entry.save()
            # form.save()
            return HttpResponse('<p>Info Saved!</p>')
        else:
            return HttpResponse('<p>Info is not Valid!</p>')
    else:
        form = NewPost
        posts = userPost.objects.all()
        context = {
            'form': form,
            'posts': posts
        }
        return render(request, "network/index.html", context)



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
    

# Make a new UserPost, mimicking the post method commented in index
def posts(request):

    # Get start and end points
    start = int(request.GET.get("start") or 0)
    end = int(request.GET.get("end") or (start + 1))

    # Load the posts saved in the platform
    posts = userPost.objects.all()

    # Generate a list of posts
    posts = list(posts.order_by("-timestamp").all())
    data = []
    for i in range(start, end + 1):
        data.append(posts[i].serialize())

    # Artificially delay speed of response
    time.sleep(1)

    # Return a list of posts
    return JsonResponse({"posts": data})
    # return JsonResponse([post.serialize() for post in posts], safe=False)

