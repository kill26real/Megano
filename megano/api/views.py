from collections import OrderedDict
from datetime import datetime, timezone
from sqlite3 import IntegrityError

from django.contrib.auth.password_validation import validate_password, password_validators_help_texts
from django.contrib.auth.views import LoginView
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.encoding import force_str
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.request import HttpRequest, Request
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, \
    DestroyModelMixin
from rest_framework.generics import GenericAPIView, ListCreateAPIView, CreateAPIView, get_object_or_404, \
    RetrieveAPIView, UpdateAPIView, ListAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet, ViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, NotAcceptable
from rest_framework.metadata import SimpleMetadata
from rest_framework.relations import ManyRelatedField, RelatedField
from django.http import FileResponse, QueryDict
from django.contrib.auth.password_validation import validate_password

from user.serializers import ProfileSerializer
from user.models import Profile, Basket, BasketItem, ProfileImage
from shop.serializers import ProductShortSerializer, ProductSerializer, CategorySerializer, OrderSerializer, \
    ReviewSerializer, SaleSerializer, TagSerializer, ProductShortBasketSerializer
from shop.models import Product, Order, Specification, Category, Review, OrderItem, Payment, Tag
from shop.pagination import CatalogPagination
from manage.models import DeliveryType
from megano.settings import ITEMS_ON_PAGE

from .utils import create_user_account, get_and_authenticate_user, IsOwnerOrReadOnly, IsOwner
from .filters import CatalogFilter
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib import messages
import uuid


