import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import MaxNLocator


#Блок бизнес-логики и работы с данными
class CrimeDataAnalyzer:
    """Класс для загрузки данных и анализа статистики преступности."""

    def __init__(self, filepath):
        self.df = pd.read_csv(filepath)
        self.years = self.df.iloc[:, 0].values
        self.crime_columns = self.df.columns[1:]

    def get_dataframe(self):
        return self.df

    def analyze_decreases(self):
        """Вычисляет, какой вид преступности снизился больше/меньше всего."""
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

    def get_advanced_stats(self):
        """Расширенная статистика: среднее, медиана, общий % изменения."""
        stats = {}
        for crime in self.crime_columns:
            data = self.df[crime]
            stats[crime] = {
                "Среднее": round(data.mean(), 2),
                "Медиана": int(data.median()),
                "Изм. %": round(((data.iloc[-1] - data.iloc[0]) / data.iloc[0]) * 100, 2)
            }
        return stats


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


# Блок графического интерфейса
class CrimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ и прогнозирование преступности")
        self.root.geometry("1100x900")

        self.analyzer = None
        self._setup_ui()

    def _setup_ui(self):
        # Верхняя панель управления
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        btn_load = tk.Button(control_frame, text="Загрузить CSV", command=self.load_data)
        btn_load.pack(side=tk.LEFT, padx=5)

        # Кнопка экспорта
        btn_export = tk.Button(control_frame, text="Экспорт графика (PNG)", command=self.export_plot)
        btn_export.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="Год:").pack(side=tk.LEFT, padx=(15, 5))
        self.combo_year = ttk.Combobox(control_frame, values=["Все"], state="readonly", width=8)
        self.combo_year.current(0)
        self.combo_year.pack(side=tk.LEFT)
        self.combo_year.bind("<<ComboboxSelected>>", self._on_combo_select)

        tk.Label(control_frame, text="Окно скользящей (n):").pack(side=tk.LEFT, padx=(15, 5))
        self.entry_n = tk.Entry(control_frame, width=5)
        self.entry_n.insert(0, "3")
        self.entry_n.pack(side=tk.LEFT)

        tk.Label(control_frame, text="Лет для прогноза:").pack(side=tk.LEFT, padx=5)
        self.entry_forecast = tk.Entry(control_frame, width=5)
        self.entry_forecast.insert(0, "4")
        self.entry_forecast.pack(side=tk.LEFT)

        btn_plot = tk.Button(control_frame, text="Обновить график/прогноз", command=self.plot_data)
        btn_plot.pack(side=tk.LEFT, padx=15)

        # Разделение экрана на таблицу и графики
        main_frame = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        table_frame = tk.Frame(main_frame)
        main_frame.add(table_frame, minsize=300)

        self.tree = ttk.Treeview(table_frame, show='headings')
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.graph_frame = tk.Frame(main_frame)
        main_frame.add(self.graph_frame, minsize=500)

        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Область для статистики
        self.stats_label = tk.Label(self.root, text="Анализ снижения: данные не загружены", font=("Arial", 10, "bold"),
                                    fg="darkred")
        self.stats_label.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        stats_frame = tk.LabelFrame(self.root, text="Расширенная статистика", padx=10, pady=5)
        stats_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.stats_tree = ttk.Treeview(stats_frame, columns=("Type", "Mean", "Median", "Change"), show='headings',
                                       height=5)
        self.stats_tree.heading("Type", text="Тип преступления")
        self.stats_tree.heading("Mean", text="Среднее")
        self.stats_tree.heading("Median", text="Медиана")
        self.stats_tree.heading("Change", text="Изм. %")
        self.stats_tree.pack(fill=tk.X)

    def export_plot(self):
        if not self.analyzer:
            messagebox.showwarning("Внимание", "Сначала загрузите данные!")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if path:
            self.figure.savefig(path, dpi=300)
            messagebox.showinfo("Успех", f"График сохранен!")

    def _update_stats(self):
        # 1. Обновляем анализ снижения
        max_cr, min_cr = self.analyzer.analyze_decreases()
        if max_cr:
            self.stats_label.config(text=f"Больше всего снизилось: {max_cr} | Меньше всего снизилось: {min_cr}")
        else:
            self.stats_label.config(text="Снижения преступности за период не выявлено.")

        # 2. Обновляем таблицу статистики
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)

        stats = self.analyzer.get_advanced_stats()
        for crime, val in stats.items():
            self.stats_tree.insert("", tk.END, values=(crime, val["Среднее"], val["Медиана"], f"{val['Изм. %']}%"))

    def _on_tree_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item: return
        item_values = self.tree.item(selected_item[0], "values")
        try:
            selected_year = str(int(float(item_values[0])))
            if self.combo_year.get() != selected_year:
                self.combo_year.set(selected_year)
                self.plot_data()
        except ValueError:
            pass

    def _on_combo_select(self, event):
        selected_year = self.combo_year.get()
        if selected_year != "Все":
            for child in self.tree.get_children():
                val = self.tree.item(child, 'values')[0]
                if str(int(float(val))) == selected_year:
                    self.tree.selection_set(child)
                    self.tree.see(child)
                    break
        else:
            if self.tree.selection(): self.tree.selection_remove(self.tree.selection())
        self.plot_data()

    def load_data(self):
        filepath = filedialog.askopenfilename(filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        if not filepath: return
        try:
            self.analyzer = CrimeDataAnalyzer(filepath)
            self._update_table()
            self._update_stats()
            years_list = ["Все"] + list(map(str, self.analyzer.years))
            self.combo_year.config(values=years_list)
            self.combo_year.current(0)
            self.plot_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{e}")

    def _update_table(self):
        self.tree.delete(*self.tree.get_children())
        df = self.analyzer.get_dataframe()
        self.tree["columns"] = list(df.columns)
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor=tk.CENTER)
        for index, row in df.iterrows(): self.tree.insert("", tk.END, values=list(row))

    def plot_data(self):
        if not self.analyzer: return
        try:
            n_window = int(self.entry_n.get())
            forecast_years = int(self.entry_forecast.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Значения должны быть целыми числами.")
            return

        self.ax.clear()
        df = self.analyzer.get_dataframe()
        years = self.analyzer.years
        crime_columns = self.analyzer.crime_columns
        selected_year = self.combo_year.get()

        if selected_year == "Все":
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
            self.ax.legend()
            self.ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        else:
            year_int = int(selected_year)
            year_data = df[df.iloc[:, 0] == year_int].iloc[0, 1:]
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            bars = self.ax.bar(crime_columns, year_data.values, color=colors[:len(crime_columns)])
            self.ax.bar_label(bars, padding=3)
            self.ax.set_title(f"Статистика за {selected_year} год")

        self.ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        self.figure.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = CrimeApp(root)
    root.mainloop()