import os
import csv
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog

from model.debitur import debitur
from views.component import datatable
import controller

class datatable_controller:
    def __init__(self, datatable:datatable):
        self.model = debitur()
        self.datatable = datatable

    def show_all_data(self):
        if controller.IS_ALL_LOADED:
            return False
        else:
            total_record = self.model.get_total_records()
            success, data = self.model.get_all_records(limit=controller.DATATABLE_BATCH, offset=controller.DATATABLE_LOADED_ROWS)
            if success and data:
                for value in data:
                    values = list(value.values())
                    controller.DATATABLE_LOADED_ROWS += 1
                    self.datatable.datatable.insert('', tk.END, values=values)
                controller.IS_ALL_LOADED = controller.DATATABLE_LOADED_ROWS >= total_record
                return True
            else:
                return False

    def lazy_show_data(self, event):
        self.datatable.delete_button.configure(state='disabled')
        if self.model.is_db_empty():
            self.datatable.export_button.configure(state='disabled')
        else:
            self.datatable.export_button.configure(state='normal')
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, 'text')
        if tab_text == 'View & export data':
            if len(self.datatable.datatable.get_children()) == 0:
                if not self.show_all_data():
                    messagebox.showerror('Error', 'Database kosong!')

    def on_scroll_lazy_load(self, event):
        if self.datatable.datatable.yview()[1] >= .8 and not controller.IS_ALL_LOADED:
            self.show_all_data()

    def datatable_row_click_handler(self, event):
        selected = self.datatable.datatable.focus()
        selected_row = self.datatable.datatable.item(selected)['values']
        if selected_row:
            self.datatable.delete_button.configure(state='normal')

    def datatable_delete_button_handler(self):
        selected = self.datatable.datatable.focus()
        selected_row_key = self.datatable.datatable.item(selected)['values'][1]
        selected_row_id = self.datatable.datatable.selection()[0]
        if selected_row_key:
            res = messagebox.askokcancel('Delete', f'Delete data dengan {selected_row_key}?')
            if res:
                res = self.model.delete_record(selected_row_key)
                if res:
                    if controller.DATATABLE_LOADED_ROWS > 0:
                        controller.DATATABLE_LOADED_ROWS -= 1
                    messagebox.showinfo('Success', f'Data dengan {selected_row_key} telah di hapus')
                    self.datatable.datatable.delete(selected_row_id)
                else:
                    messagebox.showerror('Fail', 'Telah terjadi error!')

    def datatable_export_button_handler(self):
        if not self.model.is_db_empty():
            res = messagebox.askokcancel('Dump?', 'Export semua data di database?')
            if res:
                possible_dir = filedialog.askdirectory()
                success, msg = self.dump_to_csv(possible_dir)
                if success:
                    messagebox.showinfo('Success', msg)
                else:
                    messagebox.showerror('Failed', msg)

    def dump_to_csv(self, possible_dir):
        possible_dir = Path(possible_dir)
        file_name = f"{datetime.now().strftime('%d-%m-%Y')}_database_dump.csv"
        column_name = ['id', 'nik', 'nama', 'tanggal_lahir', 'tempat_lahir', 'alamat', 'nama_ibu_kandung', 'nama_pasangan', 'kolektibilitas', 'keterangan', 'created_at', 'last_edit']
        if possible_dir.is_dir():
            success, data = self.model.get_all_records()
            if success:
                export_dir = os.path.join(possible_dir, file_name)
                try:
                    with open(os.path.join(controller.abs_path, export_dir), 'w', newline='') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=column_name)
                        writer.writeheader()
                        writer.writerows(data)
                except IOError as e:
                    return (False, f'Error pada saat process dumping csv {e}')
                except Exception as e:
                    return (False, f'Unexpected error {e}')
                else:
                    return (True, f'Data berhasil di export dengan nama {file_name} di folder {possible_dir}')
        else:
            return (False, f'{str(possible_dir)} bukan merupakan sebuah direktori!')