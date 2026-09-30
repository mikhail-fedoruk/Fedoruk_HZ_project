import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import RadioButtons, TextBox, Slider, Button
import matplotlib.patheffects as path_effects

import utils as utils
import models as models
import physics as physics
import constants as constants


# ==============================================================================
# ОТРИСОВКА ДИАГРАММЫ
# ==============================================================================

font_size_vidgets = 8


# ------------------------------------------------------------------------------
# ПАРАМЕТРЫ ОКНА ГРАФИКА

fig, ax = plt.subplots(figsize=(14.5, 8))
plt.subplots_adjust(left=0.25)
plt.subplots_adjust(right=0.85)
plt.subplots_adjust(bottom=0.12)
plt.subplots_adjust(top=0.94)
fig.canvas.manager.set_window_title('Моделирование зоны обитаемости')

# ------------------------------------------------------------------------------
# МАТРИЦА

x = np.linspace(-4, 4, 400)
y = np.linspace(-4, 4, 400)
X, Y = np.meshgrid(x, y)
Z = np.zeros_like(X)
empty_temperature = np.full_like(X, np.nan)
result_ready = False

# ------------------------------------------------------------------------------
# ОТРИСОВКА ЗОНЫ ОБИТАЕМОСТИ

Habitable_zone = Z.copy()
Habitable_zone[(Habitable_zone < 0) | (Habitable_zone > 100)] = np.nan
habitable_zone_mesh = ax.pcolormesh(X, Y, Habitable_zone, shading='auto', cmap=mcolors.ListedColormap(['forestgreen']), alpha=np.where(np.isnan(Habitable_zone), 0.0, 0.4))
habitable_zone_contour = ax.contour(X, Y, Z, levels=[0, 100], colors='forestgreen', linewidths=2)

def draw_habitable_zone(Z):
    global X, Y
    global habitable_zone_mesh
    global habitable_zone_contour
    
    habitable_zone_mesh.remove()
    habitable_zone_contour.remove()

    Habitable_zone = Z.copy()
    Habitable_zone[(Habitable_zone < 0) | (Habitable_zone > 100)] = np.nan
    habitable_zone_mesh = ax.pcolormesh(X, Y, Habitable_zone, shading='auto', cmap=mcolors.ListedColormap(['forestgreen']), alpha=np.where(np.isnan(Habitable_zone), 0.0, 0.4))
    habitable_zone_contour = ax.contour(X, Y, Z, levels=[0, 100], colors='forestgreen', linewidths=2)

mesh = ax.pcolormesh(X, Y, Z, shading='auto', cmap='plasma', vmin=-200, vmax=200)

plt.colorbar(mesh, label='Температура, °C')

# ------------------------------------------------------------------------------
# ДЕЛЕНИЯ ГРАФИКА

ticks = np.arange(-4, 4.5, 0.5)
ax.set_xticks(ticks)
ax.set_yticks(ticks)
ax.set_xlabel('X, а.е.')
ax.set_ylabel('Y, а.е.')

# ------------------------------------------------------------------------------
# СТРОКА СОСТОЯНИЯ

def format_coord(x_current, y_current):

    x_idx = np.argmin(np.abs(x - x_current))
    y_idx = np.argmin(np.abs(y - y_current))

    z_value = Z[y_idx, x_idx]

    return (f'X={x_current:.2f} а.е., ' f'Y={y_current:.2f} а.е. | ' f'Температура: {z_value:.0f} °C')

ax.format_coord = format_coord

# ------------------------------------------------------------------------------
# ПОЛУЧЕНИЕ ДАННЫХ О ГРАФИКЕ

def show_data(event):
    if not result_ready:
        show_data_final_field.set_text('Сначала выполните успешный расчёт.')
        fig.canvas.draw_idle()
        return
    global data_show_x_textbox, data_show_y_textbox, data_show_time_textbox
    global Z, Z_history, Flux, Flux_history, Stars_positions
    global x, y
    
    x_request = data_show_x_textbox.text
    y_request = data_show_y_textbox.text
    time_request = data_show_time_textbox.text
    
    if utils.is_number(x_request) == True and utils.is_number(y_request) == True:
        if (float(x_request) > -4) and (float(x_request) < 4) and (float(y_request) > -4) and (float(y_request) < 4):
            if data_show_time_box.get_visible() == False:
                if 'Flux' not in globals():
                    x_request_idx = np.argmin(np.abs(x - float(x_request)))
                    y_request_idx = np.argmin(np.abs(y - float(y_request)))
                    z_request_value = Z[y_request_idx, x_request_idx]                    
                    show_data_final_field.set_text(f'Температура в точке: {z_request_value:.1f} °C')
                else:
                    x_request_idx = np.argmin(np.abs(x - float(x_request)))
                    y_request_idx = np.argmin(np.abs(y - float(y_request)))
                    z_request_value = Z[y_request_idx, x_request_idx]
                    flux_request_value = Flux[y_request_idx, x_request_idx]
                    show_data_final_field.set_text(f'Температура в точке: {z_request_value:.1f} °C\nПоток: {flux_request_value:.1f} Вт/м^2')
            else:
                if utils.is_number(time_request) == True:
                    if (float(time_request) <= 1) and (float(time_request) >= 0):
                        idx_request = int(round(float(time_request) * (physics.orbit_samples_amount - 1)))
                        idx_request = max(0, min(idx_request, physics.orbit_samples_amount - 1))
                        x_request_idx = np.argmin(np.abs(x - float(x_request)))
                        y_request_idx = np.argmin(np.abs(y - float(y_request)))                        
                        z_request_value = Z_history[idx_request, y_request_idx, x_request_idx]
                        flux_request_value = Flux_history[idx_request, y_request_idx, x_request_idx]
                        show_data_final_field.set_text(f'Температура в точке: {z_request_value:.1f} °C\nПоток: {flux_request_value:.1f} Вт/м^2\nX1 = {Stars_positions[idx_request, 0]:.3f}\nY1 = {Stars_positions[idx_request, 1]:.3f}\nX2 = {Stars_positions[idx_request, 2]:.3f}\nY2 = {Stars_positions[idx_request, 3]:.3f}')
                    else:
                        show_data_final_field.set_text('Введены некорректные значения.')
                else:
                    show_data_final_field.set_text('Введены некорректные значения.')
        else:
            show_data_final_field.set_text('Введены некорректные значения.')
    else:
        show_data_final_field.set_text('Введены некорректные значения.')
    
    
