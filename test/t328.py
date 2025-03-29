import pymysql
import numpy as np


def euclidean_distance(vec1, vec2):
    return np.linalg.norm(np.array(vec1) - np.array(vec2))


def find_similar_users(user_id, top_n=5):
    try:
        # 连接数据库
        mydb = pymysql.connect(
            host="localhost",
            user="root",
            password="123456",
            database="movierecdb"
        )
        cursor = mydb.cursor()

        # 获取所有用户的标签偏好度
        query = "SELECT user_id, tag_id, preference_score FROM movie_usertagpreferencedegree"
        cursor.execute(query)
        rows = cursor.fetchall()

        user_preferences = {}
        for row in rows:
            user_id_, tag_id, score = row
            if user_id_ not in user_preferences:
                user_preferences[user_id_] = {}
            user_preferences[user_id_][tag_id] = score

        # 对每个用户的偏好度进行z - 归一化处理
        for user, prefs in user_preferences.items():
            values = list(prefs.values())
            if values:
                mean_val = np.mean(values)
                std_val = np.std(values)
                if std_val != 0:
                    for tag_id in prefs:
                        prefs[tag_id] = (prefs[tag_id] - mean_val) / std_val

        # 获取所有标签 ID
        tag_ids = sorted(set(tag_id for user_prefs in user_preferences.values() for tag_id in user_prefs))

        # 构建用户 - 标签矩阵
        user_matrix = {}
        for user, prefs in user_preferences.items():
            user_vector = [prefs.get(tag_id, 0) for tag_id in tag_ids]
            user_matrix[user] = user_vector

        # 计算用户相似度
        target_user_vector = user_matrix.get(user_id)
        if target_user_vector is None:
            print(f"用户 ID {user_id} 未找到偏好数据。")
            return []

        similarities = []
        for other_user, other_vector in user_matrix.items():
            if other_user != user_id:
                distance = euclidean_distance(target_user_vector, other_vector)
                similarities.append((other_user, distance))

        # 按距离排序并取前 top_n 个（距离越小越相似）
        similarities.sort(key=lambda x: x[1])
        top_similar_users = similarities[:top_n]

        return top_similar_users

    except pymysql.Error as e:
        print(f"数据库错误: {e}")
    finally:
        if mydb:
            mydb.close()


if __name__ == "__main__":
    target_user_id = 2
    similar_users = find_similar_users(target_user_id)
    print(f"与用户 ID {target_user_id} 最相似的 5 个用户:")
    for user_id, similarity in similar_users:
        print(f"用户 ID: {user_id}, 距离: {similarity:.4f}")