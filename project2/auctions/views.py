from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max

from .models import User, AuctionListing, Bid, Comment #, Category
from .forms import AuctionListingForm


def index(request):
    active_listings = AuctionListing.objects.filter(is_active=True)

    # Add the latest bid for each listing
    listings_with_bids = []
    for listing in active_listings:
        latest_bid = listing.bids.last()
        listings_with_bids.append({
            'listing': listing,
            'latest_bid': latest_bid,
        })

    return render(request, "auctions/index.html", {
        "listings_with_bids": listings_with_bids,
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
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


def place_bid(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(AuctionListing, pk=listing_id)
        bid_amount = request.POST.get("bid")
        if float(bid_amount) > listing.starting_bid:
            Bid.objects.create(
                amount=bid_amount,
                bidder=request.user,
                auction_listing=listing
            )
            return redirect("listing_detail", listing_id=listing.id)
        else:
            return render(request, "auctions/listing_detail.html", {
                "listing": listing,
                "error": "Bid must be higher than the starting bid."
            })

def add_comment(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(AuctionListing, pk=listing_id)
        content = request.POST.get("comment")
        Comment.objects.create(
            content=content,
            commenter=request.user,
            auction_listing=listing
        )
        return redirect("listing_detail", listing_id=listing.id)


@login_required
def create_listing(request):
    if request.method == "POST":
        form = AuctionListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user  # Associate the listing with the logged-in user
            listing.save()
            messages.success(request, "Your listing has been created!")
            return redirect("index")  # Redirect to the index page
        else:
            messages.error(request, "There was an error creating your listing. Please try again.")
    else:
        form = AuctionListingForm()
    
    return render(request, "auctions/create_listing.html", {"form": form})


def listing_detail(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    bids = Bid.objects.filter(auction_listing=listing)

    # Get the highest bid for the listing
    highest_bid = bids.aggregate(Max('amount'))['amount__max'] if bids.exists() else listing.starting_bid

    # Check if the user has already added this listing to their watchlist
    watchlisted = listing in request.user.watchlist.all() if request.user.is_authenticated else False

    # Check if the auction is closed and if the user has won the auction
    user_won = False
    if not listing.is_active and request.user.is_authenticated:
        highest_bidder = bids.order_by('-amount').first()
        if highest_bidder and highest_bidder.bidder == request.user:
            user_won = True

    if request.method == 'POST':
        # Handling placing a bid
        if 'bid' in request.POST:
            bid_amount = float(request.POST['bid_amount'])
            if bid_amount >= highest_bid and bid_amount >= listing.starting_bid:
                # Create a new bid
                new_bid = Bid(auction_listing=listing, bidder=request.user, amount=bid_amount)
                new_bid.save()
                messages.success(request, 'Your bid has been placed!')
                return redirect('listing_detail', listing_id=listing.id)
            else:
                messages.error(request, 'Your bid must be higher than the current bid and the starting bid.')

        # Handling adding/removing the listing from the watchlist
        if 'watchlist' in request.POST and request.user.is_authenticated:
            if watchlisted:
                request.user.watchlist.remove(listing)
                messages.success(request, 'Removed from your watchlist.')
            else:
                request.user.watchlist.add(listing)
                messages.success(request, 'Added to your watchlist.')

        # Handling closing the auction (only allowed for the creator)
        if 'close_auction' in request.POST and listing.owner == request.user:
            listing.is_active = False  # Close the auction
            listing.save()

            # Find the highest bidder
            highest_bidder = bids.order_by('-amount').first()
            if highest_bidder:
                # Set the current_bid to the highest bid
                listing.current_bid = highest_bidder.amount
                listing.save()
                messages.success(request, f'Auction closed. The highest bidder is {highest_bidder.bidder.username}.')
            else:
                messages.info(request, 'Auction closed. No bids were placed.')

            return redirect('listing_detail', listing_id=listing.id)

        # Handling comments
        if 'comment' in request.POST:
            comment_content = request.POST['comment']
            new_comment = Comment(auction_listing=listing, commenter=request.user, content=comment_content)
            new_comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('listing_detail', listing_id=listing.id)

    comments = Comment.objects.filter(auction_listing=listing)

    return render(request, 'auctions/listing_detail.html', {
        'listing': listing,
        'bids': bids,
        'highest_bid': highest_bid,
        'watchlisted': watchlisted,
        'user_won': user_won,  # Pass the user_won status to the template
        'comments': comments,
    })


@login_required
def watchlist(request):
    listings = request.user.watchlist.all()  # Retrieve the user's watchlisted listings
    return render(request, 'auctions/watchlist.html', {'listings': listings})

@login_required
def toggle_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    
    if request.method == "POST":
        if listing in request.user.watchlist.all():  # Check if the listing is already in the user's watchlist
            request.user.watchlist.remove(listing)  # Remove from watchlist
        else:
            request.user.watchlist.add(listing)  # Add to watchlist
        return redirect("listing_detail", listing_id=listing.id)
    
    return redirect("listing_detail", listing_id=listing.id)

def categories(request):
    categories = [choice[0] for choice in AuctionListing._meta.get_field('category').choices]
    return render(request, "auctions/categories.html", {"categories": categories})

def category_listings(request, category_name):
    listings = AuctionListing.objects.filter(category=category_name, is_active=True)
    return render(request, "auctions/category_listings.html", {
        "category_name": category_name,
        "listings": listings
    })