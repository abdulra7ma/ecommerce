from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.db.models.query_utils import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import (
    FormView,
    TemplateView,
    UpdateView,
    View,
    ListView,
    CreateView,
)
from django.views.generic.edit import DeleteView, DeletionMixin, BaseDeleteView
from store.models import Product

from .forms import RegistrationForm, UserEditForm, UserReactivateForm, UserAddressForm
from .models import Customer, Address
from .tokens import account_activation_token
from orders.models import Order

class Wishlist(LoginRequiredMixin, TemplateView):
    template_name = 'account/dashboard/user_wish_list.html'

    def get_queryset(self):
        queryset = Product.objects.filter(users_wishlist=self.request.user)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["wishlist"] = self.get_queryset()
        return context


class WishlistAdd(LoginRequiredMixin, View):
    def get(self, request, *args,**kwargs):
        product = self.get_object()
        if product.users_wishlist.filter(id=request.user.id).exists():
            product.users_wishlist.remove(request.user)
            messages.success(request, product.title + " has been removed from your WishList")
        else:
            product.users_wishlist.add(request.user)
            messages.success(request, "Added " + product.title + " to your WishList")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])
        
    def get_object(self):
        obj = get_object_or_404(Product, id=self.kwargs['id'])
        return obj

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "account/dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


class EditDetailsView(LoginRequiredMixin, FormView):
    template_name = "account/dashboard/edit_details.html"
    form_class = UserEditForm
    success_url = reverse_lazy("account:edit_details")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            form.save()

        return render(request, "account/dashboard/edit_details.html", {"form": form})


class AccountRegister(FormView):
    template_name = "account/registration/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("account:register")
    # email_service = EmailService()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("account:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email = form.cleaned_data["email"]
        user.set_password(form.cleaned_data["password"])
        user.is_active = False
        user.save()
        # self.email_service.send_message(
        #     subject, user, ...
        # )
        current_site = get_current_site(self.request)
        subject = "Activate your Account"
        message = render_to_string(
            "account/registration/account_activation_email.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )
        user.email_user(subject=subject, message=message)
        return render(self.request, "account/registration/register_email_confirm.html")


class DeleteUser(LoginRequiredMixin, DeletionMixin, View):
    success_url = reverse_lazy("account:delete_confirmation")

    def delete(self, request, *args: str, **kwargs):
        user = Customer.objects.get(user_name=request.user)
        user.is_active = False
        user.save(update_fields=['is_active'])
        logout(request)
        return HttpResponseRedirect(self.success_url)

    def get(self, request):
        user = Customer.objects.get(user_name=request.user)
        user.is_active = False
        user.save()
        logout(request)
        return HttpResponseRedirect(self.success_url)


class AccountReactivate(FormView):
    template_name = "account/registration/reactivate.html"
    form_class = UserReactivateForm

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = Customer.objects.filter(email=email)
        if user.exists():
            user = user.first()
            current_site = get_current_site(self.request)
            subject = "Reactivate your Account"
            message = render_to_string(
                "account/registration/account_reactivation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            user.email_user(subject=subject, message=message)
            messages.success(
                self.request, "Your request has been sended. Please check your email."
            )
            return HttpResponseRedirect(reverse("account:reactivate"))


def account_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Customer.objects.get(pk=uid)
    except Exception as e:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect("account:dashboard")
    else:
        return render(request, "account/registration/activation_invalid.html")


class AddressView(LoginRequiredMixin, ListView):
    """ View for listing the avaialble addresses in the DB  """
    template_name = "account/dashboard/addresses.html"
    context_object_name = "addresses"

    def get_queryset(self):
        queryset = Address.objects.filter(customer=self.request.user)
        return queryset


class AddAddress(LoginRequiredMixin, CreateView):
    """ View for adding an address  """
    template_name = "account/dashboard/edit_addresses.html"
    form_class = UserAddressForm

    def form_valid(self, form) -> HttpResponse:
        address_form = form.save(commit=False)
        address_form.customer = self.request.user

        if Address.objects.filter(customer=self.request.user).count() <= 0:
            address_form.default = True

        address_form.save()
        return HttpResponseRedirect(reverse("account:addresses"))


class EditAddress(UpdateView):
    """ View for editing the selected address  """
    template_name = 'account/dashboard/edit_addresses.html'
    model = Address
    form_class = UserAddressForm

    def get_object(self):
        try:
            obj = Address.objects.get(pk=self.kwargs['id'], customer=self.request.user)
        except Address.DoesNotExist:
            pass
        else:
            return obj
    
    def form_valid(self, form) -> HttpResponse:
        form.save()
        prev_url = self.request.META.get('HTTP_REFERER')

        if 'delivery_address' in prev_url:
            return HttpResponseRedirect(reverse("checkout:delivery_address"))

        return HttpResponseRedirect(reverse("account:addresses"))
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs

        
class DeleteAddress(LoginRequiredMixin, BaseDeleteView):
    """ View for deleting the selected address  """
    success_url = reverse_lazy('account:addresses')

    def get_object(self, queryset=None):
        obj = Address.objects.get(pk=self.kwargs['id'], customer=self.request.user)
        return obj

    def get(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()
        return HttpResponseRedirect(reverse("account:addresses"))


class SetDefaultView(LoginRequiredMixin, View):
    """
    View for updating the state of the default address
    """
    
    def get(self, request, *args, **kwargs):
        Address.objects.filter(customer=request.user, default=True).update(default=False)
        Address.objects.filter(pk=self.kwargs['id'], customer=request.user).update(default=True)

        previous_url = request.META.get("HTTP_REFERER")

        print(previous_url)

        if "delivery_address" in previous_url:
            return redirect("checkout:delivery_address")
       
        return HttpResponseRedirect(reverse("account:addresses"))


class UserOrders(LoginRequiredMixin, ListView):
    """
    Return all the order that associated 
    with current logged in user and billing status is True
    """

    template_name = 'account/dashboard/user_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        user_id = self.request.user
        queryset = Order.objects.filter(user=user_id).filter(billing_status=True)
        return queryset
    