from sqlite3 import IntegrityError

from django.contrib.auth.password_validation import validate_password, password_validators_help_texts
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.encoding import force_str
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
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

from user.serializers import UserSerializer, UserLoginSerializer, AuthUserSerializer, RegisterSerializer, \
    ProfileSerializer, BasketSerializer, BasketItemSerializer, AddBasketItemSerializer, \
    DeleteBasketItemSerializer, PasswordSerializer, CreateProfileSerializer, ChangeAvatarSerializer
from user.models import Profile, Basket, BasketItem
from shop.serializers import ProductShortSerializer, ProductSerializer, CategorySerializer, OrderSerializer, \
    ReviewSerializer, SaleSerializer, PaymentSerializer, OrderItemSerializer, CreateOrderSerializer, TagSerializer, \
    UpdateOrderSerializer, CreatePaymentSerializer
from shop.models import Product, Order, Image, Specification, Category, Review, OrderItem, Payment, \
    Tag
from shop.pagination import CatalogPagination, CatalogsPagination
from manage.models import DeliveryType
from .utils import create_user_account, get_and_authenticate_user, IsOwnerOrReadOnly, IsOwner
from .filters import CatalogFilter




class LoginUserView(GenericAPIView):
    """Представление для входа в систему"""
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get("login")
        password = request.data.get("password")
        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid Credentials'},
                            status=status.HTTP_404_NOT_FOUND)
        login(request, user)
        return Response({'code': '200', 'user': user.username, 'message': 'successfully login'},
                        status=status.HTTP_200_OK)

