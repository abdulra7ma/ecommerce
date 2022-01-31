from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls.base import reverse
from django.views.generic import TemplateView, View

from store.models import Product

from .basket import Basket


class BasketSummary(TemplateView):
    """Return a Summary page with the selected items to be bought."""

    template_name = "basket/summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        basket = Basket(self.request)
        context["basket"] = basket
        return context


class BasketAdd(View):
    def get(self, request):
        return HttpResponseRedirect(reverse("basket:basket_summary"))

    def post(self, request):
        basket = Basket(request)

        if request.POST.get("action") == "post":
            product_id = int(request.POST.get("productid"))
            product_qty = int(request.POST.get("productqty"))
            product = get_object_or_404(Product, id=product_id)
            basket.add(product=product, qty=product_qty)

            basketqty = basket.__len__()
            response = JsonResponse({"qty": basketqty})
            return response


class BasketUpdate(View):
    def get(self, request):
        return HttpResponseRedirect(reverse("basket:basket_summary"))

    def post(self, request):
        basket = Basket(request)

        if request.POST.get("action") == "post":
            product_id = int(request.POST.get("productid"))
            product_qty = int(request.POST.get("productqty"))
            basket.update(product=product_id, qty=product_qty)

            basketqty = basket.__len__()
            baskettotal = basket.get_total_price()
            response = JsonResponse({"qty": basketqty, "subtotal": baskettotal})
            return response


class BasketDelete(View):
    def get(self, request):
        return HttpResponseRedirect(reverse("basket:basket_summary"))

    def post(self, request):
        basket = Basket(request)

        if request.POST.get("action") == "post":
            product_id = int(request.POST.get("productid"))
            basket.delete(product=product_id)

            basketqty = basket.__len__()
            baskettotal = basket.get_total_price()
            response = JsonResponse({"qty": basketqty, "subtotal": baskettotal})
            return response
