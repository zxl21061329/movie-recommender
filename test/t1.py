import pandas as pd
import numpy as np
from collections import defaultdict

# 读取数据
movies = pd.read_csv('movies.csv')  # 电影数据
ratings = pd.read_csv('ratings.csv')  # 评分数据

# 将电影类型（genres）拆分为标签列表
movies['genres'] = movies['genres'].apply(lambda x: x.split('|'))

# 创建电影-标签的映射关系
movie_tags = defaultdict(list)
for _, row in movies.iterrows():
    movie_id = row['movieId']
    tags = row['genres']
    movie_tags[movie_id] = tags

# 创建用户-标签偏好度字典
user_tag_prefs = defaultdict(lambda: defaultdict(float))

# 计算每个用户的平均评分
user_avg_ratings = ratings.groupby('userId')['rating'].mean().to_dict()

# 遍历评分数据，计算用户对标签的偏好度
for _, row in ratings.iterrows():
    user_id = row['userId']
    movie_id = row['movieId']
    rating = row['rating']
    timestamp = row['timestamp']  # 如果需要时间衰减，可以在这里使用

    # 获取当前电影的所有标签
    tags = movie_tags[movie_id]

    # 计算用户对每个标签的偏好度贡献
    delta = rating - user_avg_ratings[user_id]  # 评分偏差
    for tag in tags:
        user_tag_prefs[user_id][tag] += delta

# 归一化用户对标签的偏好度
for user_id in user_tag_prefs:
    total_weight = sum(abs(val) for val in user_tag_prefs[user_id].values())
    if total_weight > 0:
        for tag in user_tag_prefs[user_id]:
            user_tag_prefs[user_id][tag] /= total_weight

# 将结果转换为DataFrame
user_tag_prefs_list = []
for user_id, tag_weights in user_tag_prefs.items():
    for tag, weight in tag_weights.items():
        user_tag_prefs_list.append({
            'userId': user_id,
            'tag': tag,
            'preference': weight
        })

user_tag_prefs_df = pd.DataFrame(user_tag_prefs_list)

# 保存结果到CSV文件
user_tag_prefs_df.to_csv('user_tag_preferences.csv', index=False)

# 打印结果
print(user_tag_prefs_df.head())