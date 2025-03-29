import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity

# 1. 数据加载与预处理
ratings = pd.read_csv('ratings.csv')
movies = pd.read_csv('movies.csv')

# 过滤高评分（假设 ≥4 为正样本）
high_ratings = ratings[ratings['rating'] >= 4]

# 按用户划分训练集和测试集，确保每个用户至少有1个测试样本
train_data, test_data = [], []
for user_id, user_ratings in high_ratings.groupby('userId'):
    if len(user_ratings) > 1:  # 确保有数据可分
        user_train, user_test = train_test_split(user_ratings, test_size=0.2, random_state=42)
        train_data.append(user_train)
        test_data.append(user_test)
    else:
        train_data.append(user_ratings)  # 评分较少时全用于训练

train_data = pd.concat(train_data)
test_data = pd.concat(test_data) if test_data else pd.DataFrame(columns=high_ratings.columns)

# 2. 构建用户-电影矩阵
all_ratings = pd.concat([train_data, ratings[ratings['rating'] < 4]])
user_movie_matrix = all_ratings.pivot_table(index='userId', columns='movieId', values='rating', fill_value=0)

# 3. 用户相似度计算
user_similarity = cosine_similarity(user_movie_matrix)
user_similarity_df = pd.DataFrame(user_similarity, index=user_movie_matrix.index, columns=user_movie_matrix.index)

# 4. 生成推荐列表
def predict_ratings(user_id, user_similarity_df, user_movie_matrix, n_neighbors=10):
    if user_id not in user_movie_matrix.index:
        return pd.Series(dtype=float)  # 避免索引错误

    # 获取最相似用户（排除自己）
    sim_users = user_similarity_df[user_id].drop(user_id, errors='ignore').nlargest(n_neighbors).index

    # 计算相似用户加权评分
    sim_weights = user_similarity_df.loc[user_id, sim_users].values.reshape(-1, 1)
    sim_ratings = user_movie_matrix.loc[sim_users]

    # 计算加权平均分数（避免除0）
    weighted_ratings = np.dot(sim_ratings.T, sim_weights).flatten()
    norm_weights = np.sum(sim_weights) if np.sum(sim_weights) > 0 else 1
    predicted_scores = pd.Series(weighted_ratings / norm_weights, index=user_movie_matrix.columns)

    # 排除已评分电影
    rated_movies = user_movie_matrix.loc[user_id] > 0
    return predicted_scores[~rated_movies].sort_values(ascending=False)

# 5. 评估指标计算
def calculate_metrics(recommendations, test_items):
    if not recommendations:
        return {'hr': 0, 'precision': 0, 'recall': 0, 'ndcg': 0}

    hits = len(set(recommendations) & set(test_items))
    precision = hits / len(recommendations) if recommendations else 0
    recall = hits / len(test_items) if test_items else 0

    # 计算 DCG 和 IDCG 避免 ZeroDivisionError
    dcg = sum(1 / np.log2(i + 2) for i, item in enumerate(recommendations) if item in test_items) if hits > 0 else 0
    idcg = sum(1 / np.log2(i + 2) for i in range(min(len(test_items), len(recommendations)))) if test_items else 1
    ndcg = dcg / idcg if idcg > 0 else 0

    return {'hr': 1 if hits > 0 else 0, 'precision': precision, 'recall': recall, 'ndcg': ndcg}

# 6. 计算所有用户的平均指标
metrics = []
for user_id in test_data['userId'].unique():
    test_items = test_data[test_data['userId'] == user_id]['movieId'].tolist()
    recommendations = predict_ratings(user_id, user_similarity_df, user_movie_matrix).head(10).index.tolist()
    metrics.append(calculate_metrics(recommendations, test_items))

# 计算平均指标
avg_hr = np.mean([m['hr'] for m in metrics]) if metrics else 0
avg_precision = np.mean([m['precision'] for m in metrics]) if metrics else 0
avg_recall = np.mean([m['recall'] for m in metrics]) if metrics else 0
avg_ndcg = np.mean([m['ndcg'] for m in metrics]) if metrics else 0

# 输出结果
print(f'HR@10: {avg_hr:.4f}')
print(f'Precision@10: {avg_precision:.4f}')
print(f'Recall@10: {avg_recall:.4f}')
print(f'NDCG@10: {avg_ndcg:.4f}')