data_show_textbox_fields_width = 0.05
data_show_textbox_fields_height = 0.035

data_show_label_box_fields_width = 0.06
data_show_label_box_fields_height = 0.035

data_show_label_box_fields_x_min = 0.84
data_show_textbox_fields_x_min = data_show_label_box_fields_x_min + data_show_label_box_fields_width + 0.02

data_show_fields_y_max = 0.90
data_show_fields_delta_y = 0.045


data_show_fields_title = plt.axes([data_show_label_box_fields_x_min, data_show_fields_y_max, data_show_textbox_fields_width, data_show_textbox_fields_height])
data_show_fields_title.axis('off')
data_show_fields_title.text(0, 0.5, 'ПОЛУЧЕНИЕ ДАННЫХ', va='center', fontsize=font_size_vidgets, fontweight='bold')

data_show_x_box = plt.axes([data_show_textbox_fields_x_min, data_show_fields_y_max - data_show_fields_delta_y, data_show_textbox_fields_width, data_show_textbox_fields_height])
data_show_y_box = plt.axes([data_show_textbox_fields_x_min, data_show_fields_y_max - data_show_fields_delta_y*2, data_show_textbox_fields_width, data_show_textbox_fields_height])
data_show_time_box = plt.axes([data_show_textbox_fields_x_min, data_show_fields_y_max - data_show_fields_delta_y*3, data_show_textbox_fields_width, data_show_textbox_fields_height])

data_show_x_label_box = plt.axes([data_show_label_box_fields_x_min, data_show_fields_y_max - data_show_fields_delta_y, data_show_label_box_fields_width, data_show_label_box_fields_height])
data_show_y_label_box = plt.axes([data_show_label_box_fields_x_min, data_show_fields_y_max - data_show_fields_delta_y*2, data_show_label_box_fields_width, data_show_label_box_fields_height])
data_show_time_label_box = plt.axes([data_show_label_box_fields_x_min, data_show_fields_y_max - data_show_fields_delta_y*3, data_show_label_box_fields_width, data_show_label_box_fields_height])

for label_box in [data_show_x_label_box, data_show_y_label_box, data_show_time_label_box]:
    label_box.axis('off')

data_show_x_label = data_show_x_label_box.text(0, 0.5, 'Координата X, а.е.:', va='center', fontsize=font_size_vidgets)
data_show_y_label = data_show_y_label_box.text(0, 0.5, 'Коорината Y, а.е.:', va='center', fontsize=font_size_vidgets)
data_show_time_label = data_show_time_label_box.text(0, 0.5, 'Время, периоды:', va='center', fontsize=font_size_vidgets)

data_show_x_textbox = TextBox(data_show_x_box, '', initial=0)
data_show_y_textbox = TextBox(data_show_y_box, '', initial=0)
data_show_time_textbox = TextBox(data_show_time_box, '', initial=0)

for textbox in [data_show_x_textbox, data_show_y_textbox, data_show_time_textbox]:
    textbox.text_disp.set_size(font_size_vidgets)

data_show_time_label.set_visible(False)
data_show_time_box.set_visible(False)

data_show_button_box = plt.axes([data_show_label_box_fields_x_min, data_show_fields_y_max - data_show_fields_delta_y*4.5, 0.08, data_show_fields_delta_y])
data_show_button = Button(data_show_button_box, "Получить данные", color='lightblue', hovercolor='skyblue')
data_show_button.label.set_fontsize(font_size_vidgets)
data_show_button.on_clicked(show_data)

show_data_final_field_box = plt.axes([data_show_label_box_fields_x_min, data_show_fields_y_max - data_show_fields_delta_y*7, data_show_label_box_fields_width, data_show_label_box_fields_height])
show_data_final_field_box.axis('off')
show_data_final_field = show_data_final_field_box.text(0, 0.5, '', va='center', fontsize=font_size_vidgets)

# ------------------------------------------------------------------------------
# СЛАЙДЕР

def change_time(val):
    if not result_ready or 'Z_history' not in globals():
        return
    global Z, Z_history, Flux_history, Stars_positions, always_habitable, Star_1, Star_1_label, Star_2, Star_2_label
    
    idx = int(round(val * (physics.orbit_samples_amount - 1)))
    idx = max(0, min(idx, physics.orbit_samples_amount - 1))
    Z = Z_history[idx, :, :]
            
    mesh.set_array(Z.ravel())
    draw_habitable_zone(Z)
            
    # Звезды
            
    Star_1.set_center([Stars_positions[idx, 0], Stars_positions[idx, 1]])
    Star_1_label.set_position([Stars_positions[idx, 0], Stars_positions[idx, 1] + 0.15])
            
    Star_2.set_center([Stars_positions[idx, 2], Stars_positions[idx, 3]])
    Star_2_label.set_position([Stars_positions[idx, 2], Stars_positions[idx, 3] + 0.15])
    
    stars_coordinates.set_text(f'X1 = {Stars_positions[idx, 0]:.3f}\nY1 = {Stars_positions[idx, 1]:.3f}\nX2 = {Stars_positions[idx, 2]:.3f}\nY2 = {Stars_positions[idx, 3]:.3f}')

slider_box = plt.axes([0.2, 0.03, 0.7, 0.03])
slider = Slider(slider_box, 'T, Орбитальные периоды', 0.0, 1.0, valinit=0.0)
slider_box.set_visible(False)

slider.on_changed(change_time)

# ==============================================================================
# ЭЛЕМЕНТЫ ВВОДА ДАННЫХ
# ==============================================================================



# ------------------------------------------------------------------------------
# ЗАМЕНА ПОЛЕЙ ВВОДА ДЛЯ СИСТЕМЫ (БИНАРНАЯ / ОДИНОЧНАЯ)

def toggle_interface(system_type):
    system_type = system_type_radio.value_selected
    if system_type == "Одиночная":
        
        planet_name_label_box.set_visible(True)
        planet_semi_major_axis_label_box.set_visible(True)
        planet_eccentricity_label_box.set_visible(True)
        planet_name_box.set_visible(True)
        planet_semi_major_axis_box.set_visible(True)
        planet_eccentricity_box.set_visible(True)
        
        star_2_fields_title.set_visible(False)
        star_name_box_2.set_visible(False)
        star_mass_box_2.set_visible(False)
        star_luminosity_box_2.set_visible(False)
        star_name_label_box_2.set_visible(False)
        star_mass_label_box_2.set_visible(False)
        star_luminosity_label_box_2.set_visible(False)
        
        stars_orbit_fields_title.set_visible(False)
        stars_semi_major_axis_box.set_visible(False)
        stars_eccentricity_box.set_visible(False)
        stars_semi_major_axis_label_box.set_visible(False)
        stars_eccentricity_label_box.set_visible(False)
        
        star_vidgets_y_max = (planet_vidgets_y_max - delta_y*7) - 0.01
        star_2_vidgets_y_max = (star_vidgets_y_max - delta_y*4) - 0.01
        stars_orbit_vidgets_y_max = (star_2_vidgets_y_max - delta_y*4) - 0.01
        
        start_box.set_position([0.02, star_2_vidgets_y_max - 0.02, 0.08, 0.04])
        
        planet_bond_albedo_box.set_position([textbox_vidgets_x_min, planet_vidgets_y_max - delta_y*4, textbox_width, textbox_height])
        planet_emissivity_box.set_position([textbox_vidgets_x_min, planet_vidgets_y_max - delta_y*5, textbox_width, textbox_height])
        planet_redistribution_factor_box.set_position([textbox_vidgets_x_min, planet_vidgets_y_max - delta_y*6, textbox_width, textbox_height])
        planet_bond_albedo_label_box.set_position([label_box_vidgets_x_min, planet_vidgets_y_max - delta_y*4 - 0.01, label_box_width, label_box_height])
        planet_emissivity_label_box.set_position([label_box_vidgets_x_min, planet_vidgets_y_max - delta_y*5 - 0.01, label_box_width, label_box_height])
        planet_redistribution_factor_label_box.set_position([label_box_vidgets_x_min, planet_vidgets_y_max - delta_y*6 - 0.01, label_box_width, label_box_height])        
        
        star_fields_title.set_position([label_box_vidgets_x_min, star_vidgets_y_max, textbox_width, textbox_height])
        star_name_box.set_position([textbox_vidgets_x_min, star_vidgets_y_max - delta_y, textbox_width, textbox_height])
        star_mass_box.set_position([textbox_vidgets_x_min, star_vidgets_y_max - delta_y*2, textbox_width, textbox_height])
        star_luminosity_box.set_position([textbox_vidgets_x_min, star_vidgets_y_max - delta_y*3, textbox_width, textbox_height])
        star_name_label_box.set_position([label_box_vidgets_x_min, star_vidgets_y_max - delta_y - 0.01, label_box_width, label_box_height])
        star_mass_label_box.set_position([label_box_vidgets_x_min, star_vidgets_y_max - delta_y*2 - 0.01, label_box_width, label_box_height])
        star_luminosity_label_box.set_position([label_box_vidgets_x_min, star_vidgets_y_max - delta_y*3 - 0.01, label_box_width, label_box_height])
        
        star_2_fields_title.set_position([label_box_vidgets_x_min, star_2_vidgets_y_max, textbox_width, textbox_height])
        star_name_box_2.set_position([textbox_vidgets_x_min, star_2_vidgets_y_max - delta_y, textbox_width, textbox_height])
        star_mass_box_2.set_position([textbox_vidgets_x_min, star_2_vidgets_y_max - delta_y*2, textbox_width, textbox_height])
        star_luminosity_box_2.set_position([textbox_vidgets_x_min, star_2_vidgets_y_max - delta_y*3, textbox_width, textbox_height])
        star_name_label_box_2.set_position([label_box_vidgets_x_min, star_2_vidgets_y_max - delta_y - 0.01, label_box_width, label_box_height])
        star_mass_label_box_2.set_position([label_box_vidgets_x_min, star_2_vidgets_y_max - delta_y*2 - 0.01, label_box_width, label_box_height])
        star_luminosity_label_box_2.set_position([label_box_vidgets_x_min, star_2_vidgets_y_max - delta_y*3 - 0.01, label_box_width, label_box_height])
        
        stars_orbit_fields_title.set_position([label_box_vidgets_x_min, stars_orbit_vidgets_y_max, textbox_width, textbox_height])
        stars_semi_major_axis_box.set_position([textbox_vidgets_x_min, stars_orbit_vidgets_y_max - delta_y, textbox_width, textbox_height])
        stars_eccentricity_box.set_position([textbox_vidgets_x_min, stars_orbit_vidgets_y_max - delta_y*2, textbox_width, textbox_height])
        stars_semi_major_axis_label_box.set_position([label_box_vidgets_x_min, stars_orbit_vidgets_y_max - delta_y - 0.01, label_box_width, label_box_height])
        stars_eccentricity_label_box.set_position([label_box_vidgets_x_min, stars_orbit_vidgets_y_max - delta_y*2 - 0.01, label_box_width, label_box_height])        
        return
    else:
        
        planet_name_label_box.set_visible(False)
        planet_semi_major_axis_label_box.set_visible(False)
        planet_eccentricity_label_box.set_visible(False)
        planet_name_box.set_visible(False)
        planet_semi_major_axis_box.set_visible(False)
        planet_eccentricity_box.set_visible(False)      
        
        star_2_fields_title.set_visible(True)
        star_name_box_2.set_visible(True)
        star_mass_box_2.set_visible(True)
        star_luminosity_box_2.set_visible(True)
        star_name_label_box_2.set_visible(True)
        star_mass_label_box_2.set_visible(True)
        star_luminosity_label_box_2.set_visible(True)
        
        stars_orbit_fields_title.set_visible(True)
        stars_semi_major_axis_box.set_visible(True)
        stars_eccentricity_box.set_visible(True)
        stars_semi_major_axis_label_box.set_visible(True)
        stars_eccentricity_label_box.set_visible(True)
        
        star_vidgets_y_max = (planet_vidgets_y_max - delta_y*4) - 0.01
        star_2_vidgets_y_max = (star_vidgets_y_max - delta_y*4) - 0.01
        stars_orbit_vidgets_y_max = (star_2_vidgets_y_max - delta_y*4) - 0.01
        
        start_box.set_position([0.02, (stars_orbit_vidgets_y_max - delta_y*3) - 0.03, 0.08, 0.04])
        
        planet_bond_albedo_box.set_position([textbox_vidgets_x_min, planet_vidgets_y_max - delta_y, textbox_width, textbox_height])
        planet_emissivity_box.set_position([textbox_vidgets_x_min, planet_vidgets_y_max - delta_y*2, textbox_width, textbox_height])
        planet_redistribution_factor_box.set_position([textbox_vidgets_x_min, planet_vidgets_y_max - delta_y*3, textbox_width, textbox_height])
        planet_bond_albedo_label_box.set_position([label_box_vidgets_x_min, planet_vidgets_y_max - delta_y - 0.01, label_box_width, label_box_height])
        planet_emissivity_label_box.set_position([label_box_vidgets_x_min, planet_vidgets_y_max - delta_y*2 - 0.01, label_box_width, label_box_height])
        planet_redistribution_factor_label_box.set_position([label_box_vidgets_x_min, planet_vidgets_y_max - delta_y*3 - 0.01, label_box_width, label_box_height])        
        
        star_fields_title.set_position([label_box_vidgets_x_min, star_vidgets_y_max, textbox_width, textbox_height])
        star_name_box.set_position([textbox_vidgets_x_min, star_vidgets_y_max - delta_y, textbox_width, textbox_height])
        star_mass_box.set_position([textbox_vidgets_x_min, star_vidgets_y_max - delta_y*2, textbox_width, textbox_height])
        star_luminosity_box.set_position([textbox_vidgets_x_min, star_vidgets_y_max - delta_y*3, textbox_width, textbox_height])
        star_name_label_box.set_position([label_box_vidgets_x_min, star_vidgets_y_max - delta_y - 0.01, label_box_width, label_box_height])
        star_mass_label_box.set_position([label_box_vidgets_x_min, star_vidgets_y_max - delta_y*2 - 0.01, label_box_width, label_box_height])
        star_luminosity_label_box.set_position([label_box_vidgets_x_min, star_vidgets_y_max - delta_y*3 - 0.01, label_box_width, label_box_height])
        
        star_2_fields_title.set_position([label_box_vidgets_x_min, star_2_vidgets_y_max, textbox_width, textbox_height])
        star_name_box_2.set_position([textbox_vidgets_x_min, star_2_vidgets_y_max - delta_y, textbox_width, textbox_height])
        star_mass_box_2.set_position([textbox_vidgets_x_min, star_2_vidgets_y_max - delta_y*2, textbox_width, textbox_height])
        star_luminosity_box_2.set_position([textbox_vidgets_x_min, star_2_vidgets_y_max - delta_y*3, textbox_width, textbox_height])
        star_name_label_box_2.set_position([label_box_vidgets_x_min, star_2_vidgets_y_max - delta_y - 0.01, label_box_width, label_box_height])
        star_mass_label_box_2.set_position([label_box_vidgets_x_min, star_2_vidgets_y_max - delta_y*2 - 0.01, label_box_width, label_box_height])
        star_luminosity_label_box_2.set_position([label_box_vidgets_x_min, star_2_vidgets_y_max - delta_y*3 - 0.01, label_box_width, label_box_height])
        
        stars_orbit_fields_title.set_position([label_box_vidgets_x_min, stars_orbit_vidgets_y_max, textbox_width, textbox_height])
        stars_semi_major_axis_box.set_position([textbox_vidgets_x_min, stars_orbit_vidgets_y_max - delta_y, textbox_width, textbox_height])
        stars_eccentricity_box.set_position([textbox_vidgets_x_min, stars_orbit_vidgets_y_max - delta_y*2, textbox_width, textbox_height])
        stars_semi_major_axis_label_box.set_position([label_box_vidgets_x_min, stars_orbit_vidgets_y_max - delta_y - 0.01, label_box_width, label_box_height])
        stars_eccentricity_label_box.set_position([label_box_vidgets_x_min, stars_orbit_vidgets_y_max - delta_y*2 - 0.01, label_box_width, label_box_height])        
        return

