import pandas as pd

# 读取CSV文件
df = pd.read_csv("movies.csv")

# 假设电影类型存储在 'genres' 列，按 ',' 分割并获取唯一值
unique_genres = set()
df['genres'].dropna().apply(lambda x: unique_genres.update(x.split('|')))

print(f"电影类型有 {len(unique_genres)} 种: {unique_genres}")
