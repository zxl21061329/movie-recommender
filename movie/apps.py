from django.apps import AppConfig

#定义了一个Django应用的配置类 MovieConfig，继承自 AppConfig。它设置了应用的名称为 movie，并在管理界面中显示为“电影数据管理”。
class MovieConfig(AppConfig):
    name = 'movie'
    verbose_name = "电影数据管理"