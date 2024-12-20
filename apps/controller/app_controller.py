from tkinter import messagebox, filedialog

from utils import utils
from views.app import App
from views.component import input_group
from services.debitur_service import debitur_service


# possibilities to refactor by merging all of this class and method
# to debitur_controller, so the controller would be more simple

class app_controller:
    def __init__(self, app:App):
        self.app = app
        self.debitur_service = debitur_service()

    def check_handler(self):
        if self.app.check_button['text'] != 'Cancel edit':
            key = self.app.nik.var.get()
            if self.debitur_service.validate_on_submit_service({'nik' : key}):
                res, data = self.debitur_service.find_record_by_key(key)
                if res:
                    [var.enable_state() for var in self.app.form_control]
                    self.app.edit_button.configure(state='normal')
                    self.app.print_button.configure(state='normal')
                    self.app.check_button.configure(text='Cancel edit')
                    self.app.nik.disable_state()
                    self.app.id.set_value(data.id)
                    self.app.nik.set_value(data.nik)
                    self.app.nama.set_value(data.nama)
                    self.app.tanggal_lahir.set_value(data.tanggal_lahir)
                    self.app.tempat_lahir.set_value(data.tempat_lahir)
                    self.app.alamat.set_value(data.alamat)
                    self.app.nama_pasangan.set_value(data.nama_pasangan)
                    self.app.nama_ibu_kandung.set_value(data.nama_ibu_kandung)
                    self.app.kolektibilitas.set_value(data.kolektibilitas)
                    self.app.keterangan.set_value(data.keterangan)
                    self.app.created_at.set_value(data.created_at)
                    self.app.last_edit.set_value(data.last_edit if data.last_edit else '')
                    self.app.id.disable_state()
                    self.app.created_at.disable_state()
                    self.app.last_edit.disable_state()

                else:
                    response = messagebox.askquestion('Question', 'Data tidak terdaftar, input baru?')
                    if response == 'yes':
                        self.app.edit_button.configure(text='Insert', state='normal')
                        [var.enable_state() for var in self.app.form_control]
                        self.app.id.disable_state()
                        self.app.created_at.disable_state()
                        self.app.last_edit.disable_state()
                        self.app.id.set_value(self.debitur_service.get_new_cif())
                        self.app.created_at.set_value(utils.get_today(False))
                    else:
                        self.app.edit_button.configure(state='disabled')
                        self.clear_all_input()
            else:
                messagebox.showerror('Error', 'Format NIK tidak valid!')
        else:
            self.app.created_at.enable_state()
            self.app.last_edit.enable_state()
            self.clear_all_input()
            self.app.nik.enable_state()
            self.app.check_button.configure(text='Check')
            self.app.print_button.configure(state='disabled')
            self.app.edit_button.configure(state='disabled')

    def clear_all_input(self):
        self.app.nik.clear_value()
        for var in self.app.form_control:
            var.clear_value()
            var.disable_state()

    def edit_insert_handler(self):
        data = {'id' : self.app.id.get_value(),
                'nik' : self.app.nik.get_value(),
                'nama' : self.app.nama.get_value(),
                'tempat_lahir' : self.app.tempat_lahir.get_value(),
                'tanggal_lahir' : self.app.tanggal_lahir.get_value(),
                'alamat' : self.app.alamat.get_value(),
                'nama_ibu_kandung' : self.app.nama_ibu_kandung.get_value(),
                'kolektibilitas' : self.app.kolektibilitas.get_value(),
                'nama_pasangan' : self.app.nama_pasangan.get_value(),
                'keterangan' : self.app.keterangan.get_value(),
                'created_at' : self.app.created_at.get_value(),
                'last_edit' : self.app.last_edit.get_value()
        }
        if self.app.edit_button['text'] == 'Insert':
            if self.debitur_service.validate_on_submit_service(data):
                # data['created_at'] = datetime.now().date()
                response, msg = self.debitur_service.insert_to_db(data)
                if response:
                    self.app.id.enable_state()
                    self.app.created_at.enable_state()
                    self.app.last_edit.enable_state()
                    self.clear_all_input()
                    messagebox.showinfo('Success', 'Data sukses di input!')
                    self.app.edit_button.configure(text='Edit', state='disabled')
                else:
                    if msg == 'IntegrityError':
                        messagebox.showerror('Failed', 'NIK sudah terdaftar!')
                    elif msg == 'UnexpectedError':
                        messagebox.showerror('Failed', 'Unexpected Error!')
                    self.app.id.enable_state()
                    self.clear_all_input()
        elif self.app.edit_button['text'] == 'Edit':
            if self.debitur_service.validate_on_submit_service(data):
                data['last_edit'] = utils.get_today(False)
                response, msg = self.debitur_service.edit_record_service(data)
                if response:
                    messagebox.showinfo('Success', msg)
                    self.app.id.enable_state()
                    self.app.last_edit.enable_state()
                    self.app.created_at.enable_state()
                    self.clear_all_input()
                    self.app.nik.enable_state()
                    self.app.edit_button.configure(state='disabled')
                    self.app.print_button.configure(state='disabled')
                    self.app.check_button.configure(text='Check')
                else:
                    messagebox.showerror('Failed', msg)
            else:
                messagebox.showerror('Invalid input', 'Cek ulang data!')

    def print_button_handler(self):
        possible_path = filedialog.askdirectory()
        key = self.app.nik.get_value()
        if possible_path:
            res, msg = self.debitur_service.print_pdf(key, possible_path)
            if res:
                messagebox.showinfo('Success', msg)
            else:
                messagebox.showerror('Failed', msg)
            self.app.print_button.config(state='disabled')


    def check_nik(self, widget:input_group):
        value = widget.var.get()
        if len(value) == 0 or (len(value) != 16 or utils.check_valid_nik(value)):
            widget.show_label_error('Digit NIK tidak sesuai atau data tidak boleh kosong.')
        else:
            widget.hide_label_error()
    
    def check_nama(self, widget:input_group):
        value = widget.var.get()
        if len(value) == 0 or not utils.check_valid_alphanum(value, nullable=False):
            widget.show_label_error('Nama harus alphanumeric atau data tidak boleh kosong.')
        else:
            widget.hide_label_error()
    
    def check_tanggal_lahir(self, widget:input_group):
        value = widget.var.get()
        if len(value) == 0:
            widget.show_label_error('Data tidak boleh kosong.')
        else:
            try:
                possible_date = utils.parse_date(value, True)
            except ValueError as e:
                widget.show_label_error('Format tidak sesuai!')
            else:
                del possible_date
                widget.hide_label_error()
    
    def check_tempat_lahir(self, widget:input_group):
        value = widget.var.get()
        if len(value) == 0 or not utils.check_valid_alphanum(value, nullable=False):
            widget.show_label_error('Tempat lahir harus alphanumeric atau data tidak boleh kosong.')
        else:
            widget.hide_label_error()
    
    def check_alamat(self, widget:input_group):
        value = widget.var.get()
        if len(value) == 0:
            widget.show_label_error('Data tidak boleh kosong.')
        else:
            widget.hide_label_error()
    
    def check_nama_pasangan(self, widget:input_group):
        value = widget.var.get()
        if not utils.check_valid_alphanum(value, nullable=True):
            widget.show_label_error('Nama pasangan harus alphanumeric.')
        else:
            widget.hide_label_error()
    
    def check_nama_ibu_kandung(self, widget:input_group):
        value = widget.var.get()
        if len(value) == 0 or not utils.check_valid_alphanum(value, nullable=False):
            widget.show_label_error('Nama ibu kandung harus alphanumeric dan tidak boleh kosong.')
        else:
            widget.hide_label_error()
    
    def check_kolektibilitas(self, widget:input_group):
        value = widget.var.get()
        if len(value) == 0:
            widget.show_label_error('Kolektibilitas harus diisi')
        else:
            widget.hide_label_error()
    
    def check_keterangan(self, widget:input_group):
        pass