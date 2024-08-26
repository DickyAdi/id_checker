import tkinter as tk
from tkinter import messagebox, filedialog

from services.debitur_service import debitur_service
from model.debitur import debitur
from views.component import datatable
from . import IS_ALL_LOADED, DATATABLE_BATCH, DATATABLE_LOADED_ROWS

class datatable_controller:
    def __init__(self, datatable:datatable):
        self.model = debitur()
        self.datatable = datatable
        self.services = debitur_service()
    def show_all_data(self):
        global DATATABLE_BATCH, IS_ALL_LOADED, DATATABLE_LOADED_ROWS
        if IS_ALL_LOADED:
            return False
        else:
            total_record = self.model.get_total_records()
            fields = ['id', 'nik', 'nama', 'tanggal_lahir', 'tempat_lahir', 'alamat', 'nama_pasangan', 'nama_ibu_kandung', 'kolektibilitas', 'keterangan']
            success, data = self.model.get_all_records(limit=DATATABLE_BATCH, offset=DATATABLE_LOADED_ROWS)
            if success and data:
                for value in data:
                    values = list(value.values())
                    DATATABLE_LOADED_ROWS += 1
                    self.datatable.datatable.insert('', tk.END, values=values)
                IS_ALL_LOADED = DATATABLE_LOADED_ROWS >= total_record
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
        global IS_ALL_LOADED
        if self.datatable.datatable.yview()[1] >= .8 and not IS_ALL_LOADED:
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
                res, msg = self.services.delete_record_service(selected_row_key)
                if res:
                    messagebox.showinfo('Success', msg)
                    self.datatable.datatable.delete(selected_row_id)
                else:
                    messagebox.showerror('Fail', msg)
    def datatable_export_button_handler(self):
        if self.model.is_db_empty():
            res = messagebox.askokcancel('Dump?', 'Export semua data di database?')
            if res:
                possible_dir = filedialog.askdirectory()
                success, msg = self.services.dump_csv_service(possible_dir)
                if success:
                    messagebox.showinfo('Success', msg)
                else:
                    messagebox.showerror('Failed', msg)