class RegisterView(CreateAPIView):
    """Представление для регистрации"""
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        username = data.get("username", None)
        name = data.get("name", None)
        password = data.get("password", None)
        user = request.user

        basket = None
        if request.session['anonym']:
            basket = Basket.objects.get(session_id=request.session['anonym'])

        try:
            validate_password(password, user)
        except ValidationError as e:
            Response(status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(username=username, first_name=name)
        user.set_password(password)
        user.save()

        user = authenticate(username=username, password=password)
        login(request, user)

        if basket:
            basket.user = user
            basket.session_id = ''
            basket.save()

        return Response({'code': '200', 'user': user.username, 'message': 'successfully sign up'},
                        status=status.HTTP_200_OK)


class MyLoginView(APIView):
    """Представление для авторизации"""
    authentication_classes = [SessionAuthentication]
    permission_classes = (AllowAny,)
    def post(self, request, format=None):
        data = json.loads(request.body)
        username = data.get('username', None)
        password = data.get('password', None)

        basket_anonym = None
        if request.session['anonym']:
            basket_anonym = Basket.objects.get(session_id=request.session['anonym'])

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            basket = Basket.objects.get(user=user)
            if basket_anonym:
                for item in basket_anonym.items.all():
                    try:
                        old_item = BasketItem.objects.get(product=item.product, basket=basket)
                        old_item.quantity += item.quantity
                        old_item.save()

                    except ObjectDoesNotExist:
                        with transaction.atomic():
                            BasketItem.objects.create(product=item.product, quantity=item.quantity, basket=basket)

                basket_anonym.delete()

            return Response({'code': '200', 'user': username, 'message': 'successfully login'},
                            status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'Unauthorized',
                'message': 'Username/password combination invalid.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """Представление для выхода из системы"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = [SessionAuthentication]

    def post(self, request, format=None):
        if request.user.is_authenticated:
            username = request.user.username
            logout(request)
            return Response({'code': '200', 'user': username, 'message': 'successfully logout'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'code': '500', 'message': 'user is not authenticated'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryList(APIView):
    """Представление для получения списка категорий"""
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
        queryset = Category.objects.filter(parent__isnull=True)
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CatalogView(ListAPIView):
    """Представление для получения каталога"""
    permission_classes = (AllowAny,)
    def get_queryset(self):
        queryset = Product.objects.all()

        if self.request.query_params:
            name = self.request.query_params.get("filter[name]")
            if name:
                queryset = queryset.filter(Q(full_description__icontains=name) | Q(title__icontains=name))

                # descr_ids = list(queryset.filter(full_description__icontains=name).values_list('id', flat=True))
                # title_ids = list(queryset.filter(title__icontains=name).values_list('id', flat=True))
                # ids_list = descr_ids + title_ids
                # queryset = queryset.filter(id__in=ids_list)

            category_id = self.request.query_params.get("category")
            if category_id:
                category = Category.objects.get(id=category_id)
                if category.parent:
                    queryset = queryset.filter(category=category)
                else:
                    categories = Category.objects.filter(parent=category)
                    queryset = queryset.filter(Q(category__in=categories) | Q(category=category))

            try:
                tags = dict(self.request.query_params)['tags[]']
                tags_ids = [int(i) for i in tags]
                quer_tags = Tag.objects.filter(id__in=tags_ids)
                queryset = queryset.filter(tags__in=quer_tags)
            except KeyError:
                pass

            min_price = self.request.query_params.get("filter[minPrice]")
            if min_price:
                queryset = queryset.filter(price__gte=min_price)

            max_price = self.request.query_params.get("filter[maxPrice]")
            if max_price:
                queryset = queryset.filter(price__lte=max_price)

            free_delivery = self.request.query_params.get("filter[freeDelivery]")
            if free_delivery == 'true':
                queryset = queryset.filter(free_delivery=True)

            available = self.request.query_params.get("filter[available]")
            if available == 'true':
                queryset = queryset.filter(count__isnull=False)

            sort = self.request.query_params.get("sort")
            sort_type = self.request.query_params.get("sortType")
            if sort == 'reviews':
                if sort_type == 'dec':
                    queryset = sorted(queryset, key=lambda p: p.rating)
                else:
                    queryset = sorted(queryset, key=lambda p: -p.rating)
            if sort == 'date':
                if sort_type == 'dec':
                    queryset = queryset.order_by('date')
                else:
                    queryset = queryset.order_by('-date')
            if sort == 'price':
                if sort_type == 'dec':
                    queryset = queryset.order_by('-price')
                else:
                    queryset = queryset.order_by('price')
            if sort == 'rating':
                if sort_type == 'dec':
                    queryset = queryset.order_by('sold_amount')
                else:
                    queryset = queryset.order_by('-sold_amount')

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page_number = int(request.query_params.get('currentPage'))  # number
        start = (page_number - 1) * ITEMS_ON_PAGE
        end = ITEMS_ON_PAGE * page_number

        serializer = ProductShortSerializer(queryset[start:end], many=True)
        return Response(OrderedDict([
            ('items', serializer.data),
            ('currentPage', page_number),
            ('lastPage', round(len(queryset) / ITEMS_ON_PAGE))
        ]))


class ProductsPopularCatalogList(APIView):
    """Представление для получения списка популярных продуктов"""
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
        queryset = Product.objects.order_by('sold_amount')[:8]
        serializer = ProductShortSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductsLimitedCatalogList(APIView):
    """Представление для получения списка лимитированных продуктов"""
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
        queryset = Product.objects.filter(Q(limited=True) and Q())[:8]
        serializer = ProductShortSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SalesList(APIView):
    """Представление для получения продуктов со скидкой"""
    permission_classes = (AllowAny,)
    # ITEMS_ON_PAGE = megano.megano.settings.ITEMS_ON_PAGE
    """Представление для получения списка скидок"""
    def get(self, request, *args, **kwargs):
        page_number = int(request.query_params.get('currentPage'))  # number
        start = (page_number - 1) * ITEMS_ON_PAGE
        end = ITEMS_ON_PAGE * page_number

        now = datetime.now(timezone.utc)
        queryset = Product.objects.filter(~Q(sale_price__exact=0) and Q(date_from__lte=now) and Q(date_to__gte=now))

        serializer = SaleSerializer(queryset[start:end], many=True)
        return Response(OrderedDict([
            ('items', serializer.data),
            ('currentPage', page_number),
            ('lastPage', round(len(queryset)/ITEMS_ON_PAGE))
        ]))


class BannersList(APIView):
    """Представление для получения списка популярных продуктов"""
    permission_classes = (AllowAny,)
    def get(self, request, *args, **kwargs):
        queryset = Product.objects.order_by('sold_amount')[:8]
        serializer = ProductShortSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BasketDetail(APIView):
    """Представление для получения корзины, а также добавления и удаления продуктов"""
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        user = request.user
        product_id = data.get('id', None)
        quantity = data.get('count', None)

        if user.is_authenticated:
            basket = Basket.objects.get(user=user)
        else:
            try:
                basket = Basket.objects.get(session_id=request.session['anonym'])
            except:
                request.session['anonym'] = str(uuid.uuid4())
                basket = Basket.objects.create(session_id=request.session['anonym'])


        product = Product.objects.get(id=product_id)
        if product.count >= quantity:
            basket_item, created = BasketItem.objects.get_or_create(basket=basket, product=product)
            basket_item.quantity += int(quantity)
            basket_item.save()
        else:
            return Response({'message': 'quantity is more than we have'}, status=404)

        queryset = BasketItem.objects.filter(basket=basket.id)
        products = Product.objects.filter(basket_items__in=queryset)

        serializer = ProductShortBasketSerializer(products, context={"basket": basket},  many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request: Request):
        user = request.user
        if user.is_authenticated:
            basket, created = Basket.objects.get_or_create(user=user)
        else:
            try:
                basket = Basket.objects.get(session_id=request.session['anonym'])
            except:
                request.session['anonym'] = str(uuid.uuid4())
                basket = Basket.objects.create(session_id=request.session['anonym'])

        queryset = BasketItem.objects.filter(basket=basket.id)
        products = Product.objects.filter(basket_items__in=queryset)
        if products:
            serializer = ProductShortBasketSerializer(products, context={"basket": basket},  many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_200_OK)


    def delete(self, request: Request):
        data = json.loads(request.body)
        user = request.user
        product_id = data.get('id', None)
        quantity = data.get('count', None)

        if user.is_authenticated:
            basket = Basket.objects.get(user=user)
        else:
            try:
                basket = Basket.objects.get(session_id=request.session['anonym'])
            except:
                request.session['anonym'] = str(uuid.uuid4())
                basket = Basket.objects.create(session_id=request.session['anonym'])

        product = Product.objects.get(id=product_id)

        try:
            basket_item = BasketItem.objects.get(basket=basket, product=product)
        except ObjectDoesNotExist:
            return Response({'message': 'Product not in basket'}, status=404)

        if basket_item.quantity == quantity:
            basket_item.delete()
        elif basket_item.quantity > quantity:
            basket_item.quantity -= quantity
            basket_item.save()
        else:
            return Response({'message': 'Quantity more than in basket. Try again'}, status=404)

        queryset = BasketItem.objects.filter(basket=basket.id)
        products = Product.objects.filter(basket_items__in=queryset)
        if products:
            serializer = ProductShortBasketSerializer(products, context={"basket": basket}, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_200_OK)



class OrdersList(APIView):
    """Представление для получения и создания заказов"""
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = Order.objects.filter(user=user)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        user = request.user

        del_type = DeliveryType.objects.get(name='Regular')

        with transaction.atomic():
            order = Order.objects.create(user=user, delivery=del_type)

        for prod in data:
            id = prod['id']
            product = Product.objects.get(id=id)
            quantity = prod['count']

            with transaction.atomic():
                order_item = OrderItem.objects.create(order=order, product=product, quantity=quantity)

        basket = Basket.objects.get(user=user.id)
        for item in basket.items.all():
            item.delete()

        return Response(data={'orderId': order.id}, status=status.HTTP_200_OK)


class OrderDetailsView(APIView):
    """Представление для получения и изменения заказа"""
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        id = self.kwargs['pk']
        try:
            order = Order.objects.get(user=user_id, id=id)
        except ObjectDoesNotExist:
            return Response({'message': 'Order with this pk is not exist or order is not yours'}, status=404)

        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        user = request.user

        city = data.get('city', None)
        address = data.get('address', None)
        delivery_type = data.get('deliveryType', None)
        payment_type = data.get('paymentType', None)
        full_name = data.get('fullName', None)
        email = data.get('email', None)
        phone = data.get('phone', None)

        # try:
        #     validate_email(email)
        # except ValidationError:
        #     Response(status=status.HTTP_400_BAD_REQUEST)

        id = self.kwargs['pk']

        try:
            order = Order.objects.get(user=user.id, id=id)
        except ObjectDoesNotExist:
            return Response({'message': 'Order with this pk is not exist or order is not yours'}, status=404)

        if delivery_type == 'ordinary':
            del_type = DeliveryType.objects.get(name='Regular')
        else:
            del_type = DeliveryType.objects.get(name='Express')

        order.delivery = del_type
        order.city = city
        order.full_name = full_name
        order.email = email
        order.phone = phone
        order.address = address
        order.payment_type = payment_type
        order.save()

        if payment_type == 'someone':
            for item in order.items.all():
                item.product.count -= item.quantity
                item.product.sold_amount += item.quantity
                item.product.save()

        serializer = OrderSerializer(order)

        return Response(serializer.data)


class PaymentView(APIView):
    """Представление для оплаты заказа"""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        id = self.kwargs['pk']
        user = request.user

        try:
            order = Order.objects.get(id=id, user=user)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            Payment.objects.get(order=order, paid=True)
            return Response(status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            pass

        number = request.data.get('number')
        code = request.data.get('code')
        month = request.data.get('month')
        year = request.data.get('year')

        error = ''

        if len(number) != 16:
            error += 'Длинна номера карты не равна 16.'

        if len(code) != 3:
            error += 'Длинна кода карты не равна 3.'

        if int(month) < 1 or int(month) > 12:
            error += 'Месяц должен быть в диапазоне от 1 до 12.'

        if int(year) < 10 or int(year) > 99:
            error += 'Месяц должен быть в диапазоне от 10 до 99.'

        if int(number) % int(code) == 0 and not error: paid = True
        else: paid = False

        with transaction.atomic():
            payment = Payment.objects.create(order=order, user=user, number=number, code=code, paid=paid)

        if error != '':
            order.payment_error = error
            order.save()
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if paid:
            for item in order.items.all():
                item.product.count -= item.quantity
                item.product.sold_amount += item.quantity
                item.product.save()

        return Response(status=status.HTTP_200_OK)


class ProfileDetail(APIView):
    """Представление для получения и создания профиля"""
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        data = json.loads(request.body)
        full_name = data.get("fullName", None)
        email = data.get("email", None)
        phone = data.get("phone", None)

        profile, created = Profile.objects.get_or_create(user=user)

        profile.full_name = full_name
        profile.phone = phone
        profile.save()

        user.email = email
        user.save()

        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePassword(APIView):
    """ Представление для изменения пароля """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        data = json.loads(request.body)
        password_current = data.get("currentPassword", None)
        password = data.get("newPassword", None)

        if not user.check_password(password_current):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # if not validate_password(password):
            # message = ''
            # for text in password_validators_help_texts(validate_password(password)):
            #     message += text
            # return Response(status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()

        return Response(status=status.HTTP_200_OK)


class UpdateProfileAvatar(APIView):
    """Представление для обновления аватара в профиле"""
    parser_classes = (FormParser, MultiPartParser)
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.get(user=user)
        src = request.FILES["avatar"]
        if src:
            try:
                avatar = ProfileImage.objects.get(profile=profile)
                avatar.delete()
            except ObjectDoesNotExist:
                pass

            with transaction.atomic():
                ProfileImage.objects.create(src=src, profile=profile)

        return Response(status=status.HTTP_200_OK)


class TagListView(APIView):
    """Представление для получения списка тэгов"""
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        queryset = Tag.objects.all()
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductDetailsView(RetrieveAPIView):
    """Представление для получения детального описания продукта"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)


class ReviewView(APIView):
    """Представление для получения и создания отзывов на продукт"""
    permission_classes = (IsAuthenticated,)
    def post(self, request: Request, pk=None, *args, **kwargs) -> Response:
        data = json.loads(request.body.decode('utf-8'))
        user = request.user
        # product_id = self.kwargs['id']
        # author = data["author"]
        # email = data["email"]
        text = data["text"]
        rate = data["rate"]
        date = datetime.now()

        id = pk or request.query_params.get('id')
        product = Product.objects.get(id=id)

        with transaction.atomic():
            Review.objects.create(author=user, product=product, text=text, rate=rate, date=date)

        reviews = Review.objects.filter(product=product)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




# class OrdersList(ListCreateAPIView):
#     """Представление для получения и создания заказов"""
#     permission_classes = (IsAuthenticated, IsOwner)
#     authentication_classes = [SessionAuthentication]
#
#     def get_queryset(self):
#         queryset = Order.objects.all()
#         user = self.request.user
#         if not user.is_authenticated:
#             raise NotAuthenticated
#         if self.request.method == 'GET':
#             user_id = user.id
#             if not user.is_staff:
#                 queryset = Order.objects.filter(user=user_id)
#         return queryset
#
#     def get_serializer_class(self):
#         if self.request.method == "POST":
#             return CreateOrderSerializer
#         return OrderSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         user = request.user
#
#         city = request.data.get('city')
#         address = request.data.get('address')
#         promocode = request.data.get('promocode')
#         delivery_type = request.data.get('delivery_type')
#         payment_type = request.data.get('payment_type')
#         del_type = DeliveryType.objects.get(name=delivery_type)
#
#         order = Order.objects.create(user=user, city=city, address=address, promocode=promocode,
#                                      delivery_type=del_type, payment_type=payment_type)
#         order.save()
#
#         for product in Product.objects.all():
#             if product.title.replace(" ", "_") in request.data.keys():
#                 product_title_underline = product.title.replace(" ", "_")
#                 quantity = request.data.get(f'{product_title_underline}')
#                 if quantity == '':
#                     continue
#                 try:
#                     quantity_int = int(quantity)
#                 except ValueError:
#                     return Response({'code': '400', 'message': 'unexpected value for product quantity'},
#                                     status=status.HTTP_400_BAD_REQUEST)
#                 if quantity_int > product.count:
#                     return Response({'code': '400', 'message': f'we have only {product.count} items of '
#                                                                f'{product.title}, but {quantity_int} was given'},
#                                     status=status.HTTP_400_BAD_REQUEST)
#
#                 order_item = OrderItem.objects.create(order=order, product=product, quantity=quantity_int)
#                 order_item.save()
#
#         serializer = OrderSerializer(order)
#         return Response(serializer.data)
#
#
# # @extend_schema(methods=['PUT'], exclude=True)
# class OrderDetailsView(RetrieveUpdateDestroyAPIView):
#     """Представление для получения, изменения и удаления заказа"""
#     queryset = Order.objects.all()
#     permission_classes = [IsAuthenticated, IsOwner]
#     authentication_classes = [SessionAuthentication]
#
#     def get_serializer_class(self):
#         if self.request.method == "PUT":
#             return UpdateOrderSerializer
#         return OrderSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
#
#     def put(self, request, *args, **kwargs):
#         user_id = request.user.id
#         id = self.kwargs['pk']
#
#         try:
#             order = Order.objects.get(user=user_id, id=id)
#         except ObjectDoesNotExist:
#             return Response({'message': 'Order with this pk is not exist or order is not yours'}, status=404)
#
#
#
#         product_id = request.data.get('add_product').split(':')[1]
#         quantity = request.data.get('quantity_of_product_to_add')
#
#         try:
#             quantity_int = int(quantity)
#         except ValueError:
#             return Response({'code': '400', 'message': 'unexpected value for product quantity'},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         if quantity_int == 0:
#             pass
#         else:
#             product = Product.objects.get(id=product_id)
#             if quantity_int > product.count:
#                 return Response({'code': '400', 'message': f'we have only {product.count} items of '
#                                                            f'{product.title}, but {quantity_int} was given. Try again'},
#                                 status=status.HTTP_400_BAD_REQUEST)
#             order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
#             order_item.quantity += quantity_int
#             order_item.save()
#
#         delete_product_id = request.data.get('delete_product').split(':')[1]
#         delete_quantity = request.data.get('quantity_of_product_to_delete')
#
#         try:
#             delete_quantity_int = int(delete_quantity)
#         except ValueError:
#             return Response({'code': '400', 'message': 'unexpected value for product quantity'},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         if delete_quantity_int == 0:
#             pass
#         else:
#             order_item = OrderItem.objects.get(product=Product.objects.get(id=delete_product_id), order=order)
#             if delete_quantity_int > order_item.quantity:
#                 return Response({'code': '400', 'message': f'we have only {order_item.quantity} items of '
#                                                            f'{order_item.product.title}, but '
#                                                            f'{delete_quantity_int} was given. Try again'},
#                                 status=status.HTTP_400_BAD_REQUEST)
#             elif delete_quantity_int == order_item.quantity:
#                 order_item.delete()
#             else:
#                 order_item.quantity -= delete_quantity_int
#                 order_item.save()
#
#
#
#         city = request.data.get('city')
#         promocode = request.data.get('promocode')
#         address = request.data.get('address')
#         payment_type = request.data.get('payment_type')
#         delivery_type = request.data.get('delivery_type')
#
#         del_type = DeliveryType.objects.get(name=delivery_type)
#
#         order.city = city
#         order.address = address
#         order.promocode = promocode
#         order.payment_type = payment_type
#         order.delivery_type = del_type
#
#         order.save()
#
#         serializer = OrderSerializer(order)
#         return Response(serializer.data)



# class BasketDetail(UpdateModelMixin, ListModelMixin, GenericAPIView):
#     """Представление для получения корзины, а также добавления и удаления продуктов"""
#     permission_classes = (IsAuthenticated, IsOwner)
#     authentication_classes = [SessionAuthentication]
#
#     def get_queryset(self):
#         queryset = Basket.objects.all()
#         user = self.request.user
#         if not user.is_authenticated:
#             raise NotAuthenticated
#         user_id = user.id
#         if not user.is_staff:
#             queryset = Basket.objects.filter(user=user_id)
#         return queryset
#
#     def get_serializer_class(self):
#         if self.request.method == "POST":
#             return AddBasketItemSerializer
#         elif self.request.method == 'PATCH':
#             return DeleteBasketItemSerializer
#         return BasketSerializer
#
#     def post(self, request):
#         data = json.loads(request.body)
#
#         username = data.get('username', None)
#         password = data.get('password', None)
#         user_id = request.user.id
#         product_id = request.data.get('product_id')
#         quantity = request.data.get('quantity')
#
#         print(product_id)
#
#         basket = Basket.objects.filter(user=user_id).first()
#         product = Product.objects.get(id=product_id)
#
#         basket_item, created = BasketItem.objects.get_or_create(basket=basket, product=product)
#         basket_item.quantity += int(quantity)
#         basket_item.save()
#
#         serializer = BasketSerializer(basket)
#         return Response(serializer.data)
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
#
#     def patch(self, request):
#         user = request.user
#         product_id = request.data.get('product_id')[0]
#         quantity = int(request.data.get('quantity'))
#
#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             return Response({'message': 'Product not found'}, status=404)
#
#         # basket = Basket.objects.filter(user=request.user).first()
#         basket = Basket.objects.get(user=user)
#
#         try:
#             basket_item = BasketItem.objects.get(basket=basket, product=product)
#         except ObjectDoesNotExist:
#             return Response({'message': 'Product not in basket'}, status=404)
#
#         if basket_item.quantity == quantity:
#             basket_item.delete()
#         elif basket_item.quantity > quantity:
#             basket_item.quantity -= quantity
#             basket_item.save()
#         else:
#             return Response({'message': 'Quantity more than in basket. Try again'}, status=404)
#
#         serializer = BasketSerializer(basket)
#         return Response(serializer.data)


# class ProductsPopularCatalogList(ListModelMixin, GenericAPIView):
#     """Представление для получения списка популярных продуктов"""
#     serializer_class = ProductShortSerializer
#     permission_classes = (AllowAny,)
#     queryset = Product.objects.order_by('sold_amount')[:8]
#
#     def get(self, request):
#         return self.list(request)


# def get(self, request, *args, **kwargs):
    #     queryset = Product.objects.filter(~Q(sale_price__exact=0))
    #
    #     page_number = request.query_params.get('currentPage') # number
    #
    #     paginator = CatalogPagination()
    #     # paginator.page.number = page_number
    #     result_page = paginator.paginate_queryset(queryset, request)
    #     serializer = SaleSerializer(result_page, many=True)
    #
    #     # serializer = SaleSerializer(queryset, many=True)
    #     page = paginator.paginate_queryset(serializer.data, request)
    #
    #     return paginator.get_paginated_response(page)
    #     # return Response(serializer.data, status=status.HTTP_200_OK)
    #     # return paginator.get_paginated_response(paginator, serializer.data)





