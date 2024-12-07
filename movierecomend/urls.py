"""movierecomend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from movie import ajax_views as views
# 用于前后端连接
urlpatterns = [
    path("", include("index.urls")),
    path("admin/", admin.site.urls),
    path("api/", include([
        path("login/", views.login, name="login"),
        path("register/", views.register, name="register"),
        path("user/", views.get_user, name="get_user"),
        path("recent_movies/", views.recent_movies),
        path("movies/", views.movies),
        path("search_movies/", views.search_movies),
        path("user_recommend/", views.user_recommend,
             name="user_recommend"),  # 用户推荐
        path("all_tags/", views.all_tags, name="all_tags"),
        path("movie/<int:movie_id>/", views.movie, name="movie"),
        path("item_recommend/", views.item_recommend,
             name="item_recommend"),  # 物品推荐
        path("score/<int:movie_id>/", views.score, name="score"),
        path("collect/<int:movie_id>/", views.collect, name="collect"),
        path("decollect/<int:movie_id>/", views.decollect, name="decollect"),
        path("comment/<int:movie_id>/", views.make_comment, name="comment"),
        path("personal/", views.personal),
        path("mycollect/", views.mycollect, name="mycollect"),
        path("my_comments/", views.my_comments, name="my_comments"),
        path("my_rate/", views.my_rate, name="my_rate"),
        path("delete_comment/<int:comment_id>",
             views.delete_comment, name="delete_comment"),
        path("delete_rate/<int:rate_id>", views.delete_rate, name="delete_rate"),
        path('choose_tags/', views.choose_tags)
    ])),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)

admin.site.site_header = '推荐系统后台管理'
admin.site.index_title = '首页-推荐系统'
admin.site.site_title = '推荐系统'
