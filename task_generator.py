import json
import os
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DEFAULT_FILE = "tasks.json"
TASK_TYPES = ["Учёба", "Спорт", "Работа", "Другое"]
INITIAL_TASKS = [
    {"text": "Прочитать статью по теме курсовой", "type": "Учёба"},
    {"text": "Сделать зарядку", "type": "Спорт"},
    {"text": "Проверить почту", "type": "Работа"},
    {"text": "Записать план на день", "type": "Другое"},
    {"text": "Написать отчёт", "type": "Работа"},
    {"text": "Решить 5 задач из учебника", "type": "Учёба"},
    {"text": "Пробежать 3 км", "type": "Спорт"},
]
DATE_FMT = "%Y-%m-%d %H:%M:%S"

class TaskGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("750x620")
        self.root.minsize(660, 540)
        self.tasks = list(INITIAL_TASKS)
        self.history = []
        self.current_task = None
        self.task_var = tk.StringVar()
        self.new_task_var = tk.StringVar()
        self.type_var = tk.StringVar(value=TASK_TYPES[0])
        self.filter_type_var = tk.StringVar(value="Все")
        self.status_var = tk.StringVar(value="Готово")
        self._build_ui()
    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)
        gen_frame = ttk.LabelFrame(main, text="Генерация задачи", padding=10)
        gen_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        gen_frame.columnconfigure(0, weight=1)
        gen_frame.columnconfigure(1, weight=1)
        ttk.Label(gen_frame, text="Добавить новую задачу").grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(gen_frame, textvariable=self.new_task_var).grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ttk.Combobox(gen_frame, textvariable=self.type_var, values=TASK_TYPES, state="readonly").grid(row=0, column=2, sticky="ew", padx=(0, 10))
        ttk.Button(gen_frame, text="Добавить задачу", command=self.add_task).grid(row=0, column=3)
        ttk.Button(gen_frame, text="Сгенерировать задачу", command=self.generate_task).grid(row=1, column=0, columnspan=4, pady=8, sticky="ew")
        ttk.Label(gen_frame, text="Текущая задача:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky="w", columnspan=2)
        ttk.Label(gen_frame, textvariable=self.task_var, wraplength=540, anchor="w", justify="left", relief="sunken", padding=6).grid(row=3, column=0, columnspan=4, sticky="ew", pady=6)
        filter_frame = ttk.LabelFrame(main, text="Фильтр истории", padding=10)
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        ttk.Label(filter_frame, text="Тип задачи").grid(row=0, column=0, sticky="w")
        ttk.Combobox(filter_frame, textvariable=self.filter_type_var, values=["Все"] + TASK_TYPES, state="readonly").grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=2, padx=(8, 0))
        ttk.Button(filter_frame, text="Очистить историю", command=self.clear_history).grid(row=0, column=3, padx=(8, 0))
        hist_frame = ttk.LabelFrame(main, text="История задач", padding=10)
        hist_frame.grid(row=2, column=0, sticky="nsew")
        hist_frame.columnconfigure(0, weight=1)
        hist_frame.rowconfigure(0, weight=1)
        columns = ("id", "task", "type", "timestamp")
        self.tree = ttk.Treeview(hist_frame, columns=columns, show="headings", height=12)
        for c, t, w in [("id","№",50),("task","Задача",280),("type","Тип",120),("timestamp","Время",160)]:
            self.tree.heading(c, text=t); self.tree.column(c, width=w, anchor="center" if c!="task" else "w")
        scrollbar = ttk.Scrollbar(hist_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        status = ttk.Label(main, textvariable=self.status_var, relief="sunken", anchor="w", padding=6)
        status.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=4, column=0, sticky="ew", pady=(6, 0))
        btn_frame.columnconfigure(0, weight=1); btn_frame.columnconfigure(1, weight=1)
        ttk.Button(btn_frame, text="Сохранить историю (JSON)", command=self.save_json).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(btn_frame, text="Загрузить историю (JSON)", command=self.load_json).grid(row=0, column=1, sticky="ew")
    def _validate_new_task(self, text):
        text = text.strip()
        if not text:
            raise ValueError("Текст задачи не может быть пустым.")
        return text
    def add_task(self):
        try:
            text = self._validate_new_task(self.new_task_var.get())
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e)); return
        t = self.type_var.get()
        self.tasks.append({"text": text, "type": t})
        self.new_task_var.set("")
        self.status_var.set(f"Задача добавлена: {text} [{t}]")
    def generate_task(self):
        if not self.tasks:
            messagebox.showwarning("Внимание", "Нет задач для генерации. Добавьте хотя бы одну."); return
        item = random.choice(self.tasks)
        from datetime import datetime
        now = datetime.now().strftime(DATE_FMT)
        self.current_task = {"id": len(self.history)+1, "text": item["text"], "type": item["type"], "timestamp": now}
        self.history.append(self.current_task)
        self.task_var.set(f"[{item['type']}] {item['text']}")
        self.refresh_history()
        self.status_var.set(f"Сгенерирована задача №{self.current_task['id']}")
    def refresh_history(self, data=None):
        data = self.history if data is None else data
        self.tree.delete(*self.tree.get_children())
        for item in data:
            self.tree.insert("", "end", values=(item["id"], item["text"], item["type"], item["timestamp"]))
    def apply_filter(self):
        task_type = self.filter_type_var.get()
        filtered = self.history if task_type == "Все" else [item for item in self.history if item["type"] == task_type]
        self.refresh_history(filtered)
        self.status_var.set(f"Фильтр: {task_type}. Найдено записей: {len(filtered)}")
    def clear_history(self):
        if not self.history:
            messagebox.showinfo("История", "История уже пуста."); return
        if not messagebox.askyesno("Очистка", "Очистить всю историю?"): return
        self.history = []
        self.refresh_history()
        self.task_var.set("")
        self.status_var.set("История очищена")
    def save_json(self):
        file_path = filedialog.asksaveasfilename(title="Сохранить историю задач", defaultextension=".json", initialfile=DEFAULT_FILE, filetypes=[("JSON files", "*.json")])
        if not file_path: return
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"tasks": self.tasks, "history": self.history}, f, ensure_ascii=False, indent=4)
        self.status_var.set(f"История сохранена: {os.path.basename(file_path)}")
        messagebox.showinfo("Сохранение", "Данные сохранены в JSON.")
    def load_json(self):
        from datetime import datetime
        file_path = filedialog.askopenfilename(title="Загрузить историю задач", filetypes=[("JSON files", "*.json")])
        if not file_path: return
        try:
            with open(file_path, "r", encoding="utf-8") as f: data = json.load(f)
            tasks = data.get("tasks", []); history = data.get("history", [])
            validated_tasks=[]
            for item in tasks:
                text = self._validate_new_task(str(item.get("text", "")))
                ttype = str(item.get("type", "Другое"))
                if ttype not in TASK_TYPES: ttype = "Другое"
                validated_tasks.append({"text": text, "type": ttype})
            validated_history=[]
            for item in history:
                text = self._validate_new_task(str(item.get("text", "")))
                ttype = str(item.get("type", "Другое"))
                if ttype not in TASK_TYPES: ttype = "Другое"
                timestamp = str(item.get("timestamp", datetime.now().strftime(DATE_FMT)))
                validated_history.append({"id": len(validated_history)+1, "text": text, "type": ttype, "timestamp": timestamp})
            self.tasks = validated_tasks; self.history = validated_history; self.refresh_history(self.history)
            self.status_var.set(f"Загружено: {len(self.tasks)} задач, {len(self.history)} записей истории")
            messagebox.showinfo("Загрузка", "Данные загружены из JSON.")
        except (json.JSONDecodeError, OSError, ValueError) as e:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить файл: {e}")

def main():
    root = tk.Tk(); TaskGeneratorApp(root); root.mainloop()
if __name__ == "__main__": main()