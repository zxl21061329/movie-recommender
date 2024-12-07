from django.apps import apps
from django.contrib import admin
from .models import Movie
from django.db.models import ManyToOneRel, ForeignKey, OneToOneField
from django.utils.html import format_html


class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        self.list_select_related = [x.name for x in model._meta.fields if isinstance(
            x, (ManyToOneRel, ForeignKey, OneToOneField,))]

        # self.search_fields=[model.p]
        super(ListAdminMixin, self).__init__(model, admin_site)


class MovieAdmin(admin.ModelAdmin):
    # tags = models.ManyToManyField(Tags, verbose_name='标签', blank=True)#多对多关系
    # collect = models.ManyToManyField(User, verbose_name="收藏者", blank=True)
    # name = models.CharField(verbose_name="电影名称", max_length=255, unique=True)
    # director = models.CharField(verbose_name="导演名称", max_length=255)
    # country = models.CharField(verbose_name="国家", max_length=255)
    # years = models.DateField(verbose_name='上映日期')
    # leader = models.CharField(verbose_name="主演", max_length=1024)
    # d_rate_nums = models.IntegerField(verbose_name="豆瓣评价数")
    # d_rate = models.CharField(verbose_name="豆瓣评分", max_length=255)
    # intro = models.TextField(verbose_name="描述")
    # num = models.IntegerField(verbose_name="浏览量", default=0)
    # origin_image_link = models.URLField(verbose_name='豆瓣图片地址', max_length=255, null=True)
    # image_link = models.FileField(verbose_name="封面图片", max_length=255, upload_to='movie_cover')
    # imdb_link = models.URLField(null=True)
    list_display = [
        #    'tags',
        #    'collect',
        'image',
        'name',
        'director',
        'country',
        'years',
        'leader',
        'd_rate_nums',
        'd_rate',
        # 'intro',
        #    'num',
        #    'origin_image_link',
        # 'image_link',
        # 'imdb_link',
    ]
    list_display_links = ("image", "name",)
    list_filter = ('director', 'years', 'country',)
    list_select_related = True
    list_per_page = 20
    list_max_show_all = 200
    list_editable = ()
    search_fields = [
        'name',
        'director',
        'intro',
        'leader',
    ]
    date_hierarchy = None
    save_as = False
    save_as_continue = True
    save_on_top = False
    preserve_filters = True
    inlines = []

    def image(self, obj):
        return format_html('<img src="{cover}" width=150 height=150>', cover=obj.image_link.url)
    image.short_description = '封面'


admin.site.register(Movie, MovieAdmin)

models = apps.get_models()
for model in models:
    admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
    try:
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass
