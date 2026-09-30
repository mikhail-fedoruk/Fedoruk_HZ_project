import math

def is_number(value):
    try:
        return math.isfinite(float(value))
    except Exception:
        return False

def correct_number(value):
    if is_number(value) == False:
        warning = f"Введенное значение {value} не является числом!"
        return warning
    elif float(value) <= 0:
        warning = f"Введенное значение {value} неположительно!"
        return warning
    else:
        return True
        
def correct_star_mass(value):
    if is_number(value) == False:
        warning = f"Масса звезды {value} не является числом!"
        return warning    
    if float(value) < 0.013:
        warning = f"Масса звезды {value} ниже минимально допустимого значения!"
        return warning
    elif float(value) > 1000:
        warning = f"Масса звезды {value} превышает максимально допустимое значение!"
        return warning
    else:
        return True
    
def correct_eccentricity(value):
    if is_number(value) == False:
        warning = f"Эксцентриситет {value} не является числом!"
        return warning
    elif float(value) < 0:
        warning = f"Эксцентриситет {value} отрицательный!"
        return warning
    elif float(value) >= 1:
        warning = f"Эксцентриситет {value} превышает максимально допустимое значение!"
        return warning
    else:
        return True
    
def correct_fraction(value):
    if is_number(value) == False:
        warning = f"Фактор {value} не является числом!"
        return warning
    if float(value) > 1:
        warning = f"Фактор {value} превышает максимально допустимое значение!"
        return warning
    elif float(value) <= 0:
        warning = f"Фактор {value} неположительный!"
        return warning        
    else:
        return True

def correct_albedo(value):
    if is_number(value) == False:
        warning = f"Альбедо {value} не является числом!"
        return warning
    if float(value) >= 1:
        warning = f"Альбедо {value} превышает максимально допустимое значение!"
        return warning
    elif float(value) < 0:
        warning = f"Альбедо {value} отрицательное!"
        return warning
    else:
        return True