from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from .models import *
from django.contrib.auth.decorators import login_required


# Defining classes for the Listing, Comment and Bid forms from line 12 to 25:
class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['item', 'price', 'image', 'description', 'category']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["username", "comment"]


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ["price"]


# Function for the index page:
def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


# Function for the login page:
def login_view(request):
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Checking authentication
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


# Function for the logout page:
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# Registration setup:
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# Here we are building the system to create listings for the items:
@login_required
def create_listing(request):
    if request.method == "POST":
        user = User.objects.get(username=request.user)
        form = ListingForm(request.POST)
        listing = form.save(commit=False)
        listing.seller = user
        listing.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create.html", {
            "form": ListingForm()
        })


# This is the main function for the website's functionality as
# it contains the logics to view listings, to control bids and watchlist.
# The sellers cannot bid on their items.
def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        user = User.objects.get(username=request.user)
        if request.POST.get("button") == "Add":
            if not user.watchlist.filter(listing=listing):
                watchlist = Watchlist()
                watchlist.user = user
                watchlist.listing = listing
                watchlist.save()
            return HttpResponseRedirect(reverse('listing', args=(listing.id,)))
        elif request.POST.get("button") == "Delete":
            user.watchlist.filter(listing=listing).delete()
            return HttpResponseRedirect(reverse('listing', args=(listing.id,)))
        if not listing.closed:
            if request.POST.get("button") == "Close":
                listing.closed = True
                listing.save()
            else:
                price = int(request.POST["price"])
                bids = listing.bids.all()
                if user.username != listing.seller.username:
                    if price <= listing.price:
                        return render(request, "auctions/listing.html", {
                            "listing": listing,
                            "form": BidForm(),
                            "message": "Error!"
                        })
                    form = BidForm(request.POST)
                    if form.is_valid():
                        bid = form.save(commit=False)
                        bid.user = user
                        bid.save()
                        listing.price = price
                        listing.bids.add(bid)
                        listing.save()
                    else:
                        return render(request, 'auctions/listing.html', {
                            "form": form
                        })
        return HttpResponseRedirect(reverse('listing', args=(listing.id,)))
    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "form": BidForm()
        })


# This is for the category page for different items
def categories(request):
    return render(request, 'auctions/categories.html', {
        "categories": CATs,
    })


# The view insode the categories page for specific types:
def category_listings(request, category):
    listings = Listing.objects.filter(category__in=category[0])
    return render(request, 'auctions/cat_page.html', {
        "listings": listings,
        "category": dict(CATs)[category]
    })


# Watchlist page can only be accessed by the users:
@login_required
def watchlist(request):
    user = User.objects.get(username=request.user)
    return render(request, "auctions/watchlist.html", {
        "watchlist": user.watchlist.all()
    })


# Comments can only be written by the users and it's readable
# by other users too:
@login_required
def comment(request, listing_id):
    user = User.objects.get(username=request.user)
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        comment = form.save(commit=False)
        comment.user = user
        comment.save()
        listing.comments.add(comment)
        listing.save()
        return HttpResponseRedirect(reverse('listing', args=(listing.id,)))
    else:
        return render(request, "auctions/comment.html", {
            "form": CommentForm(),
            "listing_id": listing.id
        })
