import json
import random
from functools import wraps

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer

from movie_it.cache_keys import USER_CACHE, ITEM_CACHE
from movie_it.recommend_movies import recommend_by_user_id, recommend_by_item_id
from .forms import *
from index.utils import success, error


def movies_paginator(movies, page):
    paginator = Paginator(movies, 12)
    if page is None:
        page = 1
    movies = paginator.page(page)
    return movies


def to_dict(l):
    def _todict(obj):
        j = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        return j

    return [_todict(i) for i in l]


# from django.urls import HT
# json response
class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs["content_type"] = "application/json;"
        super(JSONResponse, self).__init__(content, **kwargs)

def choose_tags(request):
    data = request.json
    print(data)
    tags_name = data.get("tags_name")
    for tag_name in tags_name:
        tag = Tags.objects.filter(name=tag_name.strip()).first()
        UserTagPrefer.objects.create(tag_id=tag.id, user_id=request.user_.id, score=5)
    return success()

def login(request):
    # 登录功能
    data = request.json
    username = data.get('username')
    password = data.get('password')
    result = User.objects.filter(username=username)
    if result:
        user = User.objects.get(username=username)
        if user.password == password:
            return success(data=user.id)
        else:
            return error('密码错误')
    return error('账号不存在')


def get_user(request):
    id_ = request.headers.get("access-token")
    user = User.objects.filter(id=id_).first()
    if user:
        return success(
            data={"name": user.username, "role": [],
                  "isSuperuser": True}
        )
    return error()


def register(request):
    # 注册功能
    data = request.json
    if not all((data.get("username"), data.get("password1"), data.get("password2"))):
        return error("信息不全")
    if data.get("password1") != data.get("password2"):
        return error("二次密码不一致")
    if User.objects.filter(username=data.get("username")).exists():
        return error("帐号已存在")
    user = User.objects.create(
        username=data.get("username"),
        password=data.get("password1"),
        email=data.get("email"))
    # 注册新用户
    return success(data=user.id)


def login_in(func):  # 验证用户是否登录
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[0]
        is_login = request.session.get("login_in")
        if is_login:
            return func(*args, **kwargs)
        else:
            return redirect(reverse("login"))

    return wrapper


def recent_movies(request):
    new_list = Movie.objects.order_by('?')[:8]
    return success(to_dict(new_list))


def user_recommend(request):
    # 基于用户推荐
    # cache_key = USER_CACHE.format(user_id=user_id)
    user_id = request.user_.id
    if user_id is None:
        movie_list = Movie.objects.order_by('?')
    else:
        cache_key = USER_CACHE.format(user_id=user_id)
        movie_list = cache.get(cache_key)
        # TODO 不要缓存
        # if movie_list is None:
        movie_list = recommend_by_user_id(user_id)
        cache.set(cache_key, movie_list, 60 * 5)
        print('设置缓存')
        # else:
        #     print('缓存命中!')

    json_movies = to_dict(movie_list)
    random.shuffle(json_movies)
    return success(json_movies[:3])


def item_recommend(request):
    # 基于物品推荐
    user_id = request.user_.id
    if user_id is None:
        movie_list = Movie.objects.order_by('?')
    else:
        cache_key = ITEM_CACHE.format(user_id=user_id)
        movie_list = cache.get(cache_key)
        # if movie_list is None:
        movie_list = recommend_by_item_id(user_id)
        cache.set(cache_key, movie_list, 60 * 5)
        print('设置缓存')
        # else:
        #     print('缓存命中!')
    json_movies = to_dict(movie_list)
    random.shuffle(json_movies)
    return success(json_movies[:3])


def movies(request):
    data = request.json
    pagesize = data.get('pagesize', 8)
    page = data.get('page', 1)
    order = data.get('order', 'num')
    tag = data.get('tag')
    if order == 'collect':
        movies = Movie.objects.annotate(
            collectors=Count('collect')).order_by('-collectors')
        title = '收藏排序'
    elif order == 'rate':
        movies = Movie.objects.all().annotate(marks=Avg('rate__mark')).order_by('-marks')
        title = '评分排序'
    elif order == 'years':
        movies = Movie.objects.order_by('-years')
        title = '时间排序'
    else:
        movies = Movie.objects.order_by('-id')
        title = '热度排序'
    if tag:
        movies = movies.filter(tags__id=tag)
    pg = Paginator(movies, pagesize)
    page = pg.page(page)
    return success({
        'total': pg.count,
        'results': to_dict(page.object_list)
    })


