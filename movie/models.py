'''
用户对电影的打分数据，以及对电影的评论模型的建立。
'''
from datetime import date
from itertools import chain

from django.db import models
from django.db.models import Avg
from django.db.models.fields.files import FileField


#数据库表
class User(models.Model):
    username = models.CharField(max_length=255, unique=True, verbose_name="账号")#unique唯一（不重复）
    password = models.CharField(max_length=255, verbose_name="密码")
    email = models.EmailField(verbose_name="邮箱")
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "前台用户"
        verbose_name = "前台用户"

    def __str__(self):
        return self.username


class Tags(models.Model):
    name = models.CharField(max_length=255, verbose_name="标签", unique=True)

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"

    def __str__(self):
        return self.name


class UserTagPrefer(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, verbose_name="用户id",
    )
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE, verbose_name='标签名')
    score = models.FloatField(default=0)

    class Meta:
        verbose_name = "用户偏好"
        verbose_name_plural = "偏好"

    def __str__(self):
        return self.user.username + str(self.score)


class Movie(models.Model):
    tags = models.ManyToManyField(Tags, verbose_name='标签', blank=True)#多对多关系
    collect = models.ManyToManyField(User, verbose_name="收藏者", blank=True)
    name = models.CharField(verbose_name="电影名称", max_length=255, unique=True)
    director = models.CharField(verbose_name="导演名称", max_length=255)
    country = models.CharField(verbose_name="国家", max_length=255)
    years = models.DateField(verbose_name='上映日期')
    leader = models.CharField(verbose_name="主演", max_length=1024)
    d_rate_nums = models.IntegerField(verbose_name="豆瓣评价数")
    d_rate = models.CharField(verbose_name="豆瓣评分", max_length=255)
    intro = models.TextField(verbose_name="描述")
    num = models.IntegerField(verbose_name="浏览量", default=0)
    origin_image_link = models.URLField(verbose_name='豆瓣图片地址', max_length=255, null=True)
    image_link = models.FileField(verbose_name="封面图片", max_length=255, upload_to='movie_cover')
    imdb_link = models.URLField(null=True)

    @property
    def movie_rate(self):
        movie_rate = Rate.objects.filter(movie_id=self.id).aggregate(Avg('mark'))['mark__avg']
        return movie_rate or '无'

    class Meta:
        verbose_name = "电影"
        verbose_name_plural = "电影"

    def __str__(self):
        return self.name

    def to_dict(self, fields=None, exclude=None):
        opts = self._meta
        data = {}
        for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
            if exclude and f.name in exclude:
                continue
            if fields and f.name not in fields:
                continue
            value = f.value_from_object(self)
            if isinstance(value, date):
                value = value.strftime('%Y-%m-%d')
            elif isinstance(f, FileField):
                value = value.url if value else None
            data[f.name] = value
        return data

class MovieList(models.Model):
    name = models.CharField(max_length=255, verbose_name="影单名称")
    description = models.TextField(verbose_name="影单简介", null=True, blank=True)
    image_link = models.FileField(verbose_name="封面图片", max_length=255, upload_to='movie_list', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    # 新增字段，用于表示影单类型，默认值为“精选影单”
    list_type = models.CharField(max_length=255, verbose_name="影单类型", default="精选影单")

    class Meta:
        verbose_name = '影单'  # 单数形式
        verbose_name_plural = '影单列表'  # 复数形式

    def __str__(self):
        return self.name

class MovieListMovies(models.Model):
    movie_list = models.ForeignKey(MovieList, related_name='movies', on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, related_name='movie_lists', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['movie_list', 'movie']
        verbose_name = '影单电影'  # 单数形式
        verbose_name_plural = '影单电影列表'  # 复数形式

    def __str__(self):
        # 可以简化显示，避免过于详细的信息导致重复显示
        return ''
#用户对电影打分数据
class Rate(models.Model):
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, blank=True, null=True, verbose_name="电影id"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, verbose_name="用户id",
    )
    mark = models.FloatField(verbose_name="评分")
    create_time = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)

    @property
    def avg_mark(self):
        average = Rate.objects.all().aggregate(Avg('mark'))['mark__avg']#求平均分
        return average

    class Meta:
        verbose_name = "评分信息"
        verbose_name_plural = verbose_name

#电影评论表
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")#外建关联
    content = models.CharField(max_length=255, verbose_name="内容")
    create_time = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="电影")

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name


class LikeComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, verbose_name='评论')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')

    class Meta:
        verbose_name = "评论点赞"
        verbose_name_plural = verbose_name
class UserTagPreferenceDegree(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE, verbose_name="标签")
    preference_score = models.FloatField(default=0, verbose_name="偏好评分")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")

    class Meta:
        verbose_name = "用户标签偏好度"
        verbose_name_plural = "用户标签偏好度"
        unique_together = ['user', 'tag']

    def __str__(self):
        return f"{self.user.username} - {self.tag.name}: {self.preference_score}"


