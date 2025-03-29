import pymysql
import numpy as np

# 连接数据库
mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="123456",
    database="movierecdb"
)

# 获取游标
cursor = mydb.cursor()

# 查询所有用户的评分数据
query = "SELECT user_id, movie_id, mark FROM movie_rate"
cursor.execute(query)
rows = cursor.fetchall()

# 构建用户 - 电影评分矩阵
user_movie_matrix = {}
for row in rows:
    user_id, movie_id, mark = row
    if user_id not in user_movie_matrix:
        user_movie_matrix[user_id] = {}
    user_movie_matrix[user_id][movie_id] = mark


# 定义余弦相似度函数
def cosine_similarity(vec1, vec2):
    common_movies = set(vec1.keys()) & set(vec2.keys())
    if len(common_movies) == 0:
        return 0
    dot_product = sum([vec1[movie] * vec2[movie] for movie in common_movies])
    norm1 = np.sqrt(sum([value ** 2 for value in vec1.values()]))
    norm2 = np.sqrt(sum([value ** 2 for value in vec2.values()]))
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot_product / (norm1 * norm2)


# 计算用户 2 与其他用户的相似度
target_user_id = 2
target_user_ratings = user_movie_matrix.get(target_user_id, {})
similarities = []
for user_id, ratings in user_movie_matrix.items():
    if user_id != target_user_id:
        similarity = cosine_similarity(target_user_ratings, ratings)
        similarities.append((user_id, similarity))

# 按相似度排序并取前 5 个
similarities.sort(key=lambda x: x[1], reverse=True)
top_5_similar_users = similarities[:5]

# 打印结果
print(f"与用户 ID 为 {target_user_id} 最相似的 5 个用户及其相似度：")
for user_id, similarity in top_5_similar_users:
    print(f"用户 ID: {user_id}, 相似度: {similarity}")

# 关闭游标和数据库连接
cursor.close()
mydb.close()
