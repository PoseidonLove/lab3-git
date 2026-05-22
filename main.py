import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


# --- Блок бизнес-логики и работы с данными (Инкапсуляция логики) ---

class CrimeDataAnalyzer:
    """Класс для загрузки данных и анализа статистики преступности."""

    def __init__(self, filepath):
        # Читаем CSV файл. Ожидается, что первый столбец - 'Год', остальные - виды преступлений
        self.df = pd.read_csv(filepath)
        self.years = self.df.iloc[:, 0].values
        self.crime_columns = self.df.columns[1:]

    def get_dataframe(self):
        return self.df

    def analyze_decreases(self):
        """Вычисляет, какой вид преступности снизился больше, а какой меньше всего."""
        decreases = {}

        for crime in self.crime_columns:
            # Разница между первым годом (15 лет назад) и последним годом
            start_value = self.df[crime].iloc[0]
            end_value = self.df[crime].iloc[-1]

            # Нас интересует именно снижение, поэтому считаем (Начало - Конец)
            decrease = start_value - end_value
            decreases[crime] = decrease

        # Фильтруем только те преступления, которые реально снизились (значение > 0)
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
        """
        Прогнозирование методом скользящей средней.
        Каждое новое значение - это среднее n_window предыдущих значений.
        """
        history = list(data_series)
        predictions = []

        for _ in range(forecast_periods):
            # Берем последние n_window элементов
            recent_data = history[-n_window:]
            next_val = sum(recent_data) / n_window
            predictions.append(next_val)
            # Добавляем прогноз в историю для расчета следующих шагов
            history.append(next_val)

        return predictions


# --- Блок графического интерфейса ---

class CrimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ и прогнозирование преступности (Вар. 13)")
        self.root.geometry("1000x700")

        self.analyzer = None

        self._setup_ui()

    def _setup_ui(self):
        # Верхняя панель управления
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        btn_load = tk.Button(control_frame, text="Загрузить CSV", command=self.load_data)
        btn_load.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="Окно скользящей средней (n):").pack(side=tk.LEFT, padx=5)
        self.entry_n = tk.Entry(control_frame, width=5)
        self.entry_n.insert(0, "3")
        self.entry_n.pack(side=tk.LEFT)

        tk.Label(control_frame, text="Лет для прогноза:").pack(side=tk.LEFT, padx=5)
        self.entry_forecast = tk.Entry(control_frame, width=5)
        self.entry_forecast.insert(0, "5")
        self.entry_forecast.pack(side=tk.LEFT)

        btn_plot = tk.Button(control_frame, text="Построить графики и прогноз", command=self.plot_data)
        btn_plot.pack(side=tk.LEFT, padx=15)

        self.lbl_stats = tk.Label(control_frame, text="Статистика: Данные не загружены", fg="blue")
        self.lbl_stats.pack(side=tk.LEFT, padx=15)

        # Разделение экрана на таблицу (слева) и графики (справа)
        main_frame = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм для таблицы
        table_frame = tk.Frame(main_frame)
        main_frame.add(table_frame, minsize=300)

        # Настройка Treeview для таблицы
        self.tree = ttk.Treeview(table_frame, show='headings')
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Фрейм для графиков
        self.graph_frame = tk.Frame(main_frame)
        main_frame.add(self.graph_frame, minsize=500)

        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Добавление панели инструментов matplotlib (масштабирование, экспорт)
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
            messagebox.showinfo("Успех", "Данные успешно загружены.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{e}")

    def _update_table(self):
        """Отображает загруженные данные в таблице."""
        # Очистка старых данных
        self.tree.delete(*self.tree.get_children())
        df = self.analyzer.get_dataframe()

        # Настройка колонок
        self.tree["columns"] = list(df.columns)
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)

        # Вставка строк
        for index, row in df.iterrows():
            self.tree.insert("", tk.END, values=list(row))

    def _update_stats(self):
        """Выводит статистику по снижению преступности."""
        max_cr, min_cr = self.analyzer.analyze_decreases()
        if max_cr and min_cr:
            stat_text = (f"Снизилось больше всего: {max_cr}\n"
                         f"Снизилось меньше всего: {min_cr}")
        else:
            stat_text = "Снижения преступности за период не выявлено."

        self.lbl_stats.config(text=stat_text)

    def plot_data(self):
        """Построение исторических данных и прогноза."""
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

        # Генерация годов для прогноза
        last_year = int(years[-1])
        future_years = [last_year + i for i in range(1, forecast_years + 1)]

        # Построение графиков для каждого вида преступности
        for crime in crime_columns:
            historical_data = df[crime].values

            # Строим исторические данные
            line, = self.ax.plot(years, historical_data, marker='o', label=crime)

            # Рассчитываем прогноз
            predictions = Forecaster.moving_average_extrapolation(historical_data, n_window, forecast_years)

            # Строим прогноз (тем же цветом, но пунктиром, чтобы выделить)
            # Для соединения линий добавим последнюю историческую точку
            pred_years = [years[-1]] + future_years
            pred_values = [historical_data[-1]] + predictions

            self.ax.plot(pred_years, pred_values, linestyle='--', color=line.get_color(), marker='x')

        self.ax.set_title("Динамика преступности и прогноз")
        self.ax.set_xlabel("Год")
        self.ax.set_ylabel("Количество зарегистрированных случаев")
        self.ax.legend()
        self.ax.grid(True)

        self.figure.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = CrimeApp(root)
    root.mainloop()