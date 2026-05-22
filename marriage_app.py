import pandas as pd
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def read_xlsx_smart(path):
    try:
        return pd.read_excel(path)
    except Exception:
        raise Exception("Failed to load Excel file")


class MarriageAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Marriage and Divorce Analysis")
        self.root.geometry("1200x800")

        self.data = None

        self.create_ui()

    def create_ui(self):
        top_frame = Frame(self.root)
        top_frame.pack(pady=10)

        Button(
            top_frame,
            text="Import XLSX",
            command=self.load_file,
            width=20
        ).grid(row=0, column=0, padx=5)

        Button(
            top_frame,
            text="Show Graph",
            command=self.build_graphs,
            width=20
        ).grid(row=0, column=1, padx=5)

        Button(
            top_frame,
            text="Forecast",
            command=self.build_forecast,
            width=20
        ).grid(row=0, column=2, padx=5)

        Label(top_frame, text="N (moving average):").grid(row=0, column=3)

        self.n_entry = Entry(top_frame, width=10)
        self.n_entry.insert(0, "3")
        self.n_entry.grid(row=0, column=4, padx=5)

        self.tree = ttk.Treeview(self.root)
        self.tree.pack(fill=BOTH, expand=True, pady=10)

        self.result_text = Text(self.root, height=10)
        self.result_text.pack(fill=X, padx=10, pady=10)

    # Load data only
    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel Files", "*.xlsx")]
        )

        if not file_path:
            return

        try:
            self.data = read_xlsx_smart(file_path)
            self.show_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Show table only
    def show_table(self):
        self.tree.delete(*self.tree.get_children())

        self.tree["columns"] = list(self.data.columns)
        self.tree["show"] = "headings"

        for col in self.data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160)

        for _, row in self.data.iterrows():
            self.tree.insert("", END, values=list(row))

    # Analysis stays separate
    def analyze_data(self):
        result = ""

        male_marriage_age = self.data.groupby("Возраст_мужчин_брак")["Браки"].sum().idxmax()
        male_divorce_age = self.data.groupby("Возраст_мужчин_развод")["Разводы"].sum().idxmax()

        female_marriage_age = self.data.groupby("Возраст_женщин_брак")["Браки"].sum().idxmax()
        female_divorce_age = self.data.groupby("Возраст_женщин_развод")["Разводы"].sum().idxmax()

        result += f"Men most often married at age: {male_marriage_age}\n"
        result += f"Men most often divorced at age: {male_divorce_age}\n\n"
        result += f"Women most often married at age: {female_marriage_age}\n"
        result += f"Women most often divorced at age: {female_divorce_age}\n"

        self.result_text.delete(1.0, END)
        self.result_text.insert(END, result)

    # Graph button
    def build_graphs(self):
        if self.data is None:
            messagebox.showwarning("Error", "Load file first")
            return

        window = Toplevel(self.root)
        window.title("Graphs")

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(self.data["Год"], self.data["Браки"], marker='o', label="Marriages")
        ax.plot(self.data["Год"], self.data["Разводы"], marker='o', label="Divorces")

        ax.set_title("Marriages and Divorces by Year")
        ax.set_xlabel("Year")
        ax.set_ylabel("Count")
        ax.legend()
        ax.grid()

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        self.analyze_data()

    # Moving average
    def moving_average_forecast(self, values, n, steps):
        forecast = values.copy()

        for _ in range(steps):
            avg = sum(forecast[-n:]) / n
            forecast.append(avg)

        return forecast

    # Forecast button
    def build_forecast(self):
        if self.data is None:
            messagebox.showwarning("Error", "Load file first")
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
            window.title("Forecast")

            fig, ax = plt.subplots(figsize=(10, 5))

            ax.plot(years, marriages, label="Marriages")
            ax.plot(years, divorces, label="Divorces")

            ax.plot(future_years, marriage_forecast, "--o", label="Forecast marriages")
            ax.plot(future_years, divorce_forecast, "--o", label="Forecast divorces")

            ax.set_title("Moving Average Forecast")
            ax.set_xlabel("Year")
            ax.set_ylabel("Count")
            ax.legend()
            ax.grid()

            canvas = FigureCanvasTkAgg(fig, master=window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Error", str(e))


root = Tk()
app = MarriageAnalyzer(root)
root.mainloop()