system_type_box = plt.axes([0.015, 0.94, 0.075, 0.045])
system_type_radio = RadioButtons(system_type_box, ('Одиночная', 'Бинарная'))

for label in system_type_radio.labels:
    label.set_fontsize(font_size_vidgets)

system_type_radio.on_clicked(toggle_interface)

# ------------------------------------------------------------------------------
# СИСТЕМА ВЫВОДА ПРЕДУПРЕЖДЕНИЙ

warning_field_settings = dict(boxstyle='round,pad=0.3',  facecolor='none', edgecolor='green', linewidth=1.5)
warning_label_box = plt.axes([0.11, 0.925, 0.1, 0.08])
warning_label_box.axis('off')
warning_lebel_text = warning_label_box.text(0, 0.5, 'NO WARNING :)', va='center', color='green', bbox=warning_field_settings, fontsize = font_size_vidgets)

def change_warning_label(event):
    global warning_lebel_text
    warning_lebel_text.set_text('NO WARNING :)')
    warning_lebel_text.set_color('green')
    warning_lebel_text.get_bbox_patch().set_edgecolor('green')
    warning_lebel_text.set_weight('normal')

change_warning_label_box = plt.axes([0.10, 0.91, 0.09, 0.035])
change_warning_label_button = Button(change_warning_label_box, "Принято к сведению", color='lightblue', hovercolor='skyblue')
change_warning_label_button.label.set_fontsize(font_size_vidgets)
change_warning_label_button.on_clicked(change_warning_label)

# ------------------------------------------------------------------------------
# СИСТЕМА СБОРА ДАННЫХ С ПОЛЕЙ ВВОДА

