import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import hashlib
import string
from datetime import datetime, timedelta
from tkinter import scrolledtext

class BulkRenamerApp:
    def __init__(self, master):
        self.master = master
        master.title("批量文件重命名器")
        master.geometry("600x500")
        master.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 10), background="#f0f0f0")
        self.style.configure("TButton", font=("Arial", 10), padding=5)
        self.style.configure("TEntry", font=("Arial", 10))
        self.style.configure("TFrame", background="#f0f0f0")

        self.folder_path = tk.StringVar()
        self.parts = []  # List of parts: ('constant', value) or ('variable', var_type, params)

        self.create_widgets()

    def create_widgets(self):
        # Folder selection
        folder_frame = ttk.Frame(self.master, padding=10)
        folder_frame.pack(fill=tk.X)

        ttk.Label(folder_frame, text="文件夹路径：").pack(side=tk.LEFT, padx=5)
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="浏览", command=self.browse_folder).pack(side=tk.LEFT, padx=5)

        # Parts list
        self.parts_frame = ttk.Frame(self.master, padding=10)
        self.parts_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.parts_frame, text="文件名部分：", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        self.parts_listbox = tk.Listbox(self.parts_frame, height=10, font=("Arial", 10))
        self.parts_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        # Buttons for adding parts
        buttons_frame = ttk.Frame(self.parts_frame)
        buttons_frame.pack(fill=tk.X)

        ttk.Button(buttons_frame, text="添加常量", command=self.add_constant).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="添加变量", command=self.add_variable).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="移除最后部分", command=self.remove_last_part).pack(side=tk.LEFT, padx=5)

        # Rename button
        ttk.Button(self.master, text="重命名文件", command=self.perform_rename).pack(pady=10)

        # Continue button for multiple folders
        self.continue_button = ttk.Button(self.master, text="重命名另一个文件夹", command=self.reset_for_next, state=tk.DISABLED)
        self.continue_button.pack(pady=5)

    def browse_folder(self):
        path = filedialog.askdirectory(title="选择文件夹")
        if path:
            self.folder_path.set(path)

    def add_constant(self):
        constant = tk.simpledialog.askstring("添加常量", "输入常量字符串：", parent=self.master)
        if constant:
            self.parts.append(('constant', constant))
            self.update_parts_list()

    def add_variable(self):
        var_type = self.choose_variable_type()
        if var_type:
            params = self.get_variable_params(var_type)
            if params:
                self.parts.append(('variable', var_type, params))
                self.update_parts_list()

    def choose_variable_type(self):
        var_window = tk.Toplevel(self.master)
        var_window.title("选择变量类型")
        var_window.geometry("400x400")
        var_window.configure(bg="#f0f0f0")

        ttk.Label(var_window, text="选择变量类型：", font=("Arial", 12)).pack(pady=10)

        var_listbox = tk.Listbox(var_window, font=("Arial", 10))
        var_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        types = [
            "1. 数字（例如：1,2,3...）",
            "2. 字母（例如：A,B,C...）",
            "3. 日期（例如：20250101）",
            "4. 罗马数字（例如：I,II,III...）",
            "5. 十六进制（例如：A,B,10...）",
            "6. 八进制（例如：1,2,10...）",
            "7. 二进制（例如：1,10,11...）",
            "8. 时间戳（例如：20250101123045）",
            "9. 希腊字母（例如：alpha,beta... 或 α,β...）",
            "10. 月份（例如：January,February...）",
            "11. 周几（例如：Monday,Tuesday...）",
            "12. 自定义列表"
        ]
        for t in types:
            var_listbox.insert(tk.END, t)

        def select_var():
            selection = var_listbox.curselection()
            if selection:
                choice = var_listbox.get(selection[0]).split('.')[0].strip()
                var_type_map = {'1': 'number', '2': 'letter', '3': 'date', '4': 'roman', '5': 'hex', '6': 'octal', '7': 'binary', '8': 'timestamp', '9': 'greek', '10': 'month', '11': 'weekday', '12': 'custom'}
                var_window.quit()
                var_window.destroy()
                self.selected_var = var_type_map.get(choice)
            else:
                var_window.quit()
                var_window.destroy()
                self.selected_var = None

        ttk.Button(var_window, text="选择", command=select_var).pack(pady=5)

        var_window.protocol("WM_DELETE_WINDOW", lambda: (var_window.quit(), var_window.destroy()))
        var_window.mainloop()

        return getattr(self, 'selected_var', None)

    def get_variable_params(self, var_type):
        var_type_trans = {
            'number': '数字',
            'letter': '字母',
            'date': '日期',
            'roman': '罗马数字',
            'hex': '十六进制',
            'octal': '八进制',
            'binary': '二进制',
            'timestamp': '时间戳',
            'greek': '希腊字母',
            'month': '月份',
            'weekday': '周几',
            'custom': '自定义列表'
        }
        title = f"{var_type_trans.get(var_type, var_type)} 的参数"

        params_window = tk.Toplevel(self.master)
        params_window.title(title)
        params_window.geometry("400x300")
        params_window.configure(bg="#f0f0f0")

        params = {}
        frame = ttk.Frame(params_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        if var_type in ['number', 'hex', 'octal', 'binary']:
            ttk.Label(frame, text="起始值：").pack(anchor=tk.W)
            start_entry = ttk.Entry(frame)
            start_entry.pack(fill=tk.X)
            ttk.Label(frame, text="步长：").pack(anchor=tk.W)
            step_entry = ttk.Entry(frame, text="1")
            step_entry.pack(fill=tk.X)
            ttk.Label(frame, text="填充位数（0表示无）：").pack(anchor=tk.W)
            padding_entry = ttk.Entry(frame, text="0")
            padding_entry.pack(fill=tk.X)
            if var_type == 'hex':
                case_var = tk.StringVar(value="upper")
                ttk.Label(frame, text="大小写：").pack(anchor=tk.W)
                ttk.Radiobutton(frame, text="大写", variable=case_var, value="upper").pack(anchor=tk.W)
                ttk.Radiobutton(frame, text="小写", variable=case_var, value="lower").pack(anchor=tk.W)

            def save_params():
                try:
                    params['start'] = int(start_entry.get())
                    params['step'] = int(step_entry.get())
                    params['padding'] = int(padding_entry.get())
                    if var_type == 'hex':
                        params['case'] = case_var.get()
                    params_window.quit()
                except ValueError:
                    messagebox.showerror("错误", "无效输入", parent=params_window)

        elif var_type == 'letter':
            ttk.Label(frame, text="起始字母（例如：A）：").pack(anchor=tk.W)
            start_letter_entry = ttk.Entry(frame)
            start_letter_entry.pack(fill=tk.X)
            case_var = tk.StringVar(value="upper")
            ttk.Label(frame, text="大小写：").pack(anchor=tk.W)
            ttk.Radiobutton(frame, text="大写", variable=case_var, value="upper").pack(anchor=tk.W)
            ttk.Radiobutton(frame, text="小写", variable=case_var, value="lower").pack(anchor=tk.W)

            def save_params():
                start_letter = start_letter_entry.get().upper()[:1]
                if start_letter:
                    params['start_letter'] = start_letter
                    params['case'] = case_var.get()
                    params_window.quit()
                else:
                    messagebox.showerror("错误", "无效起始字母", parent=params_window)

        elif var_type == 'date':
            ttk.Label(frame, text="起始日期（YYYY-MM-DD，空为今天）：").pack(anchor=tk.W)
            start_date_entry = ttk.Entry(frame)
            start_date_entry.pack(fill=tk.X)
            ttk.Label(frame, text="天数步长：").pack(anchor=tk.W)
            days_step_entry = ttk.Entry(frame, text="1")
            days_step_entry.pack(fill=tk.X)
            ttk.Label(frame, text="日期格式（例如：%Y%m%d）：").pack(anchor=tk.W)
            format_entry = ttk.Entry(frame, text="%Y%m%d")
            format_entry.pack(fill=tk.X)

            def save_params():
                start_date_str = start_date_entry.get()
                if not start_date_str:
                    params['start_date'] = datetime.now()
                else:
                    try:
                        params['start_date'] = datetime.strptime(start_date_str, '%Y-%m-%d')
                    except ValueError:
                        messagebox.showerror("错误", "无效日期格式", parent=params_window)
                        return
                try:
                    params['days_step'] = int(days_step_entry.get())
                    params['date_format'] = format_entry.get()
                    params_window.quit()
                except ValueError:
                    messagebox.showerror("错误", "无效步长", parent=params_window)

        elif var_type == 'roman':
            ttk.Label(frame, text="起始数字（例如：1，表示从I开始）：").pack(anchor=tk.W)
            start_entry = ttk.Entry(frame)
            start_entry.pack(fill=tk.X)

            def save_params():
                try:
                    params['start'] = int(start_entry.get())
                    params_window.quit()
                except ValueError:
                    messagebox.showerror("错误", "无效输入", parent=params_window)

        elif var_type == 'timestamp':
            ttk.Label(frame, text="起始时间（YYYY-MM-DD HH:MM:SS，空为现在）：").pack(anchor=tk.W)
            start_time_entry = ttk.Entry(frame)
            start_time_entry.pack(fill=tk.X)
            ttk.Label(frame, text="秒数步长：").pack(anchor=tk.W)
            seconds_step_entry = ttk.Entry(frame, text="1")
            seconds_step_entry.pack(fill=tk.X)
            ttk.Label(frame, text="时间格式（例如：%Y%m%d%H%M%S）：").pack(anchor=tk.W)
            format_entry = ttk.Entry(frame, text="%Y%m%d%H%M%S")
            format_entry.pack(fill=tk.X)

            def save_params():
                start_time_str = start_time_entry.get()
                if not start_time_str:
                    params['start_time'] = datetime.now()
                else:
                    try:
                        params['start_time'] = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        messagebox.showerror("错误", "无效时间格式", parent=params_window)
                        return
                try:
                    params['seconds_step'] = int(seconds_step_entry.get())
                    params['time_format'] = format_entry.get()
                    params_window.quit()
                except ValueError:
                    messagebox.showerror("错误", "无效步长", parent=params_window)

        elif var_type == 'greek':
            symbols_var = tk.BooleanVar(value=False)
            ttk.Label(frame, text="使用符号（是：α,β,... 否：alpha,beta,...）：").pack(anchor=tk.W)
            ttk.Checkbutton(frame, text="使用符号", variable=symbols_var).pack(anchor=tk.W)
            ttk.Label(frame, text="起始索引（0表示从第一个开始）：").pack(anchor=tk.W)
            start_idx_entry = ttk.Entry(frame, text="0")
            start_idx_entry.pack(fill=tk.X)

            def save_params():
                try:
                    params['start_idx'] = int(start_idx_entry.get())
                    if symbols_var.get():
                        params['letters'] = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']
                    else:
                        params['letters'] = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega']
                    params_window.quit()
                except ValueError:
                    messagebox.showerror("错误", "无效输入", parent=params_window)

        elif var_type == 'month':
            abbr_var = tk.BooleanVar(value=False)
            ttk.Label(frame, text="使用缩写（是：Jan,Feb,... 否：January,February,...）：").pack(anchor=tk.W)
            ttk.Checkbutton(frame, text="使用缩写", variable=abbr_var).pack(anchor=tk.W)
            ttk.Label(frame, text="起始索引（0表示从第一个开始）：").pack(anchor=tk.W)
            start_idx_entry = ttk.Entry(frame, text="0")
            start_idx_entry.pack(fill=tk.X)

            def save_params():
                try:
                    params['start_idx'] = int(start_idx_entry.get())
                    if abbr_var.get():
                        params['months'] = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    else:
                        params['months'] = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
                    params_window.quit()
                except ValueError:
                    messagebox.showerror("错误", "无效输入", parent=params_window)

        elif var_type == 'weekday':
            abbr_var = tk.BooleanVar(value=False)
            ttk.Label(frame, text="使用缩写（是：Mon,Tue,... 否：Monday,Tuesday,...）：").pack(anchor=tk.W)
            ttk.Checkbutton(frame, text="使用缩写", variable=abbr_var).pack(anchor=tk.W)
            ttk.Label(frame, text="起始索引（0表示从第一个开始）：").pack(anchor=tk.W)
            start_idx_entry = ttk.Entry(frame, text="0")
            start_idx_entry.pack(fill=tk.X)

            def save_params():
                try:
                    params['start_idx'] = int(start_idx_entry.get())
                    if abbr_var.get():
                        params['weekdays'] = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                    else:
                        params['weekdays'] = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    params_window.quit()
                except ValueError:
                    messagebox.showerror("错误", "无效输入", parent=params_window)

        elif var_type == 'custom':
            ttk.Label(frame, text="自定义列表（逗号分隔）：").pack(anchor=tk.W)
            custom_entry = ttk.Entry(frame)
            custom_entry.pack(fill=tk.X)

            def save_params():
                custom_str = custom_entry.get()
                params['custom_list'] = [item.strip() for item in custom_str.split(',') if item.strip()]
                if params['custom_list']:
                    params_window.quit()
                else:
                    messagebox.showerror("错误", "列表不能为空", parent=params_window)

        # Save button
        ttk.Button(params_window, text="保存", command=save_params).pack(pady=10)

        params_window.protocol("WM_DELETE_WINDOW", lambda: params_window.quit())
        params_window.mainloop()
        params_window.destroy()

        if params:
            return params
        else:
            return None

    def update_parts_list(self):
        self.parts_listbox.delete(0, tk.END)
        part_trans = {
            'constant': '常量',
            'number': '数字',
            'letter': '字母',
            'date': '日期',
            'roman': '罗马数字',
            'hex': '十六进制',
            'octal': '八进制',
            'binary': '二进制',
            'timestamp': '时间戳',
            'greek': '希腊字母',
            'month': '月份',
            'weekday': '周几',
            'custom': '自定义列表'
        }
        for part in self.parts:
            if part[0] == 'constant':
                self.parts_listbox.insert(tk.END, f"常量: {part[1]}")
            else:
                var_type = part[1]
                self.parts_listbox.insert(tk.END, f"变量: {part_trans.get(var_type, var_type)}")

    def remove_last_part(self):
        if self.parts:
            self.parts.pop()
            self.update_parts_list()

    def perform_rename(self):
        folder_path = self.folder_path.get()
        if not folder_path or not self.parts:
            messagebox.showerror("错误", "请选择文件夹并添加部分。")
            return

        try:
            files = sorted([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])

            # Temporary rename
            temp_names = []
            for old_name in files:
                file_path = os.path.join(folder_path, old_name)
                with open(file_path, 'rb') as f:
                    md5_hash = hashlib.md5(f.read()).hexdigest()[:16]
                ext = os.path.splitext(old_name)[1]
                temp_name = f"{md5_hash}{ext}"
                os.rename(file_path, os.path.join(folder_path, temp_name))
                temp_names.append(temp_name)

            # Final rename
            for i, temp_name in enumerate(temp_names):
                ext = os.path.splitext(temp_name)[1]
                name_parts = []
                for part in self.parts:
                    if part[0] == 'constant':
                        name_parts.append(part[1])
                    else:
                        var_type, params = part[1], part[2]
                        name_parts.append(self.generate_variable(i, var_type, params))
                new_name = ''.join(name_parts) + ext
                os.rename(os.path.join(folder_path, temp_name), os.path.join(folder_path, new_name))

            messagebox.showinfo("成功", f"重命名了 {len(files)} 个文件。")
            self.continue_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def generate_variable(self, i, var_type, params):
        if var_type == 'number':
            start = params.get('start', 1)
            step = params.get('step', 1)
            padding = params.get('padding', 0)
            value = start + i * step
            if padding > 0:
                return f"{value:0{padding}d}"
            return str(value)
        
        elif var_type == 'letter':
            case = params.get('case', 'upper')
            start_letter = params.get('start_letter', 'A').upper()
            start_idx = ord(start_letter) - ord('A')
            letters = string.ascii_uppercase if case == 'upper' else string.ascii_lowercase
            value = ''
            num = start_idx + i
            while num >= 0:
                value = letters[num % 26] + value
                num = num // 26 - 1
            return value
        
        elif var_type == 'date':
            start_date = params.get('start_date', datetime.now())
            days_step = params.get('days_step', 1)
            date_format = params.get('date_format', '%Y%m%d')
            current_date = start_date + timedelta(days=i * days_step)
            return current_date.strftime(date_format)
        
        elif var_type == 'roman':
            start = params.get('start', 1)
            value = start + i
            roman_numerals = [
                (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
                (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
                (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
            ]
            roman = ''
            for arabic, symbol in roman_numerals:
                while value >= arabic:
                    roman += symbol
                    value -= arabic
            return roman
        
        elif var_type == 'hex':
            start = params.get('start', 0)
            step = params.get('step', 1)
            padding = params.get('padding', 0)
            case = params.get('case', 'upper')
            value = start + i * step
            hex_value = format(value, 'x' if case == 'lower' else 'X')
            if padding > 0:
                hex_value = hex_value.zfill(padding)
            return hex_value
        
        elif var_type == 'octal':
            start = params.get('start', 0)
            step = params.get('step', 1)
            padding = params.get('padding', 0)
            value = start + i * step
            oct_value = format(value, 'o')
            if padding > 0:
                oct_value = oct_value.zfill(padding)
            return oct_value
        
        elif var_type == 'binary':
            start = params.get('start', 0)
            step = params.get('step', 1)
            padding = params.get('padding', 0)
            value = start + i * step
            bin_value = format(value, 'b')
            if padding > 0:
                bin_value = bin_value.zfill(padding)
            return bin_value
        
        elif var_type == 'timestamp':
            start_time = params.get('start_time', datetime.now())
            seconds_step = params.get('seconds_step', 1)
            time_format = params.get('time_format', '%Y%m%d%H%M%S')
            current_time = start_time + timedelta(seconds=i * seconds_step)
            return current_time.strftime(time_format)
        
        elif var_type == 'greek':
            letters = params.get('letters', ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega'])
            start_idx = params.get('start_idx', 0)
            return letters[(start_idx + i) % len(letters)]
        
        elif var_type == 'month':
            months = params.get('months', ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
            start_idx = params.get('start_idx', 0)
            return months[(start_idx + i) % len(months)]
        
        elif var_type == 'weekday':
            weekdays = params.get('weekdays', ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
            start_idx = params.get('start_idx', 0)
            return weekdays[(start_idx + i) % len(weekdays)]
        
        elif var_type == 'custom':
            custom_list = params.get('custom_list', [])
            if not custom_list:
                return ''
            return custom_list[i % len(custom_list)]
        
        else:
            raise ValueError("未知的变量类型")

    def reset_for_next(self):
        if messagebox.askyesno("继续？", "重命名另一个文件夹？"):
            self.folder_path.set("")
            self.parts = []
            self.update_parts_list()
            self.continue_button.config(state=tk.DISABLED)
        else:
            self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = BulkRenamerApp(root)
    root.mainloop()