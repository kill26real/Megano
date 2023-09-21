from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import DetailView, UpdateView

from .models import Profile, Basket
from .forms import AuthForm, SignUpForm

from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core.cache import cache
from shop.models import Order, Category

from django.contrib.auth.mixins import LoginRequiredMixin





class MyLoginView(LoginView):
    template_name = 'user/signIn.html'
    # success_url = redirect('shop/catalog/')

    def get_success_url(self):
        return reverse('index')


class MyLogoutView(LogoutView):
    # template_name = 'users/logout.html'
    next_page = '/'


def register_view(request: HttpRequest):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            date_of_birth = form.cleaned_data.get('date_of_birth')
            phone = form.cleaned_data.get('phone_number')
            e_mail = form.cleaned_data.get('e_mail')
            if form.cleaned_data.get('avatar'):
                avatar = form.cleaned_data.get('avatar')
                Profile.objects.create(
                    user=user,
                    phone_number=phone,
                    e_mail=e_mail,
                    avatar=avatar,
                )
            else:
                Profile.objects.create(
                    user=user,
                    phone_number=phone,
                    e_mail=e_mail,
                    avatar=' ',
                )
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)

            my_group = Group.objects.get(name='Пользователи')
            my_group.user_set.add(user)

            login(request, user)
            pk = user.id
            return redirect(f'user/{pk}')
    else:
        form = SignUpForm()
    context = {
        'form': form
    }
    return render(request, 'user/signUp.html', context=context)


class ProfileView(DetailView):
    template_name = 'user/profile.html'
    model = Profile
    context_object_name = 'user'

    def get_context_data(self, pk, **kwargs):
        if self.request.user.id != pk and not self.request.user.is_staff:
            raise PermissionError
        context = super().get_context_data(**kwargs)
        username = self.request.user.username

        categories_cache_key = f'categories:{username}'
        orders_cache_key = f'orders:{username}'
        orders = Order.objects.filter(user=self.object)
        categories = Category.objects.filter(user=self.object)

        user_account_cache_data = {
            categories_cache_key: categories,
            orders_cache_key: orders
        }

        data = cache.get_many(user_account_cache_data)

        if not data:
            cache.set_many(user_account_cache_data)
        context['categories'] = categories
        context['orders'] = orders
        context['form'] = SignUpForm
        return context



class ProfileUpdateView(UpdateView):
    model = Profile
    fields = ['city', 'date_of_birth', 'phone_number', 'e_mail', 'avatar']
    template_name = 'userapp/profile.html'

    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        if request.user.id != pk and not request.user.is_staff:
            raise PermissionError
        return super().dispatch(request, *args, **kwargs)


    def get_success_url(self):
        return reverse(
            'userapp:profile',
            kwargs={'pk': self.object.user.pk},
        )

