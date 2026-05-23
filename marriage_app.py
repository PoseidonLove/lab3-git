import pandas as pd
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def read_xlsx_smart(path):
    try:
        return pd.read_excel(path)
    except Exception:
        raise Exception("Не удалось загрузить Excel файл")


class MarriageAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ браков и разводов")
        self.root.geometry("1300x850")

        self.data = None
        self.current_fig = None

        self.create_ui()

    def create_ui(self):
        # ===== TOP PANEL =====
        top_frame = Frame(self.root, pady=10)
        top_frame.pack(fill=X)

        Button(top_frame, text="Импорт XLSX", width=18, command=self.load_file).pack(side=LEFT, padx=5)
        Button(top_frame, text="График", width=18, command=self.build_graphs).pack(side=LEFT, padx=5)
        Button(top_frame, text="Прогноз", width=18, command=self.build_forecast).pack(side=LEFT, padx=5)
        Button(top_frame, text="Очистить", width=18, command=self.clear_all).pack(side=LEFT, padx=5)

        Button(top_frame, text="Сохранить график", width=18, command=self.save_graph).pack(side=LEFT, padx=5)

        # ===== CONTROL PANEL =====
        control_frame = Frame(self.root, pady=5)
        control_frame.pack(fill=X)

        Label(control_frame, text="N (скользящая средняя):").pack(side=LEFT, padx=5)

        self.n_scale = Scale(control_frame, from_=2, to=10, orient=HORIZONTAL)
        self.n_scale.set(3)
        self.n_scale.pack(side=LEFT)

        # ===== TABLE =====
        table_frame = Frame(self.root)
        table_frame.pack(fill=BOTH, expand=True, pady=10)

        self.tree = ttk.Treeview(table_frame)
        self.tree.pack(fill=BOTH, expand=True)

        # ===== OUTPUT =====
        output_frame = Frame(self.root)
        output_frame.pack(fill=X, pady=5)

        Label(output_frame, text="Результаты анализа:").pack(anchor=W)

        self.result_text = Text(output_frame, height=8)
        self.result_text.pack(fill=X)

    # ================= LOAD =================
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel файлы", "*.xlsx")])
        if not file_path:
            return

        try:
            self.data = pd.read_excel(file_path)
            self.show_table()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ================= TABLE =================
    def show_table(self):
        self.tree.delete(*self.tree.get_children())

        self.tree["columns"] = list(self.data.columns)
        self.tree["show"] = "headings"

        for col in self.data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        for _, row in self.data.iterrows():
            self.tree.insert("", END, values=list(row))

    # ================= ANALYSIS =================
    def analyze_data(self):
        result = ""

        male_marriage_age = self.data.groupby("Возраст_мужчин_брак")["Браки"].sum().idxmax()
        male_divorce_age = self.data.groupby("Возраст_мужчин_развод")["Разводы"].sum().idxmax()

        female_marriage_age = self.data.groupby("Возраст_женщин_брак")["Браки"].sum().idxmax()
        female_divorce_age = self.data.groupby("Возраст_женщин_развод")["Разводы"].sum().idxmax()

        result += f"Мужчины чаще женились в возрасте: {male_marriage_age}\n"
        result += f"Мужчины чаще разводились в возрасте: {male_divorce_age}\n\n"
        result += f"Женщины чаще выходили замуж в возрасте: {female_marriage_age}\n"
        result += f"Женщины чаще разводились в возрасте: {female_divorce_age}\n"

        self.result_text.delete(1.0, END)
        self.result_text.insert(END, result)

    # ================= GRAPH =================
    def build_graphs(self):
        if self.data is None:
            messagebox.showwarning("Ошибка", "Сначала загрузите файл")
            return

        window = Toplevel(self.root)
        window.title("График")

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(self.data["Год"], self.data["Браки"], marker='o', label="Браки")
        ax.plot(self.data["Год"], self.data["Разводы"], marker='o', label="Разводы")

        ax.set_title("Динамика браков и разводов")
        ax.set_xlabel("Год")
        ax.set_ylabel("Количество")
        ax.legend()
        ax.grid()

        self.current_fig = fig

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        self.analyze_data()

    # ================= FORECAST =================
    def moving_average_forecast(self, values, n, steps):
        forecast = values.copy()

        for _ in range(steps):
            avg = sum(forecast[-n:]) / n
            forecast.append(avg)

        return forecast

    def build_forecast(self):
        if self.data is None:
            messagebox.showwarning("Ошибка", "Сначала загрузите файл")
            return

        try:
            n = self.n_scale.get()

            marriages = self.data["Браки"].tolist()
            divorces = self.data["Разводы"].tolist()
            years = self.data["Год"].tolist()

            steps = 5

            marriage_forecast = self.moving_average_forecast(marriages, n, steps)
            divorce_forecast = self.moving_average_forecast(divorces, n, steps)

            future_years = years.copy()
            last_year = years[-1]

            for i in range(1, steps + 1):
                future_years.append(last_year + i)

            window = Toplevel(self.root)
            window.title("Прогноз")

            fig, ax = plt.subplots(figsize=(10, 5))

            ax.plot(years, marriages, label="Браки")
            ax.plot(years, divorces, label="Разводы")

            ax.plot(future_years, marriage_forecast, "--o", label="Прогноз браков")
            ax.plot(future_years, divorce_forecast, "--o", label="Прогноз разводов")

            ax.set_title("Прогноз (скользящая средняя)")
            ax.set_xlabel("Год")
            ax.set_ylabel("Количество")
            ax.legend()
            ax.grid()

            self.current_fig = fig

            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ================= SAVE GRAPH =================
    def save_graph(self):
        if self.current_fig is None:
            messagebox.showwarning("Ошибка", "Сначала постройте график")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG файл", "*.png")])
        if file_path:
            self.current_fig.savefig(file_path)
            messagebox.showinfo("Успех", "График сохранён")

    # ================= CLEAR =================
    def clear_all(self):
        self.tree.delete(*self.tree.get_children())
        self.result_text.delete(1.0, END)
        self.data = None
        self.current_fig = None


root = Tk()
app = MarriageAnalyzer(root)
root.mainloop()