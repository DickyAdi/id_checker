from datetime import datetime
import re

from controller.debitur_controller import debitur_controller
from model.debitur import debitur

class debitur_service:
    def __init__(self):
        self.debitur_controller = debitur_controller()
    def find_record_by_key(self, key) -> debitur:
        return self.debitur_controller.search_key(key)
    def is_db_empty(self):
        return self.debitur_controller.is_db_empty()
    def get_total_records(self):
        return self.debitur_controller.get_total_records()
    def insert_to_db(self, data:dict):
        return self.debitur_controller.insert(data)
    def validate_on_submit_service(self, data:dict):
        return self.debitur_controller.validate_on_submit(data)
    def edit_record_service(self, data:dict):
        return self.debitur_controller.edit(data)
    def delete_record_service(self, key:str):
        return self.debitur_controller.delete(key)
    def dump_csv_service(self, possible_dir):
        return self.debitur_controller.dump_to_csv(possible_dir)
    def print_pdf(self, key:str, path:str):
        return self.debitur_controller.create_pdf(key, path)