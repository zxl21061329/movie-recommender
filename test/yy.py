import pymysql
import random
from datetime import datetime

# 连接数据库
mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="123456",
    database="movierecdb"
)

try:
    with mydb.cursor() as cursor:
        # 获取所有有标签的电影的 ID
        cursor.execute("SELECT id FROM movie_movie WHERE EXISTS (SELECT 1 FROM movie_movie_tags WHERE movie_movie_tags.movie_id = movie_movie.id)")
        movie_ids = [row[0] for row in cursor.fetchall()]

        # 获取所有用户的 ID
        cursor.execute("SELECT id FROM movie_user")
        user_ids = [row[0] for row in cursor.fetchall()]

        total_combinations = len(movie_ids) * len(user_ids)
        processed = 0
        batch_size = 100  # 每批插入的记录数
        batch = []

        for movie_id in movie_ids:
            for user_id in user_ids:
                processed += 1
                progress = (processed / total_combinations) * 100
                print(f"处理进度: {progress:.2f}%")

                # 检查是否已有评分
                cursor.execute("SELECT 1 FROM movie_rate WHERE movie_id = %s AND user_id = %s", (movie_id, user_id))
                if not cursor.fetchone():
                    # 生成随机评分
                    mark = random.randint(1, 5)
                    create_time = datetime.now()
                    batch.append((mark, create_time, movie_id, user_id))

                if len(batch) >= batch_size:
                    # 批量插入数据
                    insert_query = "INSERT INTO movie_rate (mark, create_time, movie_id, user_id) VALUES (%s, %s, %s, %s)"
                    cursor.executemany(insert_query, batch)
                    mydb.commit()
                    batch = []

        # 插入剩余的数据
        if batch:
            insert_query = "INSERT INTO movie_rate (mark, create_time, movie_id, user_id) VALUES (%s, %s, %s, %s)"
            cursor.executemany(insert_query, batch)
            mydb.commit()

    print("数据插入成功")
except Exception as e:
    # 回滚事务
    mydb.rollback()
    print(f"数据插入失败: {e}")
finally:
    # 关闭数据库连接
    mydb.close()