class NewLoginView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, format=None):
        data = json.loads(request.body)

        username = data.get('username', None)
        password = data.get('password', None)

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({'code': '200', 'user': username, 'message': 'successfully login'},
                            status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'Unauthorized',
                'message': 'Username/password combination invalid.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class RegisterView(CreateAPIView):
    """Представление для регистрации"""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        username = data.get("username", None)
        name = data.get("name", None)
        password = data.get("password", None)
        user = request.user

        try:
            validate_password(password, user)
        except ValidationError as e:
            Response({'error': f'{e}'},
                     status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create(
            username=username,
            first_name=name
        )
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        login(request, user)

        return Response({'code': '200', 'user': user.username, 'message': 'successfully sign up'},
                        status=status.HTTP_200_OK)


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


# class CategoryList(ListModelMixin, GenericAPIView):
#     """Представление для получения списка категорий"""
#     permission_classes = (AllowAny,)
#     serializer_class = CategorySerializer
#     queryset = Category.objects.all()
#
#     def get(self, request):
#         return self.list(request)


class CategoryList(APIView):
    """Представление для получения списка категорий"""

    def get(self, request, *args, **kwargs):
        queryset = Category.objects.all()
        # data = [CategorySerializer(object) for object in queryset]
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ProductsCatalogList(APIView):
    """Представление для получения списка продуктов в каталоге"""
    serializer_class = ProductShortSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CatalogFilter

    def get(self, request, *args, **kwargs):
        queryset = Product.objects.all()
        serializer = ProductShortSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CatalogView(APIView):
    # pagination_class = CatalogPagination
    def get(self, request):
        ser = json.dumps(request.GET)

        # DEBUGGER INSTEAD OF PRINT

        # print('sers', ser)

        products = Product.objects.all()

        serializer = ProductShortSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def get(self, request):
    #     query_params = QueryDict(request.GET.urlencode())
    #
    #     # Get query parameters
    #     title = query_params.getlist('filter[name]')
    #     min_price = query_params.get('filter[minPrice]')
    #     max_price = query_params.get('filter[maxPrice]')
    #     free_delivery = query_params.get('filter[freeDelivery]')
    #     available = query_params.get('filter[available]')
    #     current_page = query_params.get('filter[currentPage]')
    #
    #     # Filter products
    #     filtered_products = Product.objects.all()
    #
    #     if title != ['']:
    #         new_title = ' '.join(title)
    #         filtered_products = filtered_products.filter(title__icontains=str(new_title))
    #
    #     if min_price:
    #         filtered_products = filtered_products.filter(price__gte=min_price)
    #
    #     if max_price:
    #         filtered_products = filtered_products.filter(price__lte=max_price)
    #
    #     if free_delivery != 'false':
    #         filtered_products = filtered_products.filter(free_delivery=True)
    #         for product in filtered_products:
    #             product.available_product()
    #             product.save()
    #
    #     if free_delivery != 'false':
    #         filtered_products = filtered_products.filter(freeDelivery=True)
    #
    #     if available:
    #         filtered_products = filtered_products.filter(available=True)
    #
    #     paginator = CatalogsPagination()
    #     page = paginator.paginate_queryset(filtered_products, request)
    #
    #     serializer = ProductShortSerializer(page, many=True)
    #     return paginator.get_paginated_response(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_200_OK)



# class ProductsPopularCatalogList(ListModelMixin, GenericAPIView):
#     """Представление для получения списка популярных продуктов"""
#     serializer_class = ProductShortSerializer
#     permission_classes = (AllowAny,)
#     queryset = Product.objects.order_by('sold_amount')[:8]
#
#     def get(self, request):
#         return self.list(request)


class ProductsPopularCatalogList(APIView):
    """Представление для получения списка популярных продуктов"""

    def get(self, request, *args, **kwargs):
        queryset = Product.objects.order_by('sold_amount')[:8]
        serializer = ProductShortSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductsLimitedCatalogList(ListModelMixin, GenericAPIView):
    """Представление для получения списка лимитированных продуктов"""

    def get(self, request, *args, **kwargs):
        queryset = Product.objects.filter(limited=True)[:8]
        serializer = ProductShortSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class SalesList(APIView):

        # PAGINATION_CLASS =

    """Представление для получения списка скидок"""
    def get(self, request, *args, **kwargs):
        queryset = Product.objects.filter(~Q(sale_price__exact=0))
        # serializer = SaleSerializer(queryset, many=True)

        paginator = Paginator(queryset, per_page=1)

        page_from_url = request.query_params.get('currentPage')


        try:
            page = paginator.get_page(page_from_url)
        except PageNotAnInteger:
            page = paginator.get_page(1)
        except EmptyPage:
            page = paginator.get_page(paginator.num_pages)

        ##QUERYSET
        objects = page.object_list

        print('objects', objects)

        serializer = SaleSerializer(objects, many=True)
        # return Response({
        #     'data': serializer.data
        # })

        return Response(serializer.data, status=status.HTTP_200_OK)

# def get(self, request, *args, **kwargs):
    #     # queryset = Product.objects.filter(sale_price__isnull=True)
    #     queryset = Product.objects.filter(~Q(sale_price__exact=0))
    #     print('nur sales', queryset)
    #     serializer = SaleSerializer(queryset, many=True)
    #
    #     paginator = Paginator(queryset, 25, allow_empty_first_page=False)  # Show 25 contacts per page.
    #
    #     page_number = request.GET.get("page")
    #     page_obj = paginator.get_page(page_number)
    #     datan = {"page_obj": page_obj, "data": serializer.data}

    #     return Response(datan, status=status.HTTP_200_OK)


class BannersList(APIView):
    """Представление для получения списка популярных продуктов"""

    def get(self, request, *args, **kwargs):
        queryset = Product.objects.order_by('sold_amount')[:8]
        serializer = ProductShortSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



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


class BasketDetail(APIView):
    """Представление для получения корзины, а также добавления и удаления продуктов"""

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        print(data)
        user = request.user
        product_id = data.get('id', None)
        quantity = data.get('count', None)


        print('product', product_id)
        print('quantity', quantity)

        # basket = Basket.objects.filter(user=user_id).first()
        basket = Basket.objects.get(user=user)

        product = Product.objects.get(id=product_id)

        basket_item, created = BasketItem.objects.get_or_create(basket=basket, product=product)
        basket_item.quantity += int(quantity)
        basket_item.save()

        queryset = BasketItem.objects.filter(basket=basket.id)

        products = Product.objects.filter(basket_items__in=queryset)

        serializer = ProductShortSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request: Request):
        user = request.user
        basket, created = Basket.objects.get_or_create(user=user)
        queryset = BasketItem.objects.filter(basket=basket.id)

        products = Product.objects.filter(basket_items__in=queryset)

        serializer = ProductShortSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def patch(self, request: Request):
        user = request.user
        product_id = request.data.get('product_id')[0]
        quantity = int(request.data.get('quantity'))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'message': 'Product not found'}, status=404)

        # basket = Basket.objects.filter(user=request.user).first()
        basket = Basket.objects.get(user=user)

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

        serializer = BasketSerializer(basket)
        return Response(serializer.data)


