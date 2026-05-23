import pandas as pd
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


def read_xlsx(path):
    return pd.read_excel(path)


class MarriageAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ браков и разводов")
        self.root.geometry("1350x900")

        self.data = None
        self.filtered = None

        self.create_ui()

    # ================= UI =================
    def create_ui(self):
        top = Frame(self.root)
        top.pack(fill=X, pady=5)

        Button(top, text="Открыть файл", command=self.load_file, width=18).pack(side=LEFT, padx=5)
        Button(top, text="График", command=self.build_graph, width=18).pack(side=LEFT, padx=5)
        Button(top, text="Прогноз", command=self.build_forecast, width=18).pack(side=LEFT, padx=5)

        Label(top, text="N:").pack(side=LEFT)
        self.n_scale = Scale(top, from_=2, to=10, orient=HORIZONTAL)
        self.n_scale.set(3)
        self.n_scale.pack(side=LEFT)

        # таблица
        self.tree = ttk.Treeview(self.root)
        self.tree.pack(fill=BOTH, expand=True)

        # вывод анализа
        self.text = Text(self.root, height=10)
        self.text.pack(fill=X)

    # ================= LOAD =================
    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if not path:
            return

        self.data = pd.read_excel(path)
        self.show_table()

    # ================= TABLE =================
    def show_table(self):
        self.tree.delete(*self.tree.get_children())

        self.tree["columns"] = list(self.data.columns)
        self.tree["show"] = "headings"

        for c in self.data.columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=140)

        for _, row in self.data.iterrows():
            self.tree.insert("", END, values=list(row))

    # ================= AGE ANALYSIS =================
    def analyze_ages(self):
        df = self.data

        male_marriage = df.groupby("Возраст_мужчин_брак")["Браки"].sum().idxmax()
        male_divorce = df.groupby("Возраст_мужчин_развод")["Разводы"].sum().idxmax()

        female_marriage = df.groupby("Возраст_женщин_брак")["Браки"].sum().idxmax()
        female_divorce = df.groupby("Возраст_женщин_развод")["Разводы"].sum().idxmax()

        result = ""
        result += f"Мужчины чаще женились в возрасте: {male_marriage}\n"
        result += f"Мужчины чаще разводились в возрасте: {male_divorce}\n\n"
        result += f"Женщины чаще выходили замуж в возрасте: {female_marriage}\n"
        result += f"Женщины чаще разводились в возрасте: {female_divorce}\n"

        self.text.delete(1.0, END)
        self.text.insert(END, result)

    # ================= GRAPH =================
    def build_graph(self):
        if self.data is None:
            return

        self.analyze_ages()

        df = self.data

        win = Toplevel(self.root)
        win.title("График")

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(df["Год"], df["Браки"], label="Браки")
        ax.plot(df["Год"], df["Разводы"], label="Разводы")

        ax.set_title("Динамика браков и разводов")
        ax.set_xlabel("Год")
        ax.set_ylabel("Количество")
        ax.legend()
        ax.grid()

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        NavigationToolbar2Tk(canvas, win).update()

    # ================= MOVING AVERAGE =================
    def moving_average(self, values, n):
        result = values.copy()

        for _ in range(5):
            result.append(sum(result[-n:]) / n)

        return result

    # ================= FORECAST =================
    def build_forecast(self):
        if self.data is None:
            return

        n = self.n_scale.get()

        df = self.data

        years = df["Год"].tolist()
        marriages = df["Браки"].tolist()

        forecast = self.moving_average(marriages, n)

        future_years = years.copy()
        last_year = years[-1]

        for i in range(1, 6):
            future_years.append(last_year + i)

        win = Toplevel(self.root)
        win.title("Прогноз")

        fig, ax = plt.subplots(figsize=(10, 5))

        # реальные данные
        ax.plot(years, marriages, label="Факт")

        # прогноз
        ax.plot(future_years, forecast, "--o", label="Прогноз")

        # закрашивание прогноза
        ax.axvspan(years[-1], future_years[-1], color="gray", alpha=0.2)

        ax.set_title("Прогноз методом скользящей средней")
        ax.set_xlabel("Год")
        ax.set_ylabel("Количество")
        ax.legend()
        ax.grid()

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        NavigationToolbar2Tk(canvas, win).update()


root = Tk()
app = MarriageAnalyzer(root)
root.mainloop()