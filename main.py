import tkinter as tk
from crime_app import CrimeApp
from marriage_app import MarriageAnalyzer

def open_crime():
    # Создаем новое окно Toplevel поверх основного
    window = tk.Toplevel(root)
    window.title("Анализ преступности")
    # Передаем window как родительский элемент для Crime
    app = CrimeApp(window)

def open_marriage():
    window = tk.Toplevel(root)
    window.title("Анализ браков и разводов")
    # Передаем window как родительский элемент для Marriage
    app = MarriageAnalyzer(window)

root = tk.Tk()
root.title("Главное меню")
root.geometry("300x200")

btn1 = tk.Button(root, text="Данные о преступности", command=open_crime, height=3, width=30)
btn1.pack(pady=20)

btn2 = tk.Button(root, text="Данные о браках и разводах", command=open_marriage, height=3, width=30)
btn2.pack(pady=20)

root.mainloop()