textbox_vidgets_x_min = 0.10
label_box_vidgets_x_min = 0.015
planet_vidgets_y_max = 0.88
delta_y = 0.035
star_vidgets_y_max = (planet_vidgets_y_max - delta_y*7) - 0.01
star_2_vidgets_y_max = (star_vidgets_y_max - delta_y*4) - 0.01
stars_orbit_vidgets_y_max = (star_2_vidgets_y_max - delta_y*4) - 0.01

textbox_width = 0.075
textbox_height = 0.02
label_box_width = 0.09
label_box_height = 0.04

# ПОЛЯ ВВОДА ЗВЕЗДА 1

star_fields_title = plt.axes([label_box_vidgets_x_min, star_vidgets_y_max, textbox_width, textbox_height])
star_fields_title.axis('off')
star_fields_title.text(0, 0.5, 'ЗВЕЗДА №1', va='center', fontsize=font_size_vidgets, fontweight='bold')

star_name_box = plt.axes([textbox_vidgets_x_min, star_vidgets_y_max - delta_y, textbox_width, textbox_height])
star_mass_box = plt.axes([textbox_vidgets_x_min, star_vidgets_y_max - delta_y*2, textbox_width, textbox_height])
star_luminosity_box = plt.axes([textbox_vidgets_x_min, star_vidgets_y_max - delta_y*3, textbox_width, textbox_height])

star_name_label_box = plt.axes([label_box_vidgets_x_min, star_vidgets_y_max - delta_y - 0.01, label_box_width, label_box_height])
star_mass_label_box = plt.axes([label_box_vidgets_x_min, star_vidgets_y_max - delta_y*2 - 0.01, label_box_width, label_box_height])
star_luminosity_label_box = plt.axes([label_box_vidgets_x_min, star_vidgets_y_max - delta_y*3 - 0.01, label_box_width, label_box_height])

for label_box in [star_name_label_box, star_mass_label_box, star_luminosity_label_box]:
    label_box.axis('off')

star_name_label_box.text(0, 0.5, 'Название звезды:', va='center', fontsize=font_size_vidgets)
star_mass_label_box.text(0, 0.5, 'Масса звезды, M☉:', va='center', fontsize=font_size_vidgets)
star_luminosity_label_box.text(0, 0.5, 'Светимость, L☉:', va='center', fontsize=font_size_vidgets)

star_name_textbox = TextBox(star_name_box, '', initial="Солнце")
star_mass_solar_mass_textbox = TextBox(star_mass_box, '', initial=1)
star_luminosity_solar_luminosity_textbox = TextBox(star_luminosity_box, '', initial=1)

for textbox in [star_name_textbox, star_mass_solar_mass_textbox, star_luminosity_solar_luminosity_textbox]:
    textbox.text_disp.set_size(font_size_vidgets)

# ПОЛЯ ВВОДА ЗВЕЗДА 2

star_2_fields_title = plt.axes([label_box_vidgets_x_min, star_2_vidgets_y_max, textbox_width, textbox_height])
star_2_fields_title.axis('off')
star_2_fields_title.text(0, 0.5, 'ЗВЕЗДА №2', va='center', fontsize=font_size_vidgets, fontweight='bold')

star_name_box_2 = plt.axes([textbox_vidgets_x_min, star_2_vidgets_y_max - delta_y, textbox_width, textbox_height])
star_mass_box_2 = plt.axes([textbox_vidgets_x_min, star_2_vidgets_y_max - delta_y*2, textbox_width, textbox_height])
star_luminosity_box_2 = plt.axes([textbox_vidgets_x_min, star_2_vidgets_y_max - delta_y*3, textbox_width, textbox_height])

star_name_label_box_2 = plt.axes([label_box_vidgets_x_min, star_2_vidgets_y_max - delta_y - 0.01, label_box_width, label_box_height])
star_mass_label_box_2 = plt.axes([label_box_vidgets_x_min, star_2_vidgets_y_max - delta_y*2 - 0.01, label_box_width, label_box_height])
star_luminosity_label_box_2 = plt.axes([label_box_vidgets_x_min, star_2_vidgets_y_max - delta_y*3 - 0.01, label_box_width, label_box_height])

for label_box in [star_name_label_box_2, star_mass_label_box_2, star_luminosity_label_box_2]:
    label_box.axis('off')

star_name_label_box_2.text(0, 0.5, 'Название звезды:', va='center', fontsize=font_size_vidgets)
star_mass_label_box_2.text(0, 0.5, 'Масса звезды, M☉:', va='center', fontsize=font_size_vidgets)
star_luminosity_label_box_2.text(0, 0.5, 'Светимость, L☉:', va='center', fontsize=font_size_vidgets)

star_name_textbox_2 = TextBox(star_name_box_2, '', initial="Солнце")
star_mass_solar_mass_textbox_2 = TextBox(star_mass_box_2, '', initial=1)
star_luminosity_solar_luminosity_textbox_2 = TextBox(star_luminosity_box_2, '', initial=1)

for textbox in [star_name_textbox_2, star_mass_solar_mass_textbox_2, star_luminosity_solar_luminosity_textbox_2]:
    textbox.text_disp.set_size(font_size_vidgets)

star_2_fields_title.set_visible(False)
star_name_box_2.set_visible(False)
star_mass_box_2.set_visible(False)
star_luminosity_box_2.set_visible(False)
star_name_label_box_2.set_visible(False)
star_mass_label_box_2.set_visible(False)
star_luminosity_label_box_2.set_visible(False)

# ПОЛЯ ВВОДА ОТНОСИТЕЛЬНАЯ ОРБИТА ЗВЕЗД

stars_orbit_fields_title = plt.axes([label_box_vidgets_x_min, stars_orbit_vidgets_y_max, textbox_width, textbox_height])
stars_orbit_fields_title.axis('off')
stars_orbit_fields_title.text(0, 0.5, 'ОТНОСИТЕЛЬНАЯ ОРБИТА ЗВЕЗД', va='center', fontsize=font_size_vidgets, fontweight='bold')

stars_semi_major_axis_box = plt.axes([textbox_vidgets_x_min, stars_orbit_vidgets_y_max - delta_y, textbox_width, textbox_height])
stars_eccentricity_box = plt.axes([textbox_vidgets_x_min, stars_orbit_vidgets_y_max - delta_y*2, textbox_width, textbox_height])

