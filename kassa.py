import pickle
import datetime
import pandas as pd
import random
from tkinter import *
from tkinter import ttk
from item2item import *

ITEM_SET = []  # лист с товарами

model = pickle.load(open('D:\\JupyterNotebook\\project\\hacks_ai_dsc\\model.pkl', 'rb'))
device_id = [352398089623724, 352398089695367, 352398089696829, 352398089703369]
random_device = random.choice(device_id)
receipt_id = [10428823398, 11837151446, 11853638071, 11952886649]
random_receipt_id = random.choice(receipt_id)


def compress_receipt(data: pd.Series) -> pd.DataFrame:
    receipt = data.groupby('receipt_id', as_index=False).agg(
        {'local_date': 'first', 'device_id': 'first', 'item_id': set})

    return receipt


# удаление выделенного элемента
def delete_id():
    global ITEM_SET
    selection = item_id_listbox.curselection()  # выбираем элемент в Listbox
    item_id_listbox.delete(selection[0])  # удаляем элемент в Listbox по индексу
    ITEM_SET.pop(selection[0])  # удаляем элемент в ITEM_SET по индексу
    dt_now = datetime.datetime.now()
    features = pd.DataFrame({'local_date': [dt_now] * len(ITEM_SET), 'item_id': [ITEM_SET],
                             'device_id': [random_device] * len(ITEM_SET),
                             'receipt_id': [random_receipt_id] * len(ITEM_SET)})
    predict_item_id = model.predict(compress_receipt(features))[0]  # сюда надо пихнуть функцию для предсказания
    res = "Рекомендуем: {}".format(predict_item_id)
    lbl.configure(text=res)


# добавление нового элемента
def add_id():
    global ITEM_SET
    new_item_id = item_id_entry.get()  # вводим id товара
    ITEM_SET.append(int(new_item_id))  # добавляем его в список
    dt_now = datetime.datetime.now()
    features = pd.DataFrame({'local_date': [dt_now] * len(ITEM_SET), 'item_id': ITEM_SET,
                             'device_id': [random_device] * len(ITEM_SET),
                             'receipt_id': [random_receipt_id] * len(ITEM_SET)})
    item_id_listbox.insert(END, new_item_id)  # добавляем его в Listbox
    predict_item_id = model.predict(compress_receipt(features))[0]  # сюда надо пихнуть функцию для предсказания
    res = "Рекомендуем: {}".format(predict_item_id)
    lbl.configure(text=res)


root = Tk()
root.title("Касса")
root.geometry("450x300")
root.columnconfigure(index=0, weight=4)
root.columnconfigure(index=1, weight=1)
root.rowconfigure(index=0, weight=1)
root.rowconfigure(index=1, weight=3)
root.rowconfigure(index=2, weight=1)

lbl = Label(root, text="Рекомендуем: ")
lbl.grid(column=0, row=0)

# текстовое поле и кнопка для добавления в список
item_id_entry = ttk.Entry()
item_id_entry.grid(column=1, row=0, padx=6, pady=6, sticky=EW)
ttk.Button(text="Добавить", command=add_id).grid(column=2, row=0, padx=6, pady=6)

# создаем список
item_id_listbox = Listbox()
item_id_listbox.grid(row=1, column=0, columnspan=3, sticky=EW, padx=5, pady=5)
#
# кнопка для удаления в списоке
ttk.Button(text="Удалить", command=delete_id).grid(row=2, column=1, padx=5, pady=5)
root.mainloop()

# получаем множество товаров
# ITEM_SET = set(ITEM_SET)
# print(ITEM_SET)
# ITEM_SET.clear()
