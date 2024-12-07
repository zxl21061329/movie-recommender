# 引用库
import django
import os
import re
import time
import json
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movierecomend.settings")

django.setup()

count = 0
# 设置headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36', 'referer': 'https://www.bilibili.com/'}

u = 'https://v.baidu.com/commonapi/movie2level/?filter=false&type=&area=&actor=&start=&complete=&order=hot&pn={}&rating=&prop=&channel=movie'
# 设置url
urls = set(u.format(str(i)) for i in range(1, 50))     #设置1-100
# urls = set(u.format(str(i)) for i in range(1, 31))
page_count = 0


class AttrDict(dict):
    def __getattr__(self, key):
        return self.__getitem__(key)


def get_fields(d: dict, *keys: str):
    return AttrDict({k: v for k, v in d.items() if k in keys})


def get_url_movie():
    global page_count
    while urls:
        url = urls.pop()
        page_count += 1
        print('fetch url', page_count)
        response = requests.get(url, headers=headers)
        data = response.json()['videoshow']['videos']
        for d in data:
            get_info_movie(d)
        time.sleep(2)


def get_info_movie(item: AttrDict):
    from movie.models import Movie, Tags
    global count
    count += 1
    data = AttrDict(item)

    name = data.title
    tags = [i['name'] for i in data.type]
    director = ', '.join([i['name'] for i in data.director])
    country = data.area[0]['name']
    years = data.date + '-01-01'
    leader = ', '.join([i['name'] for i in data.actor])
    d_rate_nums = 0
    d_rate = str(float(data.rating)/10)
    num = 0
    origin_image_link = data.imgh_url
    intro = data.intro
    imdb_link = data.url
    try:
        image_link = save_images(origin_image_link, str(data.id))
    except Exception as e:
        print(origin_image_link,e)
        return
    print(name, director, country)
    # print(dict(
    #     id=data.id,
    #     name=name,
    #     director=director,
    #     country=country,
    #     years=years,
    #     leader=leader,
    #     d_rate_nums=d_rate_nums,
    #     d_rate=d_rate,
    #     num=num,
    #     origin_image_link=origin_image_link,
    #     image_link=image_link,
    #     intro=intro,
    #     imdb_link=imdb_link
    # ), end="\n"*2)
    film, created = Movie.objects.get_or_create(
        name=name, defaults=dict(
            id=data.id,
            director=director,
            country=country,
            years=years,
            leader=leader,
            d_rate_nums=d_rate_nums,
            d_rate=d_rate,
            num=num,
            origin_image_link=origin_image_link,
            image_link=image_link,
            intro=intro,
            imdb_link=imdb_link
        )
    )
    if created:
        print("插入电影成功！")
    else:
        print('movie exists')
    for tag in tags:
        tags, created = Tags.objects.get_or_create(name=tag)
        if created:
            print('tag create success', created)
        film.tags.add(tags)


def save_images(link, name):
    res = requests.get(url=link, headers=headers)
    if res.status_code != 200:
        raise IOError("code not 200")
    image_name = 'media/movie_cover/' + name + '.png'
    if not os.path.exists(image_name):
        with open(image_name, 'wb') as opener:
            opener.write(res.content)
    return image_name.replace('media/', '')
    # print('image success', image_name)

if __name__ == '__main__':
    get_url_movie()
