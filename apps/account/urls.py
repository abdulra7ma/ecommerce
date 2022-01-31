from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView

from . import views
from .forms import PwdResetConfirmForm, PwdResetForm, UserLoginForm

app_name = "account"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="account/login.html", form_class=UserLoginForm
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="/account/login/"),
        name="logout",
    ),
    path("register/", views.AccountRegister.as_view(), name="register"),
    path(
        "activate/<slug:uidb64>/<slug:token>/", views.account_activate, name="activate"
    ),
    path("reactivate/", views.AccountReactivate.as_view(), name="reactivate"),
    path(
        "reactivate_confirm/<slug:uidb64>/<slug:token>/",
        views.account_activate,
        name="reactivate_confirm",
    ),
    # password rest
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="account/password_reset/password_reset_form.html",
            success_url="password_reset_email_confirm",
            email_template_name="account/password_reset/password_reset_email.html",
            form_class=PwdResetForm,
        ),
        name="pwdreset",
    ),
    path(
        "password_reset_confirm/<uidb64>/<token>",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="account/password_reset/password_reset_confirm.html",
            success_url="/account/password_reset_complete/",
            form_class=PwdResetConfirmForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset/password_reset_email_confirm/",
        TemplateView.as_view(template_name="account/password_reset/reset_status.html"),
        name="password_reset_done",
    ),
    path(
        "password_reset_complete/",
        TemplateView.as_view(template_name="account/password_reset/reset_status.html"),
        name="password_reset_complete",
    ),
    # dashboard
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("profile/edit/", views.EditDetailsView.as_view(), name="edit_details"),
    path("profile/delete_user/", views.DeleteUser.as_view(), name="delete_user"),
    path(
        "profile/delete_confirm/",
        TemplateView.as_view(template_name="account/dashboard/delete_confirm.html"),
        name="delete_confirmation",
    ),
    # Address
    path("addresses/", views.AddressView.as_view(), name="addresses"),
    path("add_address/", views.AddAddress.as_view(), name="add_address"),
    path("addresses/edit/<slug:id>/", views.EditAddress.as_view(), name="edit_address"),
    path("addresses/delete/<slug:id>/", views.DeleteAddress.as_view(), name="delete_address"),
    path("addresses/set_default/<slug:id>/", views.SetDefaultView.as_view(), name="set_default"),
    # Wish List
    path("wishlist", views.Wishlist.as_view(), name="wishlist"),
    path("wishlist/add_to_wishlist/<int:id>", views.WishlistAdd.as_view(), name="user_wishlist"),
    # orders
    path('orders', views.UserOrders.as_view(), name='orders')
]
