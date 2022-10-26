from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title, User


class SignupSerializer(serializers.ModelSerializer):
    """Сериалайзер для регистрации пользователя."""
    class Meta:
        model = User
        fields = ['email', 'username']

    def validate(self, attrs):
        """Проверка на недопустимое имя пользователя 'me'."""
        username = attrs.get('username')

        if username == 'me':
            raise serializers.ValidationError(
                'Запрещенное имя для пользователя'
            )
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ConfirmationSerializer(serializers.Serializer):
    """Сериалайзер для получения токена по confirmation code."""
    username = serializers.CharField(max_length=30)
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Базовый сериалайзер для users."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class UserMeSerializer(serializers.ModelSerializer):
    """"Сериалайзер для эндпонита /me."""
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер для категории."""
    class Meta:
        exclude = ('id',)
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериалайзер для жанра."""
    class Meta:
        exclude = ('id',)
        model = Genre
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериалайзер для произведения (на чтение)."""
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(TitleReadSerializer):
    """Сериалайзер для произведения (на запись)."""
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериалайзер для отзыва."""
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate(self, data):
        """Проверка на то, что отзывов к произведению автор еще не оставлял."""
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    'Можно оставить только один отзыв'
                )
        return data

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    """Сериалайзер для коммента."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
