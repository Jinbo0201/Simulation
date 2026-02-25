import tkinter as tk

# 创建一个空白窗口
root = tk.Tk()
root.title("测试 tkinter")
root.geometry("300x200")

# 添加一个标签
label = tk.Label(root, text="tkinter 可用！", font=("Arial", 16))
label.pack(pady=50)

# 运行主循环
root.mainloop()