stars_semi_major_axis_label_box = plt.axes([label_box_vidgets_x_min, stars_orbit_vidgets_y_max - delta_y - 0.01, label_box_width, label_box_height])
stars_eccentricity_label_box = plt.axes([label_box_vidgets_x_min, stars_orbit_vidgets_y_max - delta_y*2 - 0.01, label_box_width, label_box_height])

for label_box in [stars_semi_major_axis_label_box, stars_eccentricity_label_box]:
    label_box.axis('off')

stars_semi_major_axis_label_box.text(0, 0.5, 'Большая полуось\nорбиты, а.е.:', va='center', fontsize=font_size_vidgets)
stars_eccentricity_label_box.text(0, 0.5, 'Эксцентриситет\nорбиты:', va='center', fontsize=font_size_vidgets)

stars_semi_major_axis_au_textbox = TextBox(stars_semi_major_axis_box, '', initial=1)
stars_eccentricity_textbox = TextBox(stars_eccentricity_box, '', initial=0)

for textbox in [stars_semi_major_axis_au_textbox, stars_eccentricity_textbox]:
    textbox.text_disp.set_size(font_size_vidgets)

stars_orbit_fields_title.set_visible(False)
stars_semi_major_axis_box.set_visible(False)
stars_eccentricity_box.set_visible(False)
stars_semi_major_axis_label_box.set_visible(False)
stars_eccentricity_label_box.set_visible(False)

# ПОЛЯ ВВОДА ПЛАНЕТА

planet_fields_title = plt.axes([label_box_vidgets_x_min, planet_vidgets_y_max, textbox_width, textbox_height])
planet_fields_title.axis('off')
planet_fields_title.text(0, 0.5, 'ПЛАНЕТА', va='center', fontsize=font_size_vidgets, fontweight='bold')

planet_name_box = plt.axes([textbox_vidgets_x_min, planet_vidgets_y_max - delta_y, textbox_width, textbox_height])
planet_semi_major_axis_box = plt.axes([textbox_vidgets_x_min, planet_vidgets_y_max - delta_y*2, textbox_width, textbox_height])
planet_eccentricity_box = plt.axes([textbox_vidgets_x_min, planet_vidgets_y_max - delta_y*3, textbox_width, textbox_height])
planet_bond_albedo_box = plt.axes([textbox_vidgets_x_min, planet_vidgets_y_max - delta_y*4, textbox_width, textbox_height])
planet_emissivity_box = plt.axes([textbox_vidgets_x_min, planet_vidgets_y_max - delta_y*5, textbox_width, textbox_height])
planet_redistribution_factor_box = plt.axes([textbox_vidgets_x_min, planet_vidgets_y_max - delta_y*6, textbox_width, textbox_height])

planet_name_label_box = plt.axes([label_box_vidgets_x_min, planet_vidgets_y_max - delta_y - 0.01, label_box_width, label_box_height])
planet_semi_major_axis_label_box = plt.axes([label_box_vidgets_x_min, planet_vidgets_y_max - delta_y*2 - 0.01, label_box_width, label_box_height])
planet_eccentricity_label_box = plt.axes([label_box_vidgets_x_min, planet_vidgets_y_max - delta_y*3 - 0.01, label_box_width, label_box_height])
planet_bond_albedo_label_box = plt.axes([label_box_vidgets_x_min, planet_vidgets_y_max - delta_y*4 - 0.01, label_box_width, label_box_height])
planet_emissivity_label_box = plt.axes([label_box_vidgets_x_min, planet_vidgets_y_max - delta_y*5 - 0.01, label_box_width, label_box_height])
planet_redistribution_factor_label_box = plt.axes([label_box_vidgets_x_min, planet_vidgets_y_max - delta_y*6 - 0.01, label_box_width, label_box_height])


for label_box in [planet_name_label_box, planet_semi_major_axis_label_box, planet_eccentricity_label_box, planet_bond_albedo_label_box, planet_emissivity_label_box, planet_redistribution_factor_label_box]:
    label_box.axis('off')

planet_name_label_box.text(0, 0.5, 'Название планеты:', va='center', fontsize=font_size_vidgets)
planet_semi_major_axis_label_box.text(0, 0.5, 'Большая полуось\nорбиты, а.е.:', va='center', fontsize=font_size_vidgets)
planet_eccentricity_label_box.text(0, 0.5, 'Эксцентриситет\nорбиты:', va='center', fontsize=font_size_vidgets)
planet_bond_albedo_label_box.text(0, 0.5, 'Албедо:', va='center', fontsize=font_size_vidgets)
planet_emissivity_label_box.text(0, 0.5, 'Степень черноты:', va='center', fontsize=font_size_vidgets)
planet_redistribution_factor_label_box.text(0, 0.5, 'Фактор переизлуча-\nющей поверхности:', va='center', fontsize=font_size_vidgets)

planet_name_textbox = TextBox(planet_name_box, '', initial="Земля")
planet_semi_major_axis_au_textbox = TextBox(planet_semi_major_axis_box, '', initial=1)
planet_eccentricity_textbox = TextBox(planet_eccentricity_box, '', initial=0.0167)
planet_bond_albedo_textbox = TextBox(planet_bond_albedo_box, '', initial=0.3)
planet_emissivity_textbox = TextBox(planet_emissivity_box, '', initial=0.96)
planet_redistribution_factor_textbox = TextBox(planet_redistribution_factor_box, '', initial=1)

for textbox in [planet_name_textbox, planet_semi_major_axis_au_textbox, planet_eccentricity_textbox, planet_bond_albedo_textbox, planet_emissivity_textbox, planet_redistribution_factor_textbox]:
    textbox.text_disp.set_size(font_size_vidgets)

# ФУНКЦИИ СБОРА ДАННЫХ

def _collect_data(event):
    
    # Объявляем, какие переменные нужно будет применять из остального кода и менять глобально
    
    global Z, X, Y
    global warning_label_text
    global star_name_textbox, star_mass_solar_mass_textbox, star_luminosity_solar_luminosity_textbox
    global star_name_textbox_2, star_mass_solar_mass_textbox_2, star_luminosity_solar_luminosity_textbox_2
    global stars_semi_major_axis_au_textbox, stars_eccentricity_textbox
    global planet_name_textbox, planet_semi_major_axis_au_textbox, planet_eccentricity_textbox, planet_bond_albedo_textbox, planet_emissivity_textbox, planet_redistribution_factor_textbox
    global slider_box, data_show_time_label, data_show_time_textbox
    
    # Объявляем, какие переменные будут глобальными
    
    global Z_history, Flux_history, Stars_positions, always_habitable, Star_1, Star_1_label, Star_2, Star_2_label, always_habitable_mesh, stars_coordinates
    global Flux, Planet_positions, Planet_trajectory
    
    # Блокируем некоторые поля ввода для избежания ошибок
    
    slider_box.set_visible(False)
    data_show_time_label.set_visible(False)
    data_show_time_box.set_visible(False)
    
    # Для сохранения памяти очищаем все объекты из предыдущей симуляции, если были
    
    variables = ['Z_history', 'Flux_history', 'Stars_positions', 'always_habitable', 'star', 'star_2', 'stars_relative_orbit', 'thermal_config', 'planet', 'Flux', 'Planet_positions']
    for variable in variables:
        if variable in globals():
                del globals()[variable]
            
    # Считываем данные полей
    
    star_name = star_name_textbox.text
    star_mass_solar_mass = star_mass_solar_mass_textbox.text
    star_luminosity_solar_luminosity = star_luminosity_solar_luminosity_textbox.text
    
    star_name_2 = star_name_textbox_2.text
    star_mass_solar_mass_2 = star_mass_solar_mass_textbox_2.text
    star_luminosity_solar_luminosity_2 = star_luminosity_solar_luminosity_textbox_2.text
    
    stars_semi_major_axis_au = stars_semi_major_axis_au_textbox.text
    stars_eccentricity = stars_eccentricity_textbox.text
    
    planet_name = planet_name_textbox.text
    planet_semi_major_axis_au = planet_semi_major_axis_au_textbox.text
    planet_eccentricity = planet_eccentricity_textbox.text
    planet_bond_albedo = planet_bond_albedo_textbox.text
    planet_emissivity = planet_emissivity_textbox.text
    planet_redistribution_factor =  planet_redistribution_factor_textbox.text
    
    
    
    if system_type_radio.value_selected == 'Одиночная':
        
        if utils.correct_star_mass(star_mass_solar_mass) != True:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_star_mass(star_mass_solar_mass)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
        else:
            star_mass_kg = constants.solar_mass_to_kg(float(star_mass_solar_mass))
                
        if utils.correct_number(star_luminosity_solar_luminosity) == True:
            star_luminosity_w = constants.solar_luminosity_to_watt(float(star_luminosity_solar_luminosity))
        else:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_number(star_luminosity_solar_luminosity)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
            
        star = models.Star(name = star_name, mass_kg = star_mass_kg, luminosity_w = star_luminosity_w)
            
        if utils.correct_number(planet_semi_major_axis_au) == True:
            planet_semi_major_axis_m = constants.au_to_m(float(planet_semi_major_axis_au))
        else:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_number(planet_semi_major_axis_au)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
                
        if utils.correct_eccentricity(planet_eccentricity) != True:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_eccentricity(planet_eccentricity)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
        else:
            planet_eccentricity = float(planet_eccentricity)
            
        if utils.correct_albedo(planet_bond_albedo) != True:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_albedo(planet_bond_albedo)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
        else:
            planet_bond_albedo = float(planet_bond_albedo)
            
        if utils.correct_fraction(planet_emissivity) != True:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_fraction(planet_emissivity)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
        else:
            planet_emissivity = float(planet_emissivity)
            
        if utils.correct_fraction(planet_redistribution_factor) != True:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_fraction(planet_redistribution_factor)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
        else:
            planet_redistribution_factor = float(planet_redistribution_factor)
            
        planet_orbit = models.KeplerOrbit(semi_major_axis_m = planet_semi_major_axis_m, eccentricity = planet_eccentricity)
        planet = models.Planet(name = planet_name, orbit = planet_orbit)
            
        thermal_config = models.ThermalConfig(bond_albedo = planet_bond_albedo, emissivity = planet_emissivity, redistribution_factor = planet_redistribution_factor)
            
        Z, Flux, Planet_positions = physics.single(planet, star, thermal_config, X, Y)
            
        mesh.set_array(Z.ravel())
        
        # Удаляем детали, которые могли остаться от предыдущего графика
        try:
            Star_2.remove()
            Star_2_label.remove()
            always_habitable_mesh.remove()
            Star_1.remove()
            Star_1_label.remove()
            stars_coordinates.remove()
        except Exception:
            try:
                Star_1.remove()
                Star_1_label.remove()
                Planet_trajectory.remove()
            except Exception:
                pass    
        
        #Рисуем звезду
        Star_1 = plt.Circle((0, 0), 0.05, color='black')
        ax.add_patch(Star_1)
        Star_1_label = ax.text(0, 0.15, str(star.name), ha='center')
        
        # Рисуем зону обитаемости
        draw_habitable_zone(Z)
        
        # Рисуем зону обитаемости
        Planet_trajectory, = ax.plot(Planet_positions[:, 0], Planet_positions[:, 1], '--', color='white', linewidth=1.5, label=f'Орбита планеты {planet.name}')
    
    else:
        
        if utils.correct_star_mass(star_mass_solar_mass) != True:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_star_mass(star_mass_solar_mass)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
        else:
            star_mass_kg = constants.solar_mass_to_kg(float(star_mass_solar_mass))
                
        if utils.correct_number(star_luminosity_solar_luminosity) == True:
            star_luminosity_w = constants.solar_luminosity_to_watt(float(star_luminosity_solar_luminosity))
        else:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_number(star_luminosity_solar_luminosity)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
            
        star = models.Star(name = star_name, mass_kg = star_mass_kg, luminosity_w = star_luminosity_w)
        
        if utils.correct_star_mass(star_mass_solar_mass_2) != True:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_star_mass(star_mass_solar_mass_2)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
        else:
            star_mass_kg_2 = constants.solar_mass_to_kg(float(star_mass_solar_mass_2))
                
        if utils.correct_number(star_luminosity_solar_luminosity_2) == True:
            star_luminosity_w_2 = constants.solar_luminosity_to_watt(float(star_luminosity_solar_luminosity_2))
        else:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_number(star_luminosity_solar_luminosity_2)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
            
        star_2 = models.Star(name = star_name_2, mass_kg = star_mass_kg_2, luminosity_w = star_luminosity_w_2)
        
        if utils.correct_number(stars_semi_major_axis_au) == True:
            stars_semi_major_axis_m = constants.au_to_m(float(stars_semi_major_axis_au))
        else:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_number(stars_semi_major_axis_au)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
                
        if utils.correct_eccentricity(stars_eccentricity) != True:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_eccentricity(stars_eccentricity)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
        else:
            stars_eccentricity = float(stars_eccentricity)
            
        stars_relative_orbit = models.KeplerOrbit(semi_major_axis_m = stars_semi_major_axis_m, eccentricity = stars_eccentricity)
        
        if utils.correct_albedo(planet_bond_albedo) != True:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_albedo(planet_bond_albedo)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
        else:
            planet_bond_albedo = float(planet_bond_albedo)
            
        if utils.correct_fraction(planet_emissivity) != True:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_fraction(planet_emissivity)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
        else:
            planet_emissivity = float(planet_emissivity)
            
        if utils.correct_fraction(planet_redistribution_factor) != True:
            warning_lebel_text.set_text(f'!!! WARNING: {utils.correct_fraction(planet_redistribution_factor)}')
            warning_lebel_text.set_color('red')
            warning_lebel_text.set_weight('bold')
            warning_lebel_text.get_bbox_patch().set_edgecolor('red')
            return
        else:
            planet_redistribution_factor = float(planet_redistribution_factor)        
        
        thermal_config = models.ThermalConfig(bond_albedo = planet_bond_albedo, emissivity = planet_emissivity, redistribution_factor = planet_redistribution_factor)
        
        Z_history, Flux_history, Stars_positions, always_habitable = physics.binary(star, star_2, stars_relative_orbit, thermal_config, X, Y)
        
        # Удаление элементов, которые могли остаться с предыдущих итераций
        
        try:
            Star_2.remove()
            Star_2_label.remove()
            always_habitable_mesh.remove()
            Star_1.remove()
            Star_1_label.remove()
            stars_coordinates.remove()
        except Exception:
            try:
                Star_1.remove()
                Star_1_label.remove()
                Planet_trajectory.remove()
            except Exception:
                pass
        
        # Отрисовка массива
        
        idx = int(round(slider.val * (physics.orbit_samples_amount - 1)))
        idx = max(0, min(idx, physics.orbit_samples_amount - 1))
        Z = Z_history[idx, :, :]
        
        mesh.set_array(Z.ravel())
        draw_habitable_zone(Z)
        
        # Всегда обитаемая зона
        
        always_habitable_mesh = ax.contourf(X, Y, always_habitable, levels=[0.5, 1.5], colors=['darkgreen'], alpha=0.35) # levels[0.5, 1.5] ограничивают значения с единицей, то есть True в матрице всегда обитаемой зоны      
        
        # Звезды
        
        Star_1 = plt.Circle((Stars_positions[idx, 0], Stars_positions[idx, 1]), 0.05, color='black')
        ax.add_patch(Star_1)
        Star_1_label = ax.text(Stars_positions[idx, 0], Stars_positions[idx, 1] + 0.15, str(star.name), ha='center')
        
        Star_2 = plt.Circle((Stars_positions[idx, 2], Stars_positions[idx, 3]), 0.05, color='black')
        ax.add_patch(Star_2)
        Star_2_label = ax.text(Stars_positions[idx, 2], Stars_positions[idx, 3] + 0.15, str(star.name), ha='center')
        
        stars_coordinates = ax.text(-3.9, 3.1, f'X1 = {Stars_positions[idx, 0]:.3f}\nY1 = {Stars_positions[idx, 1]:.3f}\nX2 = {Stars_positions[idx, 2]:.3f}\nY2 = {Stars_positions[idx, 3]:.3f}')
        
        slider_box.set_visible(True)
        data_show_time_label.set_visible(True)
        data_show_time_box.set_visible(True)        
    
    
    fig.canvas.draw_idle()

