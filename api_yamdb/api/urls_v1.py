from rest_framework.routers import DefaultRouter

from . import views

v1 = DefaultRouter()
v1.register('titles', views.TitleViewSet, basename='title')
v1.register('categories', views.CategoryViewSet, basename='category')
v1.register('genres', views.GenreViewSet, basename='genre')
v1.register('users', views.UserViewSet, basename='users')
v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewViewSet,
    basename='reviews'
)
v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet,
    basename='comments'
)
