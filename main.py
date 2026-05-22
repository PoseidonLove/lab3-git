import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import MaxNLocator  # Добавлен импорт для исправления дробных годов


# --- Блок бизнес-логики и работы с данными ---

class CrimeDataAnalyzer:
    """Класс для загрузки данных и анализа статистики преступности."""

    def __init__(self, filepath):
        self.df = pd.read_csv(filepath)
        self.years = self.df.iloc[:, 0].values
        self.crime_columns = self.df.columns[1:]

    def get_dataframe(self):
        return self.df

    def analyze_decreases(self):
        decreases = {}
        for crime in self.crime_columns:
            start_value = self.df[crime].iloc[0]
            end_value = self.df[crime].iloc[-1]
            decrease = start_value - end_value
            decreases[crime] = decrease

        actual_decreases = {k: v for k, v in decreases.items() if v > 0}
        if not actual_decreases:
            return None, None

        max_decrease_crime = max(actual_decreases, key=actual_decreases.get)
        min_decrease_crime = min(actual_decreases, key=actual_decreases.get)
        return max_decrease_crime, min_decrease_crime


class Forecaster:
    """Класс для реализации алгоритмов прогнозирования."""

    @staticmethod
    def moving_average_extrapolation(data_series, n_window, forecast_periods):
        history = list(data_series)
        predictions = []
        for _ in range(forecast_periods):
            recent_data = history[-n_window:]
            next_val = sum(recent_data) / n_window
            predictions.append(next_val)
            history.append(next_val)
        return predictions


# --- Блок графического интерфейса ---

class CrimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ и прогнозирование преступности (Вар. 13)")
        self.root.geometry("1100x700")

        self.analyzer = None
        self._setup_ui()

    def _setup_ui(self):
        # Верхняя панель управления
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        btn_load = tk.Button(control_frame, text="Загрузить CSV", command=self.load_data)
        btn_load.pack(side=tk.LEFT, padx=5)

        # --- НОВОЕ: Выпадающий список для выбора года ---
        tk.Label(control_frame, text="Год:").pack(side=tk.LEFT, padx=(15, 5))
        self.combo_year = ttk.Combobox(control_frame, values=["Все"], state="readonly", width=8)
        self.combo_year.current(0)
        self.combo_year.pack(side=tk.LEFT)

        tk.Label(control_frame, text="Окно скользящей (n):").pack(side=tk.LEFT, padx=(15, 5))
        self.entry_n = tk.Entry(control_frame, width=5)
        self.entry_n.insert(0, "3")
        self.entry_n.pack(side=tk.LEFT)

        tk.Label(control_frame, text="Лет для прогноза:").pack(side=tk.LEFT, padx=5)
        self.entry_forecast = tk.Entry(control_frame, width=5)
        self.entry_forecast.insert(0, "4")
        self.entry_forecast.pack(side=tk.LEFT)

        btn_plot = tk.Button(control_frame, text="Построить график", command=self.plot_data)
        btn_plot.pack(side=tk.LEFT, padx=15)

        self.lbl_stats = tk.Label(control_frame, text="Статистика: Данные не загружены", fg="blue", justify=tk.LEFT)
        self.lbl_stats.pack(side=tk.LEFT, padx=15)

        # Разделение экрана на таблицу (слева) и графики (справа)
        main_frame = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм для таблицы
        table_frame = tk.Frame(main_frame)
        main_frame.add(table_frame, minsize=300)

        self.tree = ttk.Treeview(table_frame, show='headings')
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Фрейм для графиков
        self.graph_frame = tk.Frame(main_frame)
        main_frame.add(self.graph_frame, minsize=600)

        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_data(self):
        filepath = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if not filepath:
            return

        try:
            self.analyzer = CrimeDataAnalyzer(filepath)
            self._update_table()
            self._update_stats()

            years_list = ["Все"] + list(map(str, self.analyzer.years))
            self.combo_year.config(values=years_list)
            self.combo_year.current(0)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{e}")

    def _update_table(self):
        self.tree.delete(*self.tree.get_children())
        df = self.analyzer.get_dataframe()

        self.tree["columns"] = list(df.columns)
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor=tk.CENTER)

        for index, row in df.iterrows():
            self.tree.insert("", tk.END, values=list(row))

    def _update_stats(self):
        max_cr, min_cr = self.analyzer.analyze_decreases()
        if max_cr and min_cr:
            stat_text = (f"Снизилось больше всего: {max_cr}\n"
                         f"Снизилось меньше всего: {min_cr}")
        else:
            stat_text = "Снижения преступности не выявлено."

        self.lbl_stats.config(text=stat_text)

    def plot_data(self):
        if not self.analyzer:
            messagebox.showwarning("Внимание", "Сначала загрузите данные.")
            return

        try:
            n_window = int(self.entry_n.get())
            forecast_years = int(self.entry_forecast.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Значения 'n' и 'лет для прогноза' должны быть целыми числами.")
            return

        self.ax.clear()
        df = self.analyzer.get_dataframe()
        years = self.analyzer.years
        crime_columns = self.analyzer.crime_columns

        selected_year = self.combo_year.get()

        if selected_year == "Все":
            # --- ЛОГИКА 1: Линейный график для всех лет с прогнозом ---
            last_year = int(years[-1])
            future_years = [last_year + i for i in range(1, forecast_years + 1)]

            for crime in crime_columns:
                historical_data = df[crime].values
                line, = self.ax.plot(years, historical_data, marker='o', label=crime)

                predictions = Forecaster.moving_average_extrapolation(historical_data, n_window, forecast_years)
                pred_years = [years[-1]] + future_years
                pred_values = [historical_data[-1]] + predictions
                self.ax.plot(pred_years, pred_values, linestyle='--', color=line.get_color(), marker='x')

            self.ax.set_title("Динамика преступности и прогноз")
            self.ax.set_xlabel("Год")
            self.ax.set_ylabel("Количество зарегистрированных случаев")
            self.ax.legend()

            # --- ИСПРАВЛЕНИЕ ДРОБЕЙ: Принудительно делаем шаги по оси X целыми числами ---
            self.ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        else:
            # --- ЛОГИКА 2: Столбчатая диаграмма для одного выбранного года ---
            year_int = int(selected_year)
            # Извлекаем строку с нужным годом
            year_data = df[df.iloc[:, 0] == year_int].iloc[0, 1:]

            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Цвета из matplotlib по умолчанию
            bars = self.ax.bar(crime_columns, year_data.values, color=colors[:len(crime_columns)])

            # Добавляем цифры прямо над столбиками для наглядности
            self.ax.bar_label(bars, padding=3)

            self.ax.set_title(f"Статистика преступности за {selected_year} год")
            self.ax.set_xlabel("Вид преступления")
            self.ax.set_ylabel("Количество случаев")

        self.ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        self.figure.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = CrimeApp(root)
    root.mainloop()