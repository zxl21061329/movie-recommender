import numpy as np
from movie.models import UserTagPrefer, UserTagPreferenceDegree


def normalize_tag_scores():
    # 获取所有用户标签偏好记录
    user_tag_preferences = UserTagPrefer.objects.all()

    # 提取所有评分
    scores = np.array([preference.score for preference in user_tag_preferences])

    # 计算均值和标准差
    mean_score = np.mean(scores)
    std_score = np.std(scores)

    # 进行Z - 归一化处理并保存到UserTagPreferenceDegree模型中
    for preference in user_tag_preferences:
        user = preference.user
        tag = preference.tag
        score = preference.score

        # 计算Z - 归一化后的分数
        if std_score != 0:
            normalized_score = (score - mean_score) / std_score
        else:
            normalized_score = 0

        # 更新或创建UserTagPreferenceDegree记录
        UserTagPreferenceDegree.objects.update_or_create(
            user=user,
            tag=tag,
            defaults={'preference_score': normalized_score}
        )


if __name__ == "__main__":
    normalize_tag_scores()
