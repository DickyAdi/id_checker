import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
# import os
# import sys
# from PIL import ImageTk
import sv_ttk

from helper import processing
import sv_ttk.theme

def main():
    def edit_button_handler():
        fields = [
            (nik, 'nik', nik_reset_bg, nik_label, nik_label_error),
            (nama, 'nama', nama_reset_bg, nama_label, nama_label_error),
            (tanggal_lahir, 'tanggal_lahir', tanggal_lahir_reset_bg, tanggal_lahir_label, tanggal_lahir_label_error),
            (tempat_lahir, 'tempat_lahir', tempat_lahir_reset_bg, tempat_lahir_label, tempat_lahir_label_error),
            (alamat, 'alamat', alamat_reset_bg, alamat_label, alamat_label_error),
            (nama_ibu_kandung, 'nama_ibu_kandung', nama_ibu_kandung_reset_bg, nama_ibu_kandung_label, nama_ibu_kandung_label_error),
            (nama_pasangan, 'nama_pasangan', nama_pasangan_reset_bg, nama_pasangan_label, nama_pasangan_label_error),
            (kolektibilitas, 'kolektibilitas', kolektibilitas_reset_bg, kolektibilitas_label, kolektibilitas_label_error),
            (keterangan, 'keterangan', keterangan_reset_bg, keterangan_label, keterangan_label_error)
        ]
        listVar = [nama, tanggal_lahir, tempat_lahir, alamat, nama_pasangan, kolektibilitas, keterangan]
        if editButton['text'] == 'Insert':
            if processing.validate_submit(fields):
                response = processing.insert_process(fields)
                if response:
                    messagebox.showinfo('Success', 'Data sukses di input')
                    processing.clear_all_input([nik, nama, tanggal_lahir, tempat_lahir, alamat, nama_pasangan, nama_ibu_kandung, kolektibilitas, keterangan])
                    [var.configure(state='disabled') for var in listVar]
                    editButton.configure(text='Edit', state='disable')
                else:
                    messagebox.showerror('Failed', 'Data tidak di input, terdapat error!')
            else:
                messagebox.showerror('Invalid input', 'Cek ulang data!')
        elif editButton['text'] == 'Edit':
            if processing.validate_submit(fields):
                response = processing.edit_process(fields)
                if response:
                    messagebox.showinfo('Success', 'Data telah di edit')
                    processing.clear_all_input([nik, nama, tanggal_lahir, tempat_lahir, alamat, nama_pasangan, nama_ibu_kandung, kolektibilitas, keterangan])
                    [var.configure(state='disabled') for var in listVar]
                    editButton.configure(state='disabled')
                else:
                    messagebox.showerror('Failed', 'Data tidak ter-edit, terdapat error!')
            else:
                messagebox.showerror('Invalid input', 'Cek ulang data!')

    def check_button_handler():
        if processing.validate_input(nik, 'nik', nik_reset_bg, nik_label, nik_label_error):
            processing.processEntry(nik, nama, tanggal_lahir, tempat_lahir, alamat, nama_pasangan, nama_ibu_kandung, keterangan, kolektibilitas
                                , nik_entry, nama_entry, tanggal_lahir_entry, tempat_lahir_entry, alamat_entry, nama_pasangan_entry, nama_ibu_kandung_entry, editButton, printButton)

    def focus_out_handler(var, var_name, reset_bg, var_label,error_label):
        processing.validate_input(var, var_name, reset_bg, var_label, error_label)

    def upload_button_handler():
        # processing.upload_file_handler(file_upload_entry)
        possible_file = Path(file_upload_entry.get()).name
        response = messagebox.askokcancel('Continue?', f'Insert data dari file {possible_file}?')
        if response:
            success, msg = processing.upload_process(file_upload_entry)
            if success:
                messagebox.showinfo('Succeed', message=msg)
                upload_button.configure(state='disable')
                file_upload_entry.set('')
            else:
                messagebox.showerror('Error', message=msg)

    def lazy_show_data(event):
        delete_button.configure(state='disabled') #disable delete button each time switching to this tab
        if not processing.is_db_empty():
            export_button.configure(state='normal')
        else:
            export_button.configure(state='disabled')
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, 'text')
        if tab_text == 'View and delete data':
            if len(view_data_list.get_children()) == 0:
                if not processing.show_all_data(view_data_list):
                    messagebox.showerror('Error', 'Database kosong!')

    def on_scroll_lazy_load(event, tree:ttk.Treeview):
        if tree.yview()[1] >= 0.8 and not processing.ALL_DATA_LOADED:
            processing.show_all_data(tree)

    def delete_button_handler():
        selected = view_data_list.focus()
        selected_row_key = view_data_list.item(selected)['values'][0]
        selected_row_id = view_data_list.selection()[0]
        if selected_row_key:
            res = messagebox.askokcancel('Delete', f'Delete data dengan NIK {selected_row_key}?')
            if res:
                res, msg = processing.delete_tree_row(selected_row_key)
                if res:
                    messagebox.showinfo('Success', msg)
                    view_data_list.delete(selected_row_id)
                else:
                    messagebox.showerror('Fail', msg)

    def export_button_handler():
        if not processing.is_db_empty():
            res = messagebox.askokcancel('Dump?', 'Export semua data di database ke file csv?')
            if res:
                possible_directory = filedialog.askdirectory()
                con, msg = processing.dump_to_csv(possible_directory)
                if con:
                    messagebox.showinfo('Success', msg)
                else:
                    messagebox.showerror('Failed', msg)


    def tree_row_click_handler(event):
        selected = view_data_list.focus()
        selected_row = view_data_list.item(selected)['values']
        if selected_row:
            delete_button.configure(state='normal')

    def print_button_handler():
        possible_path = filedialog.askdirectory()
        if possible_path:
            res, msg = processing.print_pdf( nik_entry.get(), possible_path)
            if res:
                messagebox.showinfo('Success', msg)
            else:
                messagebox.showerror('Failed', msg)
            printButton.configure(state='disabled')
    
    # if getattr(sys, 'frozen', False):
    #     abs_path = sys._MEIPASS
    # else:
    #     abs_path = os.path.abspath('.')
    root = tk.Tk()
    # root.withdraw()
    width = 650
    height = 620
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = int((screen_width/2) - (width/2))
    y = int((screen_height/2) - (height/2))
    root.geometry(f'{width}x{height}+{x}+{y}')
    root.minsize(width, height)
    root.title("ID Checker")
    corporate_logo = processing.to_imagetk('apps/assets/img/logo_BJA_PNG(resize).png')
    corporate_logo_label = ttk.Label(root, image=corporate_logo)
    corporate_logo_label.image = corporate_logo
    corporate_logo_label.grid(row=0, column=0, sticky='n', pady=10, padx=15)

    notebook = ttk.Notebook(root)
    notebook.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)

    # tab1 = ttk.Frame(notebook)
    # notebook.add(tab1, text='data')

    input_form_frame = ttk.Frame(notebook, padding=10)
    notebook.add(input_form_frame, text='data')
    # input_form_frame.grid(row=0, column=0, columnspan=2, sticky='nsew')

    nik_label = tk.Label(input_form_frame, text='NIK*')
    nik_label_error = tk.Label(input_form_frame, text='', font=('TkDefaultFont', 8), foreground='red')
    nik_label.grid(row=0, column=0, sticky='w', columnspan=2)
    nik_label_error.grid(row=0, column=0)
    nik_entry = tk.StringVar()
    nik =ttk.Entry(input_form_frame, textvariable=nik_entry)
    nik_reset_bg = nik_label.cget('foreground')
    nik.bind('<FocusOut>', lambda event, reset_bg=nik_reset_bg, var=nik, var_name='nik', error_label=nik_label_error, var_label=nik_label : focus_out_handler(var, var_name, reset_bg, var_label, error_label))
    nik.grid(row=1, column=0, sticky='ew')


    nama_label =ttk.Label(input_form_frame, text='Nama*')
    nama_label_error = tk.Label(input_form_frame, text='', font=('TkDefaultFont', 8), foreground='red')
    nama_label.grid(row=2, column=0, sticky='w')
    nama_label_error.grid(row=2, column=0)
    nama_entry = tk.StringVar()
    nama =ttk.Entry(input_form_frame, textvariable=nama_entry, state='disabled')
    nama_reset_bg = nama_label.cget('foreground')
    nama.bind('<FocusOut>', lambda event, reset_bg=nama_reset_bg, var=nama, var_name='nama', error_label=nama_label_error, var_label=nama_label : focus_out_handler(var, var_name, reset_bg, var_label, error_label))
    nama.grid(row=3, column=0, sticky='ew')

    tanggal_lahir_label =ttk.Label(input_form_frame, text='Tanggal lahir(dd-mm-YYYY)*')
    tanggal_lahir_label_error = ttk.Label(input_form_frame, text='', font=('TkDefaultFont', 8), foreground='red')
    tanggal_lahir_label.grid(row=4, column=0, sticky='w')
    tanggal_lahir_label_error.grid(row=4, column=0)
    tanggal_lahir_entry = tk.StringVar()
    tanggal_lahir =ttk.Entry(input_form_frame, textvariable=tanggal_lahir_entry, state='disabled')
    tanggal_lahir_reset_bg = tanggal_lahir.cget('foreground')
    tanggal_lahir.bind('<FocusOut>', lambda event, reset_bg=tanggal_lahir_reset_bg, var=tanggal_lahir, var_name='tanggal_lahir', error_label=tanggal_lahir_label_error, var_label=tanggal_lahir_label : focus_out_handler(var, var_name, reset_bg, var_label, error_label))
    tanggal_lahir.grid(row=5, column=0, sticky='ew')

    tempat_lahir_label =ttk.Label(input_form_frame, text='Tempat lahir*')
    tempat_lahir_label_error = ttk.Label(input_form_frame, text='', font=('TkDefaultFont', 8), foreground='red')
    tempat_lahir_label.grid(row=4, column=1, sticky='w', padx=4)
    tempat_lahir_label_error.grid(row=4, column=1, padx=4)
    tempat_lahir_entry = tk.StringVar()
    tempat_lahir =ttk.Entry(input_form_frame, textvariable=tempat_lahir_entry, state='disabled')
    tempat_lahir_reset_bg = tempat_lahir.cget('foreground')
    tempat_lahir.bind('<FocusOut>', lambda event, reset_bg = tempat_lahir_reset_bg, var=tempat_lahir, var_name='tempat_lahir', error_label=tempat_lahir_label_error, var_label=tempat_lahir_label : focus_out_handler(var, var_name, reset_bg, var_label, error_label))
    tempat_lahir.grid(row=5, column=1, sticky='ew', padx=4)

    alamat_label =ttk.Label(input_form_frame, text='Alamat*')
    alamat_label_error = ttk.Label(input_form_frame, text='', font=('TkDefaultFont', 8), foreground='red')
    alamat_label.grid(row=6, column=0, sticky='w')
    alamat_label_error.grid(row=6, column=0)
    alamat_entry = tk.StringVar()
    alamat =ttk.Entry(input_form_frame, textvariable=alamat_entry, state='disabled')
    alamat_reset_bg = alamat.cget('foreground')
    alamat.bind('<FocusOut>', lambda event, reset_bg = alamat_reset_bg, var=alamat, var_name='alamat', error_label=alamat_label_error, var_label=alamat_label : focus_out_handler(var, var_name, reset_bg, var_label, error_label))
    alamat.grid(row=7, column=0, sticky='ew')

    nama_pasangan_label =ttk.Label(input_form_frame, text='Nama pasangan')
    nama_pasangan_label_error = ttk.Label(input_form_frame, text='', font=('TkDefaultFont', 8), foreground='red')
    nama_pasangan_label.grid(row=8, column=0, sticky='w')
    nama_pasangan_label_error.grid(row=8, column=0)
    nama_pasangan_entry = tk.StringVar()
    nama_pasangan =ttk.Entry(input_form_frame, textvariable=nama_pasangan_entry, state='disabled')
    nama_pasangan_reset_bg = nama_pasangan.cget('foreground')
    nama_pasangan.bind('<FocusOut>', lambda event, reset_bg=nama_pasangan_reset_bg, var=nama_pasangan, var_name='nama_pasangan', error_label=nama_pasangan_label_error, var_label=nama_pasangan_label : focus_out_handler(var, var_name, reset_bg, var_label, error_label))
    nama_pasangan.grid(row=9, column=0, sticky='ew')

    nama_ibu_kandung_label = ttk.Label(input_form_frame, text='Nama ibu kandung*')
    nama_ibu_kandung_label_error = ttk.Label(input_form_frame, text='', font=('TkDefaultFont', 8), foreground='red')
    nama_ibu_kandung_label.grid(row=8, column=1, sticky='w', padx=4)
    nama_ibu_kandung_label_error.grid(row=8, column=1, padx=4)
    nama_ibu_kandung_entry = tk.StringVar()
    nama_ibu_kandung = ttk.Entry(input_form_frame, textvariable=nama_ibu_kandung_entry, state='disabled')
    nama_ibu_kandung_reset_bg = nama_ibu_kandung.cget('foreground')
    nama_ibu_kandung.bind('<FocusOut>', lambda event, reset_bg = nama_ibu_kandung_reset_bg, var=nama_ibu_kandung, var_name='nama_ibu_kandung', error_label=nama_ibu_kandung_label_error, var_label=nama_ibu_kandung_label : focus_out_handler(var, var_name, reset_bg, var_label, error_label))
    nama_ibu_kandung.grid(row=9, column=1, sticky='ew', padx=4)

    kolektibilitas_val = ['Lancar', 'Kurang lancar', 'Diragukan', 'Macet', 'Daftar hitam']
    kolektibilitas_label =ttk.Label(input_form_frame, text='Kolektibilitas*')
    kolektibilitas_label_error = ttk.Label(input_form_frame, text='', font=('TkDefaultFont', 8), foreground='red')
    kolektibilitas_label.grid(row=10, column=0, sticky='w')
    kolektibilitas_label_error.grid(row=10, column=0)
    kolektibilitas_entry = tk.IntVar()
    kolektibilitas = ttk.Combobox(input_form_frame, values=kolektibilitas_val, state='disabled')
    kolektibilitas_reset_bg = kolektibilitas.cget('foreground')
    kolektibilitas.bind('<FocusOut>', lambda event, reset_bg=kolektibilitas_reset_bg, var=kolektibilitas, var_name='kolektibilitas', error_label=kolektibilitas_label_error, var_label=kolektibilitas_label : focus_out_handler(var, var_name, reset_bg, var_label, error_label))
    kolektibilitas.grid(row=11, column=0, sticky='ew')

    keterangan_label =ttk.Label(input_form_frame, text='Keterangan')
    keterangan_label_error = ttk.Label(input_form_frame, text='', font=('TkDefaultFont', 8), foreground='red')
    keterangan_label.grid(row=12, column=0, sticky='w')
    keterangan_label_error.grid(row=12, column=0)
    keterangan_entry = tk.StringVar()
    keterangan = tk.Text(input_form_frame, height=6, state='disabled')
    keterangan_reset_bg = keterangan.cget('foreground')
    keterangan.bind('<FocusOut>', lambda event, reset_bg = keterangan_reset_bg, var=keterangan, var_name='keterangan', error_label=keterangan_label_error, var_label=keterangan_label : focus_out_handler(var, var_name, reset_bg, var_label, error_label))
    keterangan.grid(row=13, column=0, sticky='ew', columnspan=2)


    input_button_frame = ttk.Frame(input_form_frame)
    input_button_frame.columnconfigure(0, weight=1)
    input_button_frame.columnconfigure(1, weight=0)
    input_button_frame.columnconfigure(2, weight=1)
    checkButton = ttk.Button(input_button_frame, text='Check', command=check_button_handler)
    checkButton.grid(row=0, column=0, sticky='ew', pady=4)

    emptyPad = ttk.Frame(input_button_frame, width=4)
    emptyPad.grid(row=0, column=1, sticky='ew')

    editButton = ttk.Button(input_button_frame, text='Edit', command=edit_button_handler, state='disabled')
    editButton.grid(row=0, column=2, sticky='ew', pady=4)

    printButton = ttk.Button(input_button_frame, text='Print', state='disabled', command=print_button_handler)
    printButton.grid(row=1, column=0, columnspan=3, sticky='ew')
    input_button_frame.grid(row=14, column=0, columnspan=2, sticky='ew')

    input_form_frame.columnconfigure(0, weight=1)
    input_form_frame.columnconfigure(1, weight=1)

    #tab2
    input_excel_frame = ttk.Frame(notebook, padding=10)
    notebook.add(input_excel_frame, text='Input excel')

    file_upload_label = ttk.Label(input_excel_frame, text='Klik box dibawah untuk upload file excel')
    file_upload_label_error = ttk.Label(input_excel_frame, text='', font=('TkDefaultFont', 8), foreground='red')
    file_upload_label.grid(row=0, column=0, sticky='w')
    file_upload_label_error.grid(row=0, column=0)
    file_upload_entry = tk.StringVar()
    file_upload = ttk.Entry(input_excel_frame, textvariable=file_upload_entry, state='readonly', cursor='hand2')
    file_upload.grid(row=1, column=0, sticky='w')

    upload_button = ttk.Button(input_excel_frame, text='Upload', command=upload_button_handler, state='disabled')
    upload_button.grid(row=2, column=0, sticky='w')

    file_upload.bind('<Button-1>', lambda event, upload_entry = file_upload_entry, upload_button = upload_button : processing.upload_file_handler(upload_entry, upload_button))

    #tab3
    view_data_frame = ttk.Frame(notebook, padding=10)
    notebook.add(view_data_frame, text='View and delete data')

    view_data_label = ttk.Label(view_data_frame, text='List data')
    view_data_label.grid(row=0, column=0, columnspan=2, sticky='w')
    view_data_columns = ('nik', 'nama', 'tanggal_lahir', 'tempat_lahir', 'alamat', 'nama_ibu_kandung','nama_pasangan', 'kolektibilitas', 'keterangan')
    view_data_list = ttk.Treeview(view_data_frame, columns=view_data_columns, show='headings')
    view_data_list.heading('nik', text='NIK')
    view_data_list.heading('nama', text='Nama')
    view_data_list.heading('tanggal_lahir', text='Tanggal lahir')
    view_data_list.heading('tempat_lahir', text='Tempat lahir')
    view_data_list.heading('alamat', text='Alamat')
    view_data_list.heading('nama_ibu_kandung', text='Nama ibu kandung')
    view_data_list.heading('nama_pasangan', text='Nama pasangan')
    view_data_list.heading('kolektibilitas', text='Kolektibilitas')
    view_data_list.heading('keterangan', text='Keterangan')
    vertical_sb = ttk.Scrollbar(view_data_frame, orient='vertical', command=view_data_list.yview)
    horizontal_sb = ttk.Scrollbar(view_data_frame, orient='horizontal', command=view_data_list.xview)
    view_data_list.configure(xscrollcommand=horizontal_sb.set, yscrollcommand=vertical_sb.set)
    view_data_list.grid(row=1, column=0, sticky='new')
    vertical_sb.grid(row=1, column=1, sticky='ns')
    horizontal_sb.grid(row=2, column=0, sticky='ew')

    button_frame = ttk.Frame(view_data_frame)
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)

    delete_button = ttk.Button(button_frame, text='Delete', state='disabled', command=delete_button_handler)
    export_button = ttk.Button(button_frame, text='Export all', state='disabled', command=export_button_handler)
    delete_button.grid(row=0, column=0, sticky='w')
    export_button.grid(row=0, column=1, sticky='e')
    button_frame.grid(row=3, column=0, sticky='ew')


    view_data_list.bind('<Configure>', lambda event : on_scroll_lazy_load(event, view_data_list))
    view_data_list.bind('<Motion>', lambda event : on_scroll_lazy_load(event, view_data_list))
    view_data_list.bind('<ButtonRelease-1>', tree_row_click_handler)
    view_data_frame.grid_rowconfigure(1, weight=1)
    view_data_frame.grid_columnconfigure(0, weight=1)
    # view_data_frame.grid_columnconfigure(1, weight=1)


    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)
    notebook.bind('<<NotebookTabChanged>>', lambda event : lazy_show_data(event)) #Show all data only when the tab is active
    root.bind('<<NotebookTabChanged>>', lambda event: root.update_idletasks()) #To make the view more seamless when switching between tabs
    # Run the application's main event loop
    sv_ttk.set_theme('dark')
    root.mainloop()

if __name__ == '__main__':
    main()