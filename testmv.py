import os
import django
from django.db import connection
from django.core.management import call_command


def test_database_connection():
    # 设置Django项目的配置模块，替换成你实际的项目名称
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movierecomend.settings')
    django.setup()

    try:
        with connection.cursor() as cursor:
            # 执行一个简单的查询语句，这里选择查询数据库版本信息，你也可以换成其他简单语句如 "SELECT 1"
            cursor.execute("SELECT VERSION()")
            result = cursor.fetchone()
            print(f"数据库连接成功，数据库版本信息: {result[0]}")
    except Exception as e:
        print(f"数据库连接失败，错误原因: {e}")


if __name__ == "__main__":
    test_database_connection()
    # 可以额外检查是否能执行数据库迁移命令，如果迁移命令能正常准备，也能侧面说明数据库连接基本正常
    try:
        call_command('makemigrations', dry_run=True, verbosity=0)
        print("能够正常执行数据库迁移相关准备工作，数据库连接大概率可用")
    except Exception as e:
        print(f"执行数据库迁移相关准备工作失败，可能数据库连接有问题，错误信息: {e}")