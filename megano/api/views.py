from sqlite3 import IntegrityError

from django.contrib.auth.password_validation import validate_password, password_validators_help_texts
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.encoding import force_str
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
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
from django.http import FileResponse
from django.contrib.auth.password_validation import validate_password

from user.serializers import UserSerializer, UserLoginSerializer, AuthUserSerializer, RegisterSerializer, \
    ProfileSerializer, BasketSerializer, BasketItemSerializer, AddBasketItemSerializer, \
    DeleteBasketItemSerializer, PasswordSerializer, CreateProfileSerializer, ChangeAvatarSerializer
from user.models import Profile, Basket, BasketItem
from shop.serializers import ProductShortSerializer, ProductSerializer, CategorySerializer, OrderSerializer, \
    ReviewSerializer, \
    SaleSerializer, PaymentSerializer, OrderItemSerializer, CreateOrderSerializer, TagSerializer, \
    AddOrderItemSerializer, \
    DeleteOrderItemSerializer, UpdateOrderSerializer
from shop.models import Order, Product, Review, Category, Image, Specification, Sale, Subcategory, OrderItem, Payment, \
    Tag
from manage.models import DeliveryType
from .utils import create_user_account, get_and_authenticate_user, IsOwnerOrReadOnly, IsOwner
from .filters import CatalogFilter




class LoginUserView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
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


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


    def post(self, request, *args, **kwargs):
        user = request.user
        username = request.data.get("username")
        email = request.data.get("email")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        password = request.data.get("password")
        password2 = request.data.get("password2")
        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password, user)
        except ValidationError as e:
            Response({'error': f'{e}'},
                     status=status.HTTP_400_BAD_REQUEST)

        if password != password2:
            return Response({'error': 'Password fields did not match.'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        user.set_password(password)
        user.save()

        user = authenticate(username=username, password=password)
        login(request, user)

        return Response({'code': '200', 'user': user.username, 'message': 'successfully sign up'},
                        status=status.HTTP_200_OK)




    # def create(self, request, *args, **kwargs):
    #     response = super().create(request, *args, **kwargs)
    #     return Response({
    #         'status': 200,
    #         'message': 'User successfully created',
    #         'data': response.data
    #     })


class LogoutView(APIView):
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


class CategoryList(ListModelMixin, GenericAPIView):
    """Представление для получения списка категорий с подкатегориями"""
    permission_classes = (AllowAny,)
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get(self, request):
        return self.list(request)


class ProductsCatalogList(ListModelMixin, GenericAPIView):
    """Представление для получения списка продуктов в каталоге"""
    serializer_class = ProductShortSerializer
    queryset = Product.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CatalogFilter

    def get(self, request):
        return self.list(request)


class ProductsPopularCatalogList(ListModelMixin, GenericAPIView):
    """Представление для получения списка популярных продуктов"""
    serializer_class = ProductShortSerializer
    permission_classes = (AllowAny,)
    queryset = Product.objects.order_by('sold_amount')[:8]

    def get(self, request):
        return self.list(request)


class ProductsLimitedCatalogList(ListModelMixin, GenericAPIView):
    """Представление для получения списка лимитированных продуктов"""
    serializer_class = ProductShortSerializer
    permission_classes = (AllowAny,)
    queryset = Product.objects.filter(limited=True).all()

    def get(self, request):
        return self.list(request)


class SalesList(ListModelMixin, GenericAPIView):
    """Представление для получения списка скидок"""
    serializer_class = SaleSerializer
    queryset = Sale.objects.all()
    permission_classes = (AllowAny,)

    def get(self, request):
        return self.list(request)


class BannersList(ListModelMixin, GenericAPIView):
    """Представление для получения списка популярных продуктов"""
    serializer_class = ProductShortSerializer
    permission_classes = (AllowAny,)
    queryset = Product.objects.order_by('sold_amount')[:8]

    def get(self, request):
        return self.list(request)


class BasketDetail(UpdateModelMixin, ListModelMixin, GenericAPIView):
    """Представление для получения корзины, а также добавления и удаления продуктов"""
    permission_classes = (IsAuthenticated, IsOwner)
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        queryset = Basket.objects.all()
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated
        user_id = user.id
        if not user.is_staff:
            queryset = Basket.objects.filter(user=user_id)
        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddBasketItemSerializer
        elif self.request.method == 'PATCH':
            return DeleteBasketItemSerializer
        return BasketSerializer

    def post(self, request):
        user_id = request.user.id
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        print(product_id)

        basket = Basket.objects.filter(user=user_id).first()
        product = Product.objects.get(id=product_id)

        basket_item, created = BasketItem.objects.get_or_create(basket=basket, product=product)
        basket_item.quantity += int(quantity)
        basket_item.save()

        serializer = BasketSerializer(basket)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def patch(self, request):
        user_id = request.user.id
        product_id = request.data.get('product_id')[0]
        quantity = int(request.data.get('quantity'))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'message': 'Product not found'}, status=404)

        basket = Basket.objects.filter(user=user_id).first()

        try:
            basket_item = BasketItem.objects.get(basket=basket, product=product)
        except BasketItem.DoesNotExist:
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
        delivery_adress = request.data.get('delivery_adress')
        promocode = request.data.get('promocode')
        delivery_type = request.data.get('delivery_type')
        payment_type = request.data.get('payment_type')
        del_type = DeliveryType.objects.get(name=delivery_type)

        order = Order.objects.create(user=user, city=city, delivery_adress=delivery_adress, promocode=promocode,
                                     delivery_type=del_type, payment_type=payment_type)
        order.save()

        for product in Product.objects.all():
            if product.name.replace(" ", "_") in request.data.keys():
                product_name_underline = product.name.replace(" ", "_")
                quantity = request.data.get(f'{product_name_underline}')
                if quantity == '':
                    continue
                try:
                    quantity_int = int(quantity)
                except ValueError:
                    return Response({'code': '400', 'message': 'unexpected value for product quantity'},
                                    status=status.HTTP_400_BAD_REQUEST)
                if quantity_int > product.amount:
                    return Response({'code': '400', 'message': f'we have only {product.amount} items of '
                                                               f'{product.name}, but {quantity_int} was given'},
                                    status=status.HTTP_400_BAD_REQUEST)

                order_item = OrderItem.objects.create(order=order, product=product, quantity=quantity_int)
                order_item.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data)


