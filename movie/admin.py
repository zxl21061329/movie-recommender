from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.sessions.models import Session
from .models import Movie, MovieList, MovieListMovies
from .forms import MovieListMoviesForm
from django.db.models import ManyToOneRel, ForeignKey, OneToOneField
from django.utils.html import format_html
from django import forms
from django.urls import reverse
from django.utils.html import format_html

# 取消注册 Django 默认的组、权限和会话（先检查是否已注册）
for model in [Group, Permission, Session]:
    if model in admin.site._registry:  # 先检查是否已注册
        admin.site.unregister(model)

class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        self.list_select_related = [x.name for x in model._meta.fields if isinstance(
            x, (ManyToOneRel, ForeignKey, OneToOneField,))]

        super(ListAdminMixin, self).__init__(model, admin_site)

class MovieListMoviesForm(forms.ModelForm):
    class Meta:
        model = MovieListMovies
        fields = '__all__'  # 使用所有字段，但我们可以在下面排除电影名称字段
class MovieListMoviesInline(admin.TabularInline):
    model = MovieListMovies
    form = MovieListMoviesForm
    extra = 1
    fields = ('movie',)  # 只显示电影的下拉框


class MovieListAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'description', 'edit_button')  # 添加 edit_button 列
    search_fields = ('name',)
    inlines = [MovieListMoviesInline]

    def edit_button(self, obj):
        # 生成编辑按钮链接，跳转到编辑页面
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name),  # 获取当前模型的编辑链接
                      args=[obj.pk])  # 使用对象的 primary key
        return format_html('<a class="button" style="background-color: #ADD8E6; color: white; padding: 4px 8px; font-size: 12px; border-radius: 4px; text-decoration: none;" href="{}">编辑</a>', url)

    edit_button.short_description = '操作'
    edit_button.allow_tags = True


class MovieAdmin(admin.ModelAdmin):
    list_display = [
        'image',
        'name',
        'director',
        'country',
        'years',
        'leader',
        'd_rate_nums',
        'd_rate',
    ]
    list_display_links = ("image", "name",)
    list_filter = ('director', 'years', 'country',)
    list_select_related = True
    list_per_page = 20
    list_max_show_all = 200
    search_fields = ['name', 'director', 'intro', 'leader']

    def image(self, obj):
        return format_html('<img src="{cover}" width=150 height=150>', cover=obj.image_link.url)
    image.short_description = '封面'

# 只注册一次 Movie 模型
admin.site.register(Movie, MovieAdmin)
admin.site.register(MovieList, MovieListAdmin)

class MovieListMoviesAdmin(admin.ModelAdmin):
    form = MovieListMoviesForm

admin.site.register(MovieListMovies, MovieListMoviesAdmin)


# 只注册非 Django 默认模型
models = apps.get_models()
exclude_models = {Group, Permission, Session}  # 排除模型

for model in models:
    if model not in exclude_models and model not in admin.site._registry:
        admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
        admin.site.register(model, admin_class)
