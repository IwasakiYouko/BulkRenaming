import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os

# 创建 Tkinter 根窗口，但隐藏它
root = tk.Tk()
root.withdraw()

# 步骤1: 让用户选择文件夹路径
folder_path = filedialog.askdirectory(title="选择要批量重命名的文件夹")
if not folder_path:
    messagebox.showerror("错误", "未选择文件夹，程序退出。")
    exit()

# 步骤2: 输入命名的第一部分（前缀）
prefix = simpledialog.askstring("输入前缀", "请输入命名的第一部分（前缀）：")
if prefix is None:
    messagebox.showerror("错误", "输入取消，程序退出。")
    exit()

# 步骤3: 输入作为变量的第二部分（起始序号）
variable_start = simpledialog.askinteger("输入变量部分", "请输入作为变量的第二部分起始值（例如：1，表示从1开始编号）：")
if variable_start is None:
    messagebox.showerror("错误", "输入取消，程序退出。")
    exit()

# 步骤4: 输入命名的最后一部分（后缀）
suffix = simpledialog.askstring("输入后缀", "请输入命名的最后一部分（后缀）：")
if suffix is None:
    messagebox.showerror("错误", "输入取消，程序退出。")
    exit()

# 收集完成后，进行批量重命名
try:
    # 获取文件夹下所有文件，按名称排序
    files = sorted([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
    
    for i, old_name in enumerate(files):
        # 保留原文件扩展名
        ext = os.path.splitext(old_name)[1]
        # 新文件名：前缀 + (起始值 + i) + 后缀 + 扩展名
        new_name = f"{prefix}{variable_start + i}{suffix}{ext}"
        # 重命名
        os.rename(os.path.join(folder_path, old_name), os.path.join(folder_path, new_name))
    
    messagebox.showinfo("成功", f"批量重命名完成！处理了 {len(files)} 个文件。")
except Exception as e:
    messagebox.showerror("错误", f"重命名过程中出错：{str(e)}")