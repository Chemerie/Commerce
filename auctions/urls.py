from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlist", views.createlist, name="createlist"),
    path("<int:list_id>/updatelist", views.updatelist, name="updatelist"),
    path("<int:list_id>/whatchlist", views.whatchlist, name="whatchlist"),
    path("whatchout", views.whatchout, name="whatchout"),
    path("<int:list_id>closedbid", views.closedbid, name="closedbid"),
    path("closed", views.closed, name="closed"),
    path("<int:list_id>commenting", views.commenting, name="commenting"),
    path("category", views.category, name="category"),
    path("<str:case>categorylist", views.categorylist, name="categorylist"),
]
