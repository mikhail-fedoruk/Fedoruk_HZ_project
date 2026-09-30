import numpy as np
import utils as utils
import models as models
import physics as physics
import constants as constants

orbit_samples_amount = 1001

def Kepler(mean_anomaly, excentricity, tol=1e-10, max_iter=100):
    # Если орбита круговая, эксцентрическая аномалия равна средней
    if excentricity == 0:
        return mean_anomaly
        
    # Начальное приближение для метода Ньютона
    eccentric_anomaly = mean_anomaly if excentricity < 0.8 else np.pi 
        
    for _ in range(max_iter):
        # f(eccentric_anomaly) = eccentric_anomaly - excentricity * sin(eccentric_anomaly) - mean_anomaly
        f = eccentric_anomaly - excentricity * np.sin(eccentric_anomaly) - mean_anomaly
        # Производная f'(eccentric_anomaly) = 1 - excentricity * cos(eccentric_anomaly)
        df = 1 - excentricity * np.cos(eccentric_anomaly)
            
        eccentric_anomaly_next = eccentric_anomaly - f / df
            
        # Если нужная точность достигнута — выходим
        if np.abs(eccentric_anomaly_next - eccentric_anomaly) < tol:
            return eccentric_anomaly_next
            
        eccentric_anomaly = eccentric_anomaly_next
            
    # Если цикл завершился, возвращаем последнее значение
    return eccentric_anomaly


def single(planet, star, thermal_config, X, Y):
    
    # Сетка температур
    
    Distance_from_star = constants.au_to_m(np.sqrt((X - 0)**2 + (Y - 0)**2))
    
    Flux = star.luminosity_w / (4 * np.pi * Distance_from_star**2)
    
    Z = ((Flux * (1 - thermal_config.bond_albedo)) / (4 * thermal_config.redistribution_factor * thermal_config.emissivity * constants.SIGMA_SB))**0.25 - 273.15
    
    # Нанесение орбиты планеты
    
    t = np.linspace(0, 2 * np.pi, orbit_samples_amount)
    
    Planet_positions = np.zeros((len(t), 2))
    
    r = (planet.orbit.semi_major_axis_m * (1 - planet.orbit.eccentricity**2)) / (1 + planet.orbit.eccentricity * np.cos(t))
    
    orbit_x = r * np.cos(t)
    orbit_y = r * np.sin(t)
    
    Planet_positions[:, 0] = constants.m_to_au(orbit_x)
    Planet_positions[:, 1] = constants.m_to_au(orbit_y)
    
    return Z, Flux, Planet_positions


def binary(star, star_2, stars_relative_orbit, thermal_config, X, Y):
    
    star_1_semi_major_axis = stars_relative_orbit.semi_major_axis_m * star_2.mass_kg / (star_2.mass_kg + star.mass_kg)
    star_2_semi_major_axis = stars_relative_orbit.semi_major_axis_m * star.mass_kg / (star_2.mass_kg + star.mass_kg)
    
    orbit_time_samples = np.linspace(0, 1, orbit_samples_amount)
    
    Z_min = np.full_like(X, 1e9)
    Z_max = np.full_like(X, -1e9)
    
    grid_shape = X.shape
    
    Stars_positions = np.zeros((len(orbit_time_samples), 4))
    Z_history = np.zeros((len(orbit_time_samples), grid_shape[0], grid_shape[1]))
    Flux_history = np.zeros((len(orbit_time_samples), grid_shape[0], grid_shape[1]))
    
    for i, orbit_time in enumerate(orbit_time_samples):
        
        mean_anomaly = 2 * np.pi * orbit_time # средняя аномалия
        
        # находим эксцентрическую аномалию для нахождения положения звезд
        eccentric_anomaly = Kepler(mean_anomaly, stars_relative_orbit.eccentricity)
        
        # положения звезд в это время через эксцентрическую аномалию
        star_1_x = -star_1_semi_major_axis * (np.cos(eccentric_anomaly)-stars_relative_orbit.eccentricity)
        star_1_y = -star_1_semi_major_axis * np.sqrt(1 - stars_relative_orbit.eccentricity**2) * np.sin(eccentric_anomaly)
        star_2_x = star_2_semi_major_axis * (np.cos(eccentric_anomaly)-stars_relative_orbit.eccentricity)
        star_2_y = star_2_semi_major_axis * np.sqrt(1 - stars_relative_orbit.eccentricity**2) * np.sin(eccentric_anomaly)
        
        # расстояния от звезд до точек сетки и расчет сумм. освещенности в этих точках
        Distance_from_star_1 = np.sqrt((constants.au_to_m(X) - star_1_x)**2 + (constants.au_to_m(Y) - star_1_y)**2)
        Distance_from_star_2 = np.sqrt((constants.au_to_m(X) - star_2_x)**2 + (constants.au_to_m(Y) - star_2_y)**2)
        Distance_from_star_1 = np.where(Distance_from_star_1 == 0, 1e-5, Distance_from_star_1)
        Distance_from_star_2 = np.where(Distance_from_star_2 == 0, 1e-5, Distance_from_star_2)

        Flux = star.luminosity_w / (4 * np.pi * Distance_from_star_1**2) + star_2.luminosity_w / (4 * np.pi * Distance_from_star_2**2)
        Z = ((Flux * (1 - thermal_config.bond_albedo)) / (4 * thermal_config.redistribution_factor * thermal_config.emissivity * constants.SIGMA_SB))**0.25 - 273.15
        
        #определение и обновление минимальной и максимальной температур в каждой точке за весь период обращения звезд
        Z_min = np.minimum(Z_min, Z)
        Z_max = np.maximum(Z_max, Z)
        
        # записываем необходимую для симуляции информацию в матрицу
        Z_history[i, :, :] = Z
        Flux_history[i, :, :] = Flux
        Stars_positions[i, 0] = constants.m_to_au(star_1_x)
        Stars_positions[i, 1] = constants.m_to_au(star_1_y)
        Stars_positions[i, 2] = constants.m_to_au(star_2_x)
        Stars_positions[i, 3] = constants.m_to_au(star_2_y)
        
    always_habitable = (Z_min >= 0) & (Z_max <= 100)
    
    
    return Z_history, Flux_history, Stars_positions, always_habitable

