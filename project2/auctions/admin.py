from django.contrib import admin
from .models import User, AuctionListing, Bid, Comment

@admin.register(AuctionListing)
class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'starting_bid', 'is_active', 'category', 'created_at')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('auction_listing', 'bidder', 'amount', 'timestamp')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('auction_listing', 'commenter', 'content', 'timestamp')