from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import (
    filters, generics, permissions, status, viewsets
)
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api_yamdb.settings import ADMIN_EMAIL

from reviews.models import Category, Genre, Review, Title, User
from .mixins import MixinSet
from .filters import TitleFilter
from .permissions import (
    AdminOrSuperUserOnly,
    IsAdminUserOrReadOnly,
    StaffOrAuthorOrReadOnly
)
from .serializers import (
    CategorySerializer, CommentSerializer, ConfirmationSerializer,
    GenreSerializer, ReviewSerializer, SignupSerializer,
    TitleReadSerializer, TitleWriteSerializer,
    UserMeSerializer, UserSerializer
)


class SignupView(generics.GenericAPIView):
    """Регистрация пользователя через API."""
    serializer_class = SignupSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.validated_data
        user = User.objects.get(email=user_data['email'])
        email_body = f'Confirmation code: {user.confirmation_code}!'
        send_mail(
            'Confirmation code', email_body, ADMIN_EMAIL, (user.email,)
        )
        return Response(user_data, status=status.HTTP_200_OK)


class RefreshTokenView(generics.GenericAPIView):
    """Получение токена через API."""
    serializer_class = ConfirmationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.validated_data
        user = get_object_or_404(User, username=user_data['username'])
        if user.confirmation_code != user_data['confirmation_code']:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {'token': str(user.token)}, status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ModelViewSet):
    """Получение, отправка и изменение данных по API для эндпоинта /users."""
    permission_classes = (AdminOrSuperUserOnly,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=UserMeSerializer
    )
    def me(self, request):
        """Функция для отработки эндопинта /me."""
        self.kwargs['username'] = request.user.username
        if self.request.method == 'PATCH':
            self.partial_update(request)
            request.user.refresh_from_db()
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class TitleViewSet(viewsets.ModelViewSet):
    """Создание, изменение либо получение данных о произведении."""
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all()
    permission_classes = (IsAdminUserOrReadOnly,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return TitleWriteSerializer
        return TitleReadSerializer


class CategoryViewSet(MixinSet):
    """Получение, добавление или изменение категории."""
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']
    lookup_field = 'slug'


class GenreViewSet(MixinSet):
    """Получение списка жанров, добавление или изменение жанра."""
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    """Получение списка отзывов или конкретного отзыва,
    добавление, изменение или удаление."""
    serializer_class = ReviewSerializer
    permission_classes = (StaffOrAuthorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        new_queryset = title.reviews.all()
        return new_queryset

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Получение списка комментов или одного коммента к конкретному отзыву,
    добавление, изменение или удаление коммента."""
    serializer_class = CommentSerializer
    permission_classes = (StaffOrAuthorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'),
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        serializer.save(author=self.request.user, review=review)
