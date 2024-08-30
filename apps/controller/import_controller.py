import os
import csv
from typing import TYPE_CHECKING
from tkinter.ttk import Button
from tkinter import filedialog, messagebox

if TYPE_CHECKING:
    from views.component import entry_input
import controller
from model.debitur import debitur
from utils.utils import is_csv
class import_controller:
    def __init__(self, file_input:'entry_input', upload_button:Button):
        self.file_input = file_input
        self.upload_button = upload_button
        self.model = debitur()


    def upload_file_handler(self):
        file_types = [('Excel csv format file', '*.csv')]
        try:
            file_path = filedialog.askopenfilename(title='Select file', filetypes=file_types)
            self.file_input.set_value(file_path)
            if file_path:
                self.upload_button.configure(state='normal')
        except:
            messagebox.showerror('Error', 'Terjadi error!')

    def upload_button_handler(self):
        possible_file = self.file_input.get_value()
        response = messagebox.askokcancel('Continue?', f'Insert data dari {possible_file}?')
        if response:
            if is_csv(possible_file):
                result = self.model.read_csv(possible_file)
                if result['success']:
                    res, flag, msg = self.model.batch_insert_records(result['validated'])
                    if res:
                        total_inserted = self.model.get_total_records()
                        controller.IS_ALL_LOADED = controller.DATATABLE_LOADED_ROWS >= total_inserted
                        messagebox.showinfo('Succeed', f"{result['total_rows']} data berhasil di insert!")
                        self.file_input.clear_value()
                        self.upload_button.config(state='disabled')
                    else:
                        if flag == 'IntegrityError':
                            messagebox.showerror('Failed', f'Terdapat data duplikat di dalam database.\nDetail: {msg}')
                        elif flag == 'UnexpectedError':
                            messagebox.showerror('Failed', f'Unexpected error!\nDetail: {msg}')
                else:
                    messagebox.showerror('Failed', result['msg'])
            else:
                messagebox.showerror('Error', 'Pastikan file yang di-upload adalah file csv')