class OrdersList(ListCreateAPIView):
    """Представление для получения и создания заказов"""
    permission_classes = (IsAuthenticated, IsOwner)
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        queryset = Order.objects.all()
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated
        if self.request.method == 'GET':
            user_id = user.id
            if not user.is_staff:
                queryset = Order.objects.filter(user=user_id)
        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        return OrderSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = request.user

        city = request.data.get('city')
        address = request.data.get('address')
        promocode = request.data.get('promocode')
        delivery_type = request.data.get('delivery_type')
        payment_type = request.data.get('payment_type')
        del_type = DeliveryType.objects.get(name=delivery_type)

        order = Order.objects.create(user=user, city=city, address=address, promocode=promocode,
                                     delivery_type=del_type, payment_type=payment_type)
        order.save()

        for product in Product.objects.all():
            if product.title.replace(" ", "_") in request.data.keys():
                product_title_underline = product.title.replace(" ", "_")
                quantity = request.data.get(f'{product_title_underline}')
                if quantity == '':
                    continue
                try:
                    quantity_int = int(quantity)
                except ValueError:
                    return Response({'code': '400', 'message': 'unexpected value for product quantity'},
                                    status=status.HTTP_400_BAD_REQUEST)
                if quantity_int > product.count:
                    return Response({'code': '400', 'message': f'we have only {product.count} items of '
                                                               f'{product.title}, but {quantity_int} was given'},
                                    status=status.HTTP_400_BAD_REQUEST)

                order_item = OrderItem.objects.create(order=order, product=product, quantity=quantity_int)
                order_item.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data)


# @extend_schema(methods=['PUT'], exclude=True)
class OrderDetailsView(RetrieveUpdateDestroyAPIView):
    """Представление для получения, изменения и удаления заказа"""
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]
    authentication_classes = [SessionAuthentication]

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return UpdateOrderSerializer
        return OrderSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        user_id = request.user.id
        id = self.kwargs['pk']

        try:
            order = Order.objects.get(user=user_id, id=id)
        except ObjectDoesNotExist:
            return Response({'message': 'Order with this pk is not exist or order is not yours'}, status=404)



        product_id = request.data.get('add_product').split(':')[1]
        quantity = request.data.get('quantity_of_product_to_add')

        try:
            quantity_int = int(quantity)
        except ValueError:
            return Response({'code': '400', 'message': 'unexpected value for product quantity'},
                            status=status.HTTP_400_BAD_REQUEST)

        if quantity_int == 0:
            pass
        else:
            product = Product.objects.get(id=product_id)
            if quantity_int > product.count:
                return Response({'code': '400', 'message': f'we have only {product.count} items of '
                                                           f'{product.title}, but {quantity_int} was given. Try again'},
                                status=status.HTTP_400_BAD_REQUEST)
            order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
            order_item.quantity += quantity_int
            order_item.save()

        delete_product_id = request.data.get('delete_product').split(':')[1]
        delete_quantity = request.data.get('quantity_of_product_to_delete')

        try:
            delete_quantity_int = int(delete_quantity)
        except ValueError:
            return Response({'code': '400', 'message': 'unexpected value for product quantity'},
                            status=status.HTTP_400_BAD_REQUEST)

        if delete_quantity_int == 0:
            pass
        else:
            order_item = OrderItem.objects.get(product=Product.objects.get(id=delete_product_id), order=order)
            if delete_quantity_int > order_item.quantity:
                return Response({'code': '400', 'message': f'we have only {order_item.quantity} items of '
                                                           f'{order_item.product.title}, but '
                                                           f'{delete_quantity_int} was given. Try again'},
                                status=status.HTTP_400_BAD_REQUEST)
            elif delete_quantity_int == order_item.quantity:
                order_item.delete()
            else:
                order_item.quantity -= delete_quantity_int
                order_item.save()



        city = request.data.get('city')
        promocode = request.data.get('promocode')
        address = request.data.get('address')
        payment_type = request.data.get('payment_type')
        delivery_type = request.data.get('delivery_type')

        del_type = DeliveryType.objects.get(name=delivery_type)

        order.city = city
        order.address = address
        order.promocode = promocode
        order.payment_type = payment_type
        order.delivery_type = del_type

        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data)


    # def delete(self, request, *args, **kwargs):
    #     return self.destroy(self, request, *args, **kwargs)


class PaymentView(CreateAPIView):
    """Представление для оплаты заказа"""
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreatePaymentSerializer
        return PaymentSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        order_id = request.data.get('order')
        number = request.data.get('number')
        code = request.data.get('code')
        print(order_id)
        order = Order.objects.get(id=order_id)
        print(order)

        if order.user.id != user.id:
            return Response({'code': '400', 'message': 'order is not yours'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            Payment.objects.get(order=order, paid=True)
            return Response({'code': '400', 'message': 'order is alredy paid'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            pass

        if int(number) % int(code) == 0:
            paid = True
        else:
            paid = False

        payment = Payment.objects.create(order=order, user=user, number=number, code=code, paid=paid)
        payment.save()

        serializer = PaymentSerializer(payment)

        if paid:
            for item in order.items.all():
                item.product.count -= item.quantity
                item.product.sold_amount += item.quantity
                item.product.save()
            return Response({'code': '200', 'order': order_id, 'message': 'successfully paid', 'data': serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({'code': '400', 'message': 'payment is failed'},
                            status=status.HTTP_400_BAD_REQUEST)


class ProfileView(ListCreateAPIView):
    """Представление для получения и создания профиля"""
    queryset = Profile.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [SessionAuthentication]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateProfileSerializer
        return ProfileSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            return Response({'code': '400', 'message': 'No such profile. Create profile below'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user

        try:
            Profile.objects.get(user=user)
            return Response({'code': '400', 'message': 'profile already exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:

            phone = request.data.get('phone')
            with transaction.atomic():
                profile = Profile.objects.create(user=user, phone=phone)
            profile.save()

            src = request.FILES.get('avatar')
            alt = request.data.get('alt')

            image = Image.objects.create(src=src, alt=alt, object_id=profile.id,
                                         content_type=ContentType.objects.get_for_model(Profile))
            image.save()
            profile.image = image
            profile.save()

            serializer = ProfileSerializer(profile)
            return Response(serializer.data)


class ProfileDetail(APIView):
    """Представление для получения и создания профиля"""

    def get(self, request, *args, **kwargs):
        user = request.user
        print(request.body)
        try:
            profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            return Response({'code': '400', 'message': 'No such profile. Create profile below'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = ProfileSerializer(profile, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        print(request.body)
        data = json.loads(request.body)
        # full_name = data.get("full_name", None)
        full_name = data["fullName"]
        email = data.get("email", None)
        phone = data.get("phone", None)

        profile, created = Profile.objects.get_or_create(user=user)

        src = data.get("avatar", None)
        if src:
            image = Image.objects.create(src=src[0], alt=src[1], object_id=profile.id,
                                         content_type=ContentType.objects.get_for_model(Profile))
            image.save()
            profile.image = image

        profile.full_name = full_name
        profile.email = email
        profile.phone = phone
        profile.save()

        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(UpdateAPIView):
    """ Представление для изменения пароля """
    serializer_class = PasswordSerializer
    model = User
    permission_classes = (IsAuthenticated, IsOwner)
    authentication_classes = [SessionAuthentication]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({'code': '400', 'message': 'Wrong old password'},
                                status=status.HTTP_400_BAD_REQUEST)

            new_password = serializer.data.get("new_password")
            new_password_repeat = serializer.data.get("new_password_repeat")

            if not validate_password(new_password):
                message = ''
                for text in password_validators_help_texts(validate_password(new_password)):
                    message += text
                return Response({'code': '400', 'message': 'Password is not validate', 'help_text': message},
                                status=status.HTTP_400_BAD_REQUEST)

            if new_password != new_password_repeat:
                return Response({'code': '400', 'message': 'New password and new password repeat must be the same'},
                                status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()

            return Response({'code': '200', 'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
        return Response({'code': '400'}, status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(APIView):
    """ Представление для изменения пароля """

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data = json.loads(request.body)
        password_current = data.get("old_password", None)
        password = data.get("new_password", None)
        password_reply = data.get("password_reply", None)

        if not user.check_password(password_current):
            return Response({'code': '400', 'message': 'Wrong old password'},
                            status=status.HTTP_400_BAD_REQUEST)

        if password != password_reply:
            return Response({'code': '400', 'message': 'New password and new password repeat must be the same'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not validate_password(password):
            message = ''
            for text in password_validators_help_texts(validate_password(password)):
                message += text
            return Response({'code': '400', 'message': 'Password is not validate', 'help_text': message},
                            status=status.HTTP_400_BAD_REQUEST)


        user.set_password(password)
        user.save()

        return Response({'code': '200', 'message': 'Password updated successfully'}, status=status.HTTP_200_OK)


class UpdateProfileAvatarView(UpdateAPIView):
    """Представление для обновления аватара в профиле"""
    queryset = Profile.objects.all()
    serializer_class = ChangeAvatarSerializer
    permission_classes = (IsAuthenticated, IsOwner)
    authentication_classes = [SessionAuthentication]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response({'code': '400', 'message': 'You do not have profile. Create profile first'},
                            status=status.HTTP_400_BAD_REQUEST)

        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if profile.avatar:
                Image.objects.get(object_id=profile.id,
                                  content_type=ContentType.objects.get_for_model(Profile)).delete()

            avatar = request.FILES.get('avatar')
            alt = serializer.data.get("alt")

            image = Image.objects.create(src=avatar, alt=alt, object_id=profile.id,
                                         content_type=ContentType.objects.get_for_model(Profile))
            image.save()
            profile.image = image
            profile.save()

        return Response({'code': '200', 'message': 'Avatar updated successfully'}, status=status.HTTP_200_OK)


class UpdateProfileAvatar(APIView):
    """Представление для обновления аватара в профиле"""

    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response({'code': '400', 'message': 'You do not have profile. Create profile first'},
                            status=status.HTTP_400_BAD_REQUEST)

        # if profile.avatar:
        #     Image.objects.get(object_id=profile.id,
        #                       content_type=ContentType.objects.get_for_model(Profile)).delete()
        src = request.FILES.get('avatar')
        # data = json.loads(request.body)
        print('imageeeeeeeeeeeeeeeeeeeeeeeee', src)

        # src = data["avatar"]

        image = Image.objects.create(src=src, alt=user.username, object_id=profile.id,
                                     content_type=ContentType.objects.get_for_model(Profile))
        image.save()
        profile.image = image
        profile.save()

        return Response({'code': '200', 'message': 'Avatar updated successfully'}, status=status.HTTP_200_OK)


class TagListView(ListAPIView):
    """Представление для получения списка тэгов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class ProductDetailsView(RetrieveAPIView):
    """Представление для получения детального описания продукта"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)


class ReviewView(CreateAPIView):
    """Представление для получения и создания отзывов"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        queryset = Review.objects.filter(product_id=self.kwargs['pk'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"product_id": self.kwargs['pk']})
        return context

    # def get(self, request, *args, **kwargs):
    #     return self.list(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        rate = request.data.get('rate')
        if int(rate) < 1 or int(rate) > 5:
            return Response({'code': '400', 'message': 'Rate must be from 1 to 5'},
                            status=status.HTTP_400_BAD_REQUEST)

        product_id = self.kwargs['pk']
        try:
            product = Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            return Response({'code': '400', 'message': 'Product with this id does not exist'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        text = request.data.get('text')

        review = Review.objects.create(product=product, author=user, text=text, rate=rate)
        # product.save()

        serializer = ReviewSerializer(review)
        return Response(serializer.data)

# СПИЗЖЕНО
# class AddReviewView(APIView):
#     def post(self, request: Request, pk=None, *args, **kwargs) -> Response:
#         results = None
#         new_dict = json.loads(request.body.decode('utf-8'))
#         if not request.user.is_authenticated:
#             return Response(data="Please login to leave reviews", status=403)                   REDIRECT??
#         author = new_dict["author"]
#         email = new_dict["email"]
#         text = new_dict["text"]
#         rate = new_dict["rate"]
#         date = datetime.datetime.now()
#         review = Review.objects.create(author=author, email=email, text=text, rate=rate, date=date)
#         review.save()
#         id = pk or request.query_params.get('id')
#         product = Product.objects.get(pk=id)
#         product.reviews.add(review)
#         product.save()
#         reviews = ReviewsSerializer(product.reviews)
#         results = reviews.data
#         return Response(data=results, status=200)

# class ProfileViewSet(ModelViewSet):
#     """Представление для получения и добавления профиля, а также изменения пароля и аватара"""
#
#     queryset = Profile.objects.all()
#
#     def get_serializer_class(self):
#         if self.request.method == 'POST':
#             return CreateProfileSerializer
#         else:
#             return ProfileSerializer
#
#     @action(methods=['get'], detail=True, permission_classes=[IsAuthenticated])
#     def get_profile(self, request, pk=None):
#         user = request.user
#         try:
#             profile = Profile.objects.get(user=user)
#         except Profile.DoesNotExist:
#             return Response({'code': '400', 'message': 'no such profile'}, status=status.HTTP_400_BAD_REQUEST)
#         serializer = ProfileSerializer(profile)
#         return Response(serializer.data)
#
#     @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated])
#     def post_profile(self, request, pk=None):
#
#         user = request.user
#         if not Profile.objects.get(user=user):
#             src = request.FILES.get('src')
#             alt = request.data.get('alt')
#             image = Image.objects.create(src=src, alt=alt)
#             image.save()
#             phone = request.data.get('phone')
#
#             with transaction.atomic():
#                 profile = Profile.objects.create(user=user, avatar=image, phone=phone)
#             profile.save()
#
#             serializer = ProfileSerializer(profile)
#             return Response(serializer.data)
#         else:
#             return Response({'code': '400', 'message': 'profile already exist'}, status=status.HTTP_400_BAD_REQUEST)