def search_movies(request):
    data = request.json
    pagesize = data.get('pagesize', 5)
    page = data.get('page', 1)
    keyword = data.get('keyword', '')
    q = Q(name__icontains=keyword) | Q(
        director__icontains=keyword) | Q(leader__icontains=keyword)
    movies = Movie.objects.filter(q).order_by('name')
    pg = Paginator(movies, pagesize)
    page = pg.page(page)
    return success(to_dict(page.object_list))


def movie(request, movie_id):
    # 电影详情
    movie = Movie.objects.get(pk=movie_id)
    movie.num += 1
    movie.save()
    result = to_dict([movie])[0]
    result['collect_count'] = movie.collect.count()
    result['image_link'] = str(result['image_link'])
    result['all_tags'] = to_dict(movie.tags.all())
    comments = movie.comment_set.order_by("-create_time")
    for i in comments:
        i.userName = i.user.username
    result['comments'] = to_dict(comments)
    user_id = request.user_.id
    movie_rate = Rate.objects.filter(
        movie=movie).all().aggregate(Avg('mark'))  # 电影评分
    if movie_rate:
        movie_rate = movie_rate['mark__avg']
    else:
        movie_rate = 0
    result['movie_rate'] = movie_rate
    if user_id is not None:
        user_rate = Rate.objects.filter(movie=movie, user_id=user_id).first()
        if user_rate:
            result['user_rate'] = to_dict([user_rate])[0]
        else:
            result['user_rate'] = None
        result['user'] = to_dict([request.user_])[0]
        is_collect = movie.collect.filter(id=user_id).first()
        if is_collect:
            result['is_collect'] = to_dict([is_collect])[0]
        else:
            result['is_collect'] = None
    return success(result)


def search(request):  # 搜索
    if request.method == "POST":  # 如果搜索界面
        key = request.POST["search"]
        request.session["search"] = key  # 记录搜索关键词解决跳页问题
    else:
        key = request.session.get("search")  # 得到关键词
    movies = Movie.objects.filter(
        Q(name__icontains=key) | Q(intro__icontains=key) | Q(
            director__icontains=key)
    )  # 进行内容的模糊搜索
    page_num = request.GET.get("page", 1)
    movies = movies_paginator(movies, page_num)
    return render(request, "items.html", {"movies": movies, 'title': '搜索结果'})


def all_tags(request):
    # 所有标签
    tags = Tags.objects.all()
    return success(to_dict(tags))


def score(request, movie_id):
    # 给电影打分 在打分的时候清除缓存
    user_id = request.user_.id
    # user = User.objects.get(id=user_id)
    movie = Movie.objects.get(id=movie_id)
    score = float(request.json.get("score"))
    get, created = Rate.objects.get_or_create(
        user_id=user_id, movie=movie, defaults={"mark": score})
    if created:
        for tag in movie.tags.all():
            prefer, created = UserTagPrefer.objects.get_or_create(
                user_id=user_id, tag=tag, defaults={'score': score})
            if not created:
                # 更新分数
                prefer.score += (score - 3)
                prefer.save()
        print('create data')
        # 清理缓存
        user_cache = USER_CACHE.format(user_id=user_id)
        item_cache = ITEM_CACHE.format(user_id=user_id)
        cache.delete(user_cache)
        cache.delete(item_cache)
        print('cache deleted')
    return success()


def collect(request, movie_id):
    # 收藏电影
    user = request.user_
    movie = Movie.objects.get(id=movie_id)
    movie.collect.add(user)
    movie.save()
    return success()


def decollect(request, movie_id):
    # 取消收藏电影
    user = request.user_
    movie = Movie.objects.get(id=movie_id)
    movie.collect.remove(user)
    # movie.rate_set.count()
    movie.save()
    return success()


def make_comment(request, movie_id):
    # 给电影进行评论
    user = request.user_
    movie = Movie.objects.get(id=movie_id)
    comment = request.json.get("comment")
    Comment.objects.create(user=user, movie=movie, content=comment)
    return success()


def personal(request):
    user = request.user_
    return success(to_dict([user])[0])


def mycollect(request):
    # 我的收藏
    user = request.user_
    movie = user.movie_set.all()
    for i in movie:
        i.all_tags = to_dict(i.tags.all())
    return success(to_dict(movie))


def my_comments(request):
    # 展示我的评论的地方
    user = request.user_
    comments = user.comment_set.all()
    for i in comments:
        i.movie_name = i.movie.name
    return success(to_dict(comments))


def delete_comment(request, comment_id):
    Comment.objects.get(pk=comment_id).delete()
    return success()


def my_rate(request):
    # 我的评分
    user = request.user_
    rate = user.rate_set.all()
    for i in rate:
        i.movie_name = i.movie.name
    return success(to_dict(rate))


def delete_rate(request, rate_id):
    Rate.objects.filter(pk=rate_id).delete()
    return success()

############################################################################################################################################
