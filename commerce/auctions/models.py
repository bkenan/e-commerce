from django.contrib.auth.models import AbstractUser
from django.db import models


CATs = (
    ('a', 'Books'),
    ('b', 'Cars'),
    ('c', 'Computers'),
    ('d', 'Clothes'),
    ('e', 'Other'),
)


class User(AbstractUser):
    pass


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="user_comments")
    username = models.CharField(max_length=30, default="")
    comment = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.user}: {self.comment}"


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="user_bids")
    price = models.DecimalField(max_digits=10, decimal_places=1)

    def __str__(self):
        return f"{self.user} put a bid for {self.price}"


class Listing(models.Model):
    item = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=300, blank=True)
    category = models.CharField(max_length=10, choices=CATs)
    image = models.URLField(null=True, blank=True)
    comments = models.ManyToManyField(Comment, blank=True,
                                      related_name="comments")
    bids = models.ManyToManyField(Bid, blank=True, related_name="bids")
    seller = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="seller")
    closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.item}: costs {self.price} & offered by {self.seller}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE,
                                related_name="listings")

    def __str__(self):
        return f"{self.user.username} as {self.listing.id}"
