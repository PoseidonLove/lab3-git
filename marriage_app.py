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
        self.root.geometry("1200x800")

        self.data = None

        self.create_ui()

    def create_ui(self):
        top_frame = Frame(self.root)
        top_frame.pack(pady=10)

        Button(
            top_frame,
            text="Импорт XLSX",
            command=self.load_file,
            width=20
        ).grid(row=0, column=0, padx=5)

        Button(
            top_frame,
            text="Показать график",
            command=self.build_graphs,
            width=20
        ).grid(row=0, column=1, padx=5)

        Button(
            top_frame,
            text="Прогноз",
            command=self.build_forecast,
            width=20
        ).grid(row=0, column=2, padx=5)

        Label(top_frame, text="N (скользящая средняя):").grid(row=0, column=3)

        self.n_entry = Entry(top_frame, width=10)
        self.n_entry.insert(0, "3")
        self.n_entry.grid(row=0, column=4, padx=5)

        self.tree = ttk.Treeview(self.root)
        self.tree.pack(fill=BOTH, expand=True, pady=10)

        self.result_text = Text(self.root, height=10)
        self.result_text.pack(fill=X, padx=10, pady=10)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel файлы", "*.xlsx")]
        )

        if not file_path:
            return

        try:
            self.data = read_xlsx_smart(file_path)
            self.show_table()

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def show_table(self):
        self.tree.delete(*self.tree.get_children())

        self.tree["columns"] = list(self.data.columns)
        self.tree["show"] = "headings"

        for col in self.data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160)

        for _, row in self.data.iterrows():
            self.tree.insert("", END, values=list(row))

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

    def build_graphs(self):
        if self.data is None:
            messagebox.showwarning("Ошибка", "Сначала загрузите файл")
            return

        window = Toplevel(self.root)
        window.title("Графики")

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(self.data["Год"], self.data["Браки"], marker='o', label="Браки")
        ax.plot(self.data["Год"], self.data["Разводы"], marker='o', label="Разводы")

        ax.set_title("Браки и разводы по годам")
        ax.set_xlabel("Год")
        ax.set_ylabel("Количество")
        ax.legend()
        ax.grid()

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        self.analyze_data()

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
            n = int(self.n_entry.get())

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

            ax.set_title("Прогноз методом скользящей средней")
            ax.set_xlabel("Год")
            ax.set_ylabel("Количество")
            ax.legend()
            ax.grid()

            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


root = Tk()
app = MarriageAnalyzer(root)
root.mainloop()