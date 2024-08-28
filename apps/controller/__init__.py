import sys
import os

DATATABLE_BATCH = 20
DATATABLE_LOADED_ROWS = 0
IS_ALL_LOADED = False
if getattr(sys, 'frozen', False):
    abs_path = sys._MEIPASS
else:
    abs_path = os.path.abspath('.')