import json

# from .paypal import PayPalClient

from account.models import Address
from django.contrib import messages
from basket.basket import Basket
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from .models import DeliveryOptions
from django.views.generic import (
    FormView,
    TemplateView,
    UpdateView,
    View,
    ListView,
    CreateView,
)

from orders.models import Order, OrderItem

class DeliveryChoices(LoginRequiredMixin, ListView):
    template_name = 'checkout/delivery_choices.html'
    context_object_name = 'deliveryoptions'

    def get_queryset(self):
        queryset = DeliveryOptions.objects.filter(is_active=True)
        return queryset

class BasketUpdateDelivery(LoginRequiredMixin, View):
    def post(self, request, *args):
        basket = Basket(request)
        if request.POST.get('action') == 'post':
            delivery_option = int(request.POST.get("deliveryoption"))
            delivery_type = DeliveryOptions.objects.get(id=delivery_option)
            updated_total_price = basket.basket_update_delivery(delivery_type.delivery_price)

            session = request.session
            if "purchase" not in request.session:
                session["purchase"] = {
                    "delivery_id": delivery_type.id,
                }
            else:
                session["purchase"]["delivery_id"] = delivery_type.id
                session.modified = True

            response = JsonResponse({"total": updated_total_price, "delivery_price": delivery_type.delivery_price})
            return response

class DeliveryAddress(LoginRequiredMixin, ListView):
    template_name = 'checkout/delivery_address.html'
    context_object_name = 'addresses'

    def get(self, request, *args, **kwargs):
        session = request.session
        if "purchase" not in request.session:
            messages.success(request, "Please select delivery option")
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

        addresses = self.get_queryset()

        if "address" not in request.session:
            session["address"] = {"address_id": str(addresses[0].id)}
        else:
            session["address"]["address_id"] = str(addresses[0].id)
            session.modified = True
            
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Address.objects.filter(customer=self.request.user).order_by("-default")
        return queryset

class PaymentSelection(LoginRequiredMixin, TemplateView):
    template_name = 'checkout/payment_selection.html'

    def get(self, request, *args, **kwargs):
        session = request.session

        if 'address' not in session:
            messages.success(request, "Please select address option")
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
            
        return super().get(request, *args, **kwargs)

################$
# PayPal
################$

class PaymentComplete(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pass
        # PPClient = PayPalClient()

        # body = json.loads(request.body)
        # data = body["orderID"]
        # user_id = request.user.id

        # requestorder = OrdersGetRequest(data)
        # response = PPClient.client.execute(requestorder)

        # basket = Basket(request)
        # order = Order.objects.create(
        #     user_id=user_id,
        #     full_name=response.result.purchase_units[0].shipping.name.full_name,
        #     email=response.result.payer.email_address,
        #     address1=response.result.purchase_units[0].shipping.address.address_line_1,
        #     address2=response.result.purchase_units[0].shipping.address.admin_area_2,
        #     postal_code=response.result.purchase_units[0].shipping.address.postal_code,
        #     country_code=response.result.purchase_units[0].shipping.address.country_code,
        #     total_paid=response.result.purchase_units[0].amount.value,
        #     order_key=response.result.id,
        #     payment_option="paypal",
        #     billing_status=True,
        # )
        # order_id = order.pk

        # for item in basket:
        #     OrderItem.objects.create(order_id=order_id, product=item["product"], price=item["price"], quantity=item["qty"])

        # return JsonResponse("Payment completed!", safe=False)


class PaymentSuccessful(LoginRequiredMixin, TemplateView):
    template_name = 'checkout/payment_successful.html'

    def get(self, request, *args, **kwargs):
        basket = Basket(request)
        basket.clear()

        return super().get(request, *args, **kwargs)