# ------------------------------------------------------------------------------
# ОТСЫЛКА ДАННЫХ НА ОБРАБОТКУ

def collect_data(event):
    global Z, result_ready
    result_ready = False
    
    Z = empty_temperature
    show_data_final_field.set_text('Нет действительного результата расчёта.')
    try:
        with np.errstate(over='raise', divide='raise', invalid='raise'):
            _collect_data(event)
        
        result_ready = 'Flux' in globals() or 'Z_history' in globals()
        if result_ready:
            change_warning_label(None)
    except (MemoryError, FloatingPointError, OverflowError, ValueError) as error:
        Z = empty_temperature
        for name in ('Z_history', 'Flux_history', 'Stars_positions',
                     'always_habitable', 'Flux', 'Planet_positions'):
            globals().pop(name, None)
        slider_box.set_visible(False)
        data_show_time_label.set_visible(False)
        data_show_time_box.set_visible(False)
        if isinstance(error, MemoryError):
            message = 'Недостаточно памяти для расчёта. Закройте другие программы.'
        else:
            message = 'Численный сбой: параметры слишком велики или малы.'
        warning_lebel_text.set_text(message)
        warning_lebel_text.set_color('red')
        warning_lebel_text.set_weight('bold')
        warning_lebel_text.get_bbox_patch().set_edgecolor('red')
    fig.canvas.draw_idle()


start_box = plt.axes([0.02, star_2_vidgets_y_max - 0.02, 0.08, 0.04])
start_button = Button(start_box, "Обработать", color='lightblue', hovercolor='skyblue')
start_button.label.set_fontsize(font_size_vidgets)

start_button.on_clicked(collect_data)

fig.canvas.draw_idle()



# ==============================================================================
# ПОКАЗ ГРАФИКА
# ==============================================================================



plt.show()