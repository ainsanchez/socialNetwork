import json
import time

from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt


from .forms import NewPost, Edit
from .models import User, userPost, Community


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

    # Load the posts saved in the platform
    posts = userPost.objects.all()

    # Generate a list of posts
    posts = list(posts.order_by("-timestamp").all())

    # Transforming the data into a Paginator object
    # Retrieve all data from the model
    paginator = Paginator(posts, 10) 

    # Paginate with 10 items per page
    page_number = request.GET.get("page") 
    page_obj = paginator.get_page(page_number)

    # Retrieve data for the current page
    # newData = list(page_obj.object_list.values()) 
    serialized_data = [post.serialize() for post in page_obj.object_list]

    # Get signed-in user
    signedInUser = request.user.username

    # Artificially delay speed of response
    time.sleep(1)

    # return JsonResponse({"posts": data})
    return JsonResponse({"posts": serialized_data,
                         "total_pages": paginator.num_pages,
                         "has_next": page_obj.has_next(),
                         "has_previous": page_obj.has_previous(),
                         "page_number": page_obj.number,
                         "signedInUser": signedInUser})

    # return JsonResponse([post.serialize() for post in posts], safe=False)


# Register followers for user community
def addFollower(request):

    # Adding a follower must occur via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status = 400)
    
    # Check for user followers
    username = json.loads(request.follower)

    # Define a user's community
    user = User.objects.get(username=username)
    community = Community.objects.get(user=user)

    # Check if the follower is already registered in the user's community
    follower = request.user.username
    newFollower = User.objects.get(usernamme=follower)
    try: 
        community.followers.get(username=follower)
        return JsonResponse({
            "error": f"User {follower} is already following"
        })
    # If it is not registered, then add it to the user's community and update the # of folowers
    except User.DoesNotExist:
        community.followers.add(newFollower)
        community.number_of_followers += 1
        community.save()

    return JsonResponse({"message": "Follower added successfully"}, status = 201)


# Get user profile data
@login_required
def profile(request, username):

    # Search for the user
    user = User.objects.get(username=username)

    # Search for the posts of the user
    posts = userPost.objects.filter(user=user)

    # Get signed-in user
    signedInUser = request.user.username

    # Serialize the user posts 
    posts = list(posts.order_by("-timestamp").all())
    data = []
    for i in range(0, len(posts)):
        data.append(posts[i].serialize())

    # Obtain the number of followers
    followers = Community.objects.get(user=user).followers.all()
    nFollowers = len(followers)

    #Obtain the number of follows
    user_followers = user.user_followers.all()
    nUserFollowers = len(user_followers)

    # Return the JsonResponse
    return JsonResponse({"posts": data, 
                         "user": user.username, 
                         "nFollowers": nFollowers,
                         "nUserFollowers": nUserFollowers,
                         "signedInUser": signedInUser})


@login_required
def following(request, username):

    # Identify the users that the user is following
    user = User.objects.get(username=username)
    community = Community.objects.filter(followers=user)

    # Apply a loop to extract all users in an array
    data = []
    for i in range(0, len(community)):
        data.append(community[i].user.username)

    # Load posts from the user array to display
    users = User.objects.filter(username__in=data)
    posts = userPost.objects.filter(user__in=users)

    # Serialize the user posts for the JsonResponse
    posts = list(posts.order_by("-timestamp").all())
    newData = []
    for i in range(0, len(posts)):
        newData.append(posts[i].serialize())

    # Artificially delay speed of response
    time.sleep(1)

    # Return list of posts
    return JsonResponse({"posts": newData})


# Edit a post
@csrf_exempt
@login_required
def edit(request, post_id):

    if request.method == "GET":
        # Load the post to edit
        post = userPost.objects.get(pk=post_id)

        # Set the context
        content = post.content
        # context = {
        #    'edit': Edit(initial={'textarea': post.content}),
        #    'post_id': post_id
        #}
        #return render(request, "network/edit.html", context)
        return JsonResponse({"content": content})
    
    elif request.method == "PUT":
        # Check the edition made to the post
        data = json.loads(request.body)
        content = data.get("content")
        # data = request.POST
        # edition = data.get('edition')
        
        print(content)

        # Get the post to be updated
        post = userPost.objects.get(pk=post_id)
        print(post_id)

        #Update the value of the post
        post.content = content
        post.save()

        #return JsonResponse({"message": "Post updated successfully"}, status=201)
        return HttpResponse(status=204)

        #form = Edit(request.POST)
        #if form.is_valid():
            # Get the value from the textarea
        #    textarea = form.cleaned_data["body"]
        #    print(textarea)
            # Get the post to be updated
        #    post = userPost.objects.get(pk=post_id)
            # Update the value of the post
        #    post.content = textarea
        #    post.save()
        #    return HttpResponse('<p>Info Saved!</p>')
        #else:
        #    return HttpResponse('<p>Info is not Valid!</p>')        


# Get a community based on the profile/username request 
# -- Notice that this page is not uploaded 
@login_required
def followers_content(request, username):

    # Filter user based on username, and then query his/her community
    user = User.objects.get(username=username)

    # Then query user's community to display his/her profile info
    community = Community.objects.filter(user=user)

    # If user does not have a community yet, then create one with no followers
    if len(community) < 1:
        setCommunity = Community.objects.create(user=user)
        setCommunity.save()
        # Update community
        community = Community.objects.filter(user=user)
        # Add a return just to load the page ---
        return JsonResponse({"user": user.username, "community": community[0].number_of_followers})
    else:
        # Create an array with the followers from the user's community
        followers = community[0].followers.all()
        data = []
        for follower in followers:
            data.append(follower.username)

    # Finally, request the posts published by user followers
    users = User.objects.filter(username__in=data)
    posts = userPost.objects.filter(user__in=users)

    # Generate a list of posts
    posts = list(posts.order_by("-timestamp").all())
    dataFinal = []
    for i in range(0, len(posts)):
        dataFinal.append(posts[i].serialize())

    # Use Paginator to set posts in 10 item pages
    paginator = Paginator(dataFinal, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Artificially delay speed of response
    time.sleep(1)

    # Return a list of posts
    # return JsonResponse({"posts": dataFinal, "user": user, "community": community})
    return JsonResponse({"posts": dataFinal, "user": user.username,
                          "community": community[0].number_of_followers,
                           "page_obj": page_obj})
