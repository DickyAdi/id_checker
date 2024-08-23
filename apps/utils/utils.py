from datetime import datetime
import re

def check_valid_alphanum(self, value, nullable=True):
        pattern_name = re.compile(r"^[A-Za-z0-9.,'`\-\(\)]+$")
        if len(value) == 0 and nullable:
            return True
        else:
            if pattern_name.match(value):
                return True
            else:
                return False
def check_valid_nik(self, digits):
    pattern = re.compile(r"%[0-9]$")
    if pattern.match(digits):
        return True
    else:
        return False
def parse_date(self, date_value:str, db_format=True):
    """Parse date input

    Args:
        date_value (str): Date value
        db_format (bool, optional): If True, it will parse the value to database format, else it will parse the value to application format. Defaults to True.

    Returns:
        str: parsed date
    """
    if db_format:
        return datetime.strptime(date_value, '%d-%m-%Y').strftime('%Y-%m-%d')
    else:
        return datetime.strptime(date_value, '%Y-%m-%d').strftime('%d-%m-%Y')