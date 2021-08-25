from django.urls import include, path

from . import views

app_name = "checkout"

urlpatterns = [
    path("deliverychoices", views.DeliveryChoices.as_view(), name="deliverychoices"),
    path("basket_update_delivery/", views.BasketUpdateDelivery.as_view(), name="basket_update_delivery"),
    path("delivery_address/", views.DeliveryAddress.as_view(), name="delivery_address"),
    path("payment_selection/", views.PaymentSelection.as_view(), name="payment_selection"),
    path("payment_complete/", views.PaymentComplete.as_view(), name="payment_complete"),
    path("payment_successful/", views.PaymentSuccessful.as_view(), name="payment_successful"),
]