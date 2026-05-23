import pandas as pd
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


def read_xlsx(path):
    try:
        return pd.read_excel(path)
    except Exception:
        raise Exception("Ошибка загрузки Excel файла")


class MarriageAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ браков и разводов")
        self.root.geometry("1400x900")

        self.data = None

        self.create_ui()

    # ===================== UI =====================
    def create_ui(self):
        top_frame = Frame(self.root)
        top_frame.pack(fill=X, pady=10)

        Button(
            top_frame,
            text="Открыть XLSX",
            command=self.load_file,
            width=18
        ).pack(side=LEFT, padx=5)

        Button(
            top_frame,
            text="Показать график",
            command=self.build_graph,
            width=18
        ).pack(side=LEFT, padx=5)

        Button(
            top_frame,
            text="Построить прогноз",
            command=self.build_forecast,
            width=18
        ).pack(side=LEFT, padx=5)

        Button(
            top_frame,
            text="Сброс",
            command=self.clear_data,
            width=18
        ).pack(side=LEFT, padx=5)

        Label(top_frame, text="Количество лет прогноза:").pack(side=LEFT, padx=5)

        self.forecast_years = Scale(
            top_frame,
            from_=1,
            to=10,
            orient=HORIZONTAL
        )
        self.forecast_years.set(5)
        self.forecast_years.pack(side=LEFT)

        Label(top_frame, text="Скользящая средняя (N):").pack(side=LEFT, padx=10)

        self.moving_n = Scale(
            top_frame,
            from_=2,
            to=10,
            orient=HORIZONTAL
        )
        self.moving_n.set(3)
        self.moving_n.pack(side=LEFT)

        # Таблица
        self.tree = ttk.Treeview(self.root)
        self.tree.pack(fill=BOTH, expand=True, pady=10)

        # Поле результатов
        self.result_text = Text(self.root, height=10)
        self.result_text.pack(fill=X, padx=10, pady=10)

    # ===================== Загрузка файла =====================
    def load_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx")]
        )

        if not path:
            return

        try:
            self.data = read_xlsx(path)
            self.show_table()
            self.analyze_data()

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ===================== Таблица =====================
    def show_table(self):
        self.tree.delete(*self.tree.get_children())

        self.tree["columns"] = list(self.data.columns)
        self.tree["show"] = "headings"

        for col in self.data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        for _, row in self.data.iterrows():
            self.tree.insert("", END, values=list(row))

    # ===================== Анализ возрастов =====================
    def analyze_data(self):
        df = self.data

        male_marriage_age = df.groupby(
            "Возраст_мужчин_брак"
        )["Браки"].sum().idxmax()

        male_divorce_age = df.groupby(
            "Возраст_мужчин_развод"
        )["Разводы"].sum().idxmax()

        female_marriage_age = df.groupby(
            "Возраст_женщин_брак"
        )["Браки"].sum().idxmax()

        female_divorce_age = df.groupby(
            "Возраст_женщин_развод"
        )["Разводы"].sum().idxmax()

        result = ""
        result += f"Мужчины чаще женились в возрасте: {male_marriage_age}\n"
        result += f"Мужчины чаще разводились в возрасте: {male_divorce_age}\n\n"

        result += f"Женщины чаще выходили замуж в возрасте: {female_marriage_age}\n"
        result += f"Женщины чаще разводились в возрасте: {female_divorce_age}\n"

        self.result_text.delete(1.0, END)
        self.result_text.insert(END, result)

    # ===================== Основной график =====================
    def build_graph(self):
        if self.data is None:
            messagebox.showwarning("Ошибка", "Сначала загрузите файл")
            return

        df = self.data

        graph_window = Toplevel(self.root)
        graph_window.title("Графики")

        fig, ax = plt.subplots(figsize=(11, 6))

        ax.plot(
            df["Год"],
            df["Браки"],
            marker='o',
            linewidth=2,
            label="Браки"
        )

        ax.plot(
            df["Год"],
            df["Разводы"],
            marker='o',
            linewidth=2,
            label="Разводы"
        )

        ax.set_title("Динамика браков и разводов")
        ax.set_xlabel("Год")
        ax.set_ylabel("Количество")
        ax.grid()
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, graph_window)
        toolbar.update()

    # ===================== Скользящая средняя =====================
    def moving_average_forecast(self, values, window_size, forecast_steps):
        window_size = int(window_size)
        forecast_steps = int(forecast_steps)

        result = values.copy()

        for _ in range(forecast_steps):
            avg = sum(result[-window_size:]) / window_size
            result.append(avg)

        return result

    # ===================== Прогноз =====================
    def build_forecast(self):
        if self.data is None:
            messagebox.showwarning("Ошибка", "Сначала загрузите файл")
            return

        df = self.data

        years = df["Год"].tolist()

        marriages = df["Браки"].tolist()
        divorces = df["Разводы"].tolist()

        forecast_years_count = self.forecast_years.get()
        moving_n = self.moving_n.get()

        marriage_forecast = self.moving_average_forecast(
            marriages,
            moving_n,
            forecast_years_count
        )

        divorce_forecast = self.moving_average_forecast(
            divorces,
            moving_n,
            forecast_years_count
        )

        future_years = years.copy()

        last_year = years[-1]

        for i in range(1, forecast_years_count + 1):
            future_years.append(last_year + i)

        forecast_window = Toplevel(self.root)
        forecast_window.title("Прогноз")

        fig, ax = plt.subplots(figsize=(11, 6))

        # Браки (факт)
        ax.plot(
            years,
            marriages,
            color="green",
            marker='o',
            linewidth=2,
            label="Браки (факт)"
        )

        # Браки (прогноз)
        ax.plot(
            future_years,
            marriage_forecast,
            color="green",
            linestyle="--",
            marker='o',
            linewidth=2,
            label="Браки (прогноз)"
        )

        # Разводы (факт)
        ax.plot(
            years,
            divorces,
            color="red",
            marker='o',
            linewidth=2,
            label="Разводы (факт)"
        )

        # Разводы (прогноз)
        ax.plot(
            future_years,
            divorce_forecast,
            color="red",
            linestyle="--",
            marker='o',
            linewidth=2,
            label="Разводы (прогноз)"
        )

        # Выделение области прогноза
        ax.axvspan(
            years[-1],
            future_years[-1],
            color="gray",
            alpha=0.2
        )

        ax.set_title("Прогноз методом скользящей средней")
        ax.set_xlabel("Год")
        ax.set_ylabel("Количество")
        ax.grid()
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=forecast_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, forecast_window)
        toolbar.update()

    # ===================== Сброс =====================
    def clear_data(self):
        self.tree.delete(*self.tree.get_children())

        self.result_text.delete(1.0, END)

        self.data = None

        messagebox.showinfo("Сброс", "Таблица очищена")

root = Tk()
app = MarriageAnalyzer(root)
root.mainloop()