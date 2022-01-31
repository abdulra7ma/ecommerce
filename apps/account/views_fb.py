from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import FormView, TemplateView, UpdateView

from .forms import RegistrationForm, UserEditForm, UserReactivateForm
from .models import Customer
from .tokens import account_activation_token


@login_required
def edit_details(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)

        if user_form.is_valid():
            user_form.save()

    else:
        user_form = UserEditForm(instance=request.user)

    return render(request, "account/dashboard/edit_details.html", {"form": user_form})


def account_register(request):

    if request.user.is_authenticated:
        return redirect("account:dashboard")

    if request.method == "POST":
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.email = registerForm.cleaned_data["email"]
            user.set_password(registerForm.cleaned_data["password"])
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
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
            messages.success(
                request,
                "You have registered succesfully and activation token has been send.",
            )
            return HttpResponseRedirect(reverse("account:register"))
    else:
        registerForm = RegistrationForm()
    return render(request, "account/registration/register.html", {"form": registerForm})


@login_required
def delete_user(request):
    user = Customer.objects.get(user_name=request.user)
    user.is_active = False
    user.save()
    logout(request)
    return redirect("account:delete_confirmation")


def account_reactivate(request):

    if request.user.is_authenticated:
        return redirect("account:dashboard")

    if request.method == "POST":
        reactivate_form = UserReactivateForm(request.POST)
        if reactivate_form.is_valid():
            email = reactivate_form.cleaned_data["email"]
            user = Customer.objects.filter(email=email)
            if user.exists():
                user = user.first()
                current_site = get_current_site(request)
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
                    request, "Your request has been sended. Please check your email."
                )
                return HttpResponseRedirect(reverse("account:reactivate"))

    else:
        reactivate_form = UserReactivateForm()
    return render(
        request, "account/registration/reactivate.html", {"form": reactivate_form}
    )