# @extend_schema(methods=['PUT'], exclude=True)
class OrderDetailsView(RetrieveUpdateDestroyAPIView):
    """Представление для получения, подтверждения и удаления заказа"""
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]
    authentication_classes = [SessionAuthentication]

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return UpdateOrderSerializer
        elif self.request.method == "PATCH":
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

        product_id = request.data.get('product').split(':')[1]
        quantity = request.data.get('quantity')

        try:
            quantity_int = int(quantity)
        except ValueError:
            return Response({'code': '400', 'message': 'unexpected value for product quantity'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
            if quantity_int > product.amount:
                return Response({'code': '400', 'message': f'we have only {product.amount} items of '
                                                           f'{product.name}, but {quantity_int} was given'},
                                status=status.HTTP_400_BAD_REQUEST)
            order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
            order_item.quantity += quantity_int
            order_item.save()
        except ObjectDoesNotExist:
            pass

        city = request.data.get('city')
        promocode = request.data.get('promocode')
        delivery_adress = request.data.get('delivery_adress')
        payment_type = request.data.get('payment_type')
        delivery_type = request.data.get('delivery_type')

        del_type = DeliveryType.objects.get(name=delivery_type)

        order.city = city
        order.delivery_adress = delivery_adress
        order.promocode = promocode
        order.payment_type = payment_type
        order.delivery_type = del_type

        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        user_id = request.user.id
        product_id = request.data.get('product_id')[0]
        quantity = int(request.data.get('quantity'))

        try:
            product = Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            return Response({'message': 'Product not found'}, status=404)

        order = Order.objects.filter(user=user_id).first()

        try:
            order_item = OrderItem.objects.get(order=order, product=product)
        except ObjectDoesNotExist:
            return Response({'message': 'Product not in order'}, status=404)

        if order_item.quantity == quantity:
            order_item.delete()
        elif order_item.quantity > quantity:
            order_item.quantity -= quantity
            order_item.save()
        else:
            return Response({'message': 'Quantity more than in order. Try again'}, status=404)

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        return self.destroy(self, request, *args, **kwargs)


class PaymentView(CreateAPIView):
    """Представление для оплаты собственного заказа"""
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        return OrderSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        order_id = request.data.get('order')
        number = request.data.get('number')
        code = request.data.get('code')

        order = Order.objects.get(id=order_id)

        if order.user.id != user.id:
            return Response({'code': '400', 'message': 'order is not yours'}, status=status.HTTP_400_BAD_REQUEST)

        if Payment.objects.get(order=order, paid=True):
            return Response({'code': '400', 'message': 'order is alredy paid'}, status=status.HTTP_400_BAD_REQUEST)

        if int(number) % int(code) == 0:
            paid = True
        else:
            paid = False

        payment = Payment.objects.create(order=order, user=user, number=number, code=code, paid=paid)
        payment.save()

        if paid:
            for item in order.items.all():
                item.product.amount -= item.quantity
                item.product.save()
            return Response({'code': '200', 'order': order_id, 'message': 'successfully paid'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'code': '400', 'message': 'payment is failed'},
                            status=status.HTTP_400_BAD_REQUEST)


class ProfileView(ListCreateAPIView):
    """Представление для получения и создания заказов"""
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
        return Response(serializer.data)

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

            img = request.FILES.get('avatar')
            alt = request.data.get('alt')

            image = Image.objects.create(img=img, alt=alt, object_id=profile.id,
                                         content_type=ContentType.objects.get_for_model(Profile))
            image.save()
            profile.image = image
            profile.save()

            serializer = ProfileSerializer(profile)
            return Response(serializer.data)


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


class UpdateProfileAvatarView(UpdateAPIView):
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

            image = Image.objects.create(img=avatar, alt=alt, object_id=profile.id,
                                         content_type=ContentType.objects.get_for_model(Profile))
            image.save()
            profile.image = image
            profile.save()

        return Response({'code': '200', 'message': 'Avatar updated successfully'}, status=status.HTTP_200_OK)


class TagListView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)


class ProductDetailsView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)


class ReviewView(ListCreateAPIView):
    """Представление для получения и создания заказов"""
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

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)

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

        serializer = ReviewSerializer(review)
        return Response(serializer.data)

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
#             img = request.FILES.get('img')
#             alt = request.data.get('alt')
#             image = Image.objects.create(img=img, alt=alt)
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
