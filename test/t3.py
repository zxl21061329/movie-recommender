import os


def print_folder_structure(folder_path, level=0):
    try:
        for root, dirs, _ in os.walk(folder_path):
            if root == folder_path:
                for dir_name in dirs:
                    # 根据层级添加缩进，展示层级结构
                    indent = "  " * level
                    print(f"{indent}{dir_name}")
                    sub_folder_path = os.path.join(folder_path, dir_name)
                    # 递归处理子文件夹
                    print_folder_structure(sub_folder_path, level + 1)
    except FileNotFoundError:
        print(f"指定的文件夹路径 {folder_path} 未找到。")
    except PermissionError:
        print(f"没有权限访问指定的文件夹路径 {folder_path}。")


if __name__ == "__main__":
    # 请将这里替换为你实际要读取的文件夹路径
    target_folder = "D:\movie-recommender\code"
    print_folder_structure(target_folder)