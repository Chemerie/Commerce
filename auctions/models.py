from django.contrib.auth.models import AbstractUser
from django.db import models
# from django import forms

class User(AbstractUser):
    pass

class Category(models.Model):
	name = models.CharField(max_length=64)
	def __str__(self):
		return f"{self.name}"



class AuctionListing(models.Model):
	title = models.CharField(max_length=64)
	description = models.TextField()
	bidstart =  models.IntegerField()
	imgurl = models.URLField(blank=True)
	case = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="types", blank=True)
	time_created = models.DateTimeField(auto_now_add=True)
	creator = models.CharField(max_length=64)
	winner = models.CharField(max_length=64, blank=True)



class Bids(models.Model):
	bid =  models.IntegerField()
	auctionlistings = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
	def __str__(self):
		return f"{self.bid}"

class WhatchList(models.Model):
	name = models.CharField(max_length=64)
	auctionlist= models.ForeignKey(AuctionListing, on_delete=models.CASCADE)

class ClossedBids(models.Model):
	title = models.CharField(max_length=64)
	description = models.TextField()
	creator = models.CharField(max_length=64)
	winner = models.CharField(max_length=64)


class Comment(models.Model):
	commentor = models.CharField(max_length=64)
	comment = models.TextField()
	commented_on = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)


# class ListCategory(models.Model):
# 	cat_name = models.CharField(max_length=64)
# 	cat_auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
# class Comments(models.Model):
# 	comment = models.TextField()
# 	def __str__(self):
# 		return f"{self.comment}"
    



#     class PostModelForm(forms.ModelForm):
#     description = forms.CharField(widget=forms.Textarea)
#     class Meta:
#         model = AuctuonListing

