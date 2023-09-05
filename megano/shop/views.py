from django.shortcuts import render
from .models import Order, Product, Comment, Category, Image
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect


class ProductsListView(ListView):
    template_name = 'shop/catalog.html'
    queryset = Product.objects.all()
    context_object_name = 'catalogCards'


class ProductsIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        popular = Product.objects.order_by('sort_index', 'sold_amount')[:8]
        limited = Product.objects.filter(limited=True)[:15]
        context = {
            'popularCards': popular,
            'limitedCards': limited,
        }
        return render(request, 'shop/index.html', context=context)

# class ProductsIndexView(View):
#
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['images'] = Image.objects.filter(post=self.object.pk)
#         context['popular'] = Product.objects.order_by('sort_index', 'sold_amount')[:8]
#         context['limited'] = Product.objects.filter(limited=True)[:15]
#         return context


# class ProductsIndexView(View):
#     template_name = 'shop/index.html'
#     queryset = Product.objects.all()
#     context_object_name = 'cards'
#
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['images'] = Image.objects.filter(post=self.object.pk)
#         return context




class ProductsDetailsView(DetailView):
    template_name = 'shop/product.html'
    model = Product
    slug_field = Product.name
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = Image.objects.filter(product=self.object.pk)
        return context




# class MyView(ListView):
#     context_object_name = "data"
#     template_name = "myapp/template.html"
#
#     def get_queryset(self):
#         myset = {
#             "first": Model1.objects.all(),
#             "second": Model2.objects.all(),
#         }
#         return myset