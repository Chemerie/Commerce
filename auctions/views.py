from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import *
from django.db.models import Max

# num_whatchlist = WhatchList.objects.all()


#lisiting form
class NewTaskForm(forms.Form):
    g_pass= (
        ("None", "None"),
        ("Home", "Home"),
        ("Electronics", "Electronics"),
        ("Toys", "Toys"),
        ("Kitchen", "Kitchen"),
        ("Furniture", "Furniture"),
        ("Fashion", "Fashion"),
        ("Material", "Material")

        )
    title = forms.CharField(max_length=64)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':30}))
    imgurl = forms.URLField()
    startbid = forms.IntegerField()
    category = forms.ChoiceField(choices=g_pass)
 
#Comment form
class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':50}))

#New bid form
class NewBidForm(forms.Form):
    new_bid = forms.IntegerField()

#Index Function: returns all the listings and bids. Equally personalizes Whatchlist incase the user is logged in
def index(request):
    #Get the whatchlist for the user
    using = request.user.username
    num_whatchlist = WhatchList.objects.filter(name=using)
    #Get all the listings
    listings = AuctionListing.objects.all()
    #Get all the bids
    bids = Bids.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings,
        "bids": bids,
        "num_whatchlist": num_whatchlist,
        })

#Login function; logs a user in after authentification
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

#Logout funtion
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

#Registration function
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


#Funtion to reate lisitng
@login_required
def createlist(request):
    #personalise whatchlist
    using = request.user.username
    num_whatchlist = WhatchList.objects.filter(name=using)
    #Get the available Categories for the user to chose
    categories = Category.objects.all()
    

   #In case of submission, lets validate and get form data
    if request.method == "POST":
        form = NewTaskForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            descriptiopn = form.cleaned_data["description"]
            imgurl = form.cleaned_data["imgurl"]
            startbid = form.cleaned_data["startbid"]
            category = form.cleaned_data["category"]

            data = request.POST.dict()
            creator = data.get("creator")
           


            #Save the listing
            m = Category()
            m.name = category
            m.save()
            f = AuctionListing(title=title, description=descriptiopn, bidstart=startbid, imgurl=imgurl, case=m, creator=creator, winner=using)
            f.save()

            #Redirect to index page
            return HttpResponseRedirect(reverse('index'))

    #initial loading of the form to create lisitng
    return render(request, "auctions/createlist.html", {
        "form":NewTaskForm(),
        "categories": categories,
        
        "num_whatchlist": num_whatchlist,
        "using":using,
        
        })


#Function for particular lisitng
def updatelist(request, list_id):
    try:
        #personalise whatchlist
        using = request.user.username
        num_whatchlist = WhatchList.objects.filter(name=using)
        #Get particular listing using the id
        list_auction = AuctionListing.objects.get(id=list_id)
        #Get comments for the lisitng
        comments = Comment.objects.filter(commented_on=list_auction)
        #Get bids for the lisitng
        bids = list_auction.bids.all()
        max_bid = list_auction.bidstart

        # Incase somebody makes a bid, get the bid and validate it, 
        # making sure it's not equall to or lower than the current bid 
        # equally set the winner as the current user who make the current bid
        #since his/he bid is the highest so far
        if request.method == "POST":
            form = NewBidForm(request.POST)
            if form.is_valid():
                bid = int(form.cleaned_data["new_bid"])
                data = request.POST.dict()
                winner = data.get("winner")
                #Incase the user input lower bid than the current bid
                if list_auction.bidstart >= bid:
                    return render(request, "auctions/updatelist.html", {
                        "list_auction":list_auction,
                        "bids": bids,
                        "max_bid": max_bid,
                        "form": NewBidForm(),
                        "form1": CommentForm(),
                        "message": "Your bid must be equal to or greater than the current bid.",
                        "num_whatchlist": num_whatchlist,
                        "comments": comments,

                        })
                #incase of currect input, save the bid and update the starting bid to the current high bid
                else:
                    f = Bids(bid=bid, auctionlistings=list_auction)
                    f.save()
                    list_auction.bidstart=bid
                    list_auction.winner = winner
                    list_auction.save()
                    #After saving, redirect to our current page
                    return HttpResponseRedirect(reverse("updatelist", args=(list_id,)))

                

            

        else:#A whole lot of informations are needed at the initial loading of the page
            return render(request, "auctions/updatelist.html", {
                "list_auction":list_auction,
                "bids": bids,
                "max_bid": max_bid,
                "form": NewBidForm(),
                "form1": CommentForm(),
                "num_whatchlist": num_whatchlist,
                "comments": comments,

                })
    except:
        return HttpResponseRedirect(reverse("closed"))   

#When the user clicks on whatchlist
@login_required
def whatchlist(request, list_id):
    try:
        using = request.user.username
        if request.method == "POST":
            #Get the curent listing ckeck whether it has been sent to the whatchlist
            #if already in whatchlist, delete else send to the whatchlist and redirect 
            #to the current page
            listing = AuctionListing.objects.get(id=list_id)
            check = WhatchList.objects.filter(auctionlist=listing)
            if check:
                check.delete()
            else:
                whatchlist = WhatchList()
                whatchlist.name = using
                whatchlist.auctionlist = listing
                whatchlist.save()
            return HttpResponseRedirect(reverse("updatelist", args=(list_id,)))
    except:
        return HttpResponseRedirect(reverse("closed"))
#When the user clicks on the Whatchlist on the menu bar
@login_required
def whatchout(request):
    using = request.user.username
    num_whatchlist = WhatchList.objects.filter(name=using)
    return render(request, "auctions/whatchlist.html", {
        "num_whatchlist": num_whatchlist,
        })

#When the user who is the lister of the current listing clicks on closebid
#deletes the current listing from the listing and whatchlist table in the database
#equally poppulates the deleted bid table in the databse with deleted lising information
@login_required
def closedbid(request, list_id):
    listing = AuctionListing.objects.get(id=list_id)
    win = ClossedBids(title=listing.title, description=listing.description, creator=listing.creator, winner=listing.winner)
    win.save()
    listing.delete()
    f= WhatchList.objects.filter(auctionlist=listing)
    f.delete()
    return HttpResponseRedirect(reverse("index"))

#When the user clicks on the Closed Bids on the menu bar
#displays information about closed bids.
#it eqally displayscongratration message to the user who is the winner of the bid
@login_required
def closed(request):
    using = request.user.username
    num_whatchlist = WhatchList.objects.filter(name=using)
    all_closed = ClossedBids.objects.all()
    return render(request, "auctions/closedbid.html", {
        "all_closed": all_closed,
        "num_whatchlist": num_whatchlist,
        })
#When a user posts a comment
#save the comment for the particular lisitng
@login_required
def commenting(request, list_id):
    if request.method == "POST":
        listing = AuctionListing.objects.get(id=list_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data["comment"]
            commentor = request.POST.get("commentor")
            cnome = Comment(commentor=commentor, comment=comment, commented_on=listing)
            cnome.save()
            return HttpResponseRedirect(reverse("updatelist", args=(list_id,)))
#When the user clicks on Category in the menu bar
#displays the the current categories
def category(request):
    categories = Category.objects.all()
    return render(request, "auctions/category.html", {
        "categories": categories
        })

#When the user clicks on  a particuar category
def categorylist(request, case):
    using = request.user.username
    num_whatchlist = WhatchList.objects.filter(name=using)
    f = Category.objects.get(name=case)
    categories = AuctionListing.objects.filter(case=f)
    return render(request, "auctions/categorylist.html", {
        "categories": categories,
        "num_whatchlist": num_whatchlist,
        })


