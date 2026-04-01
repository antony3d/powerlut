#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ кривой крутящего момента (Nm) и мощности (BHP) из .lut файла.
Входные данные: крутящий момент в Ньютон-метрах (Nm).
Отображение: мощность в лошадиных силах (BHP), момент в Ньютон-метрах (Nm).

Analysis of torque (Nm) and power (BHP) curves from .lut file.
Input: torque in Newton-meters (Nm).
Output: power in brake horsepower (BHP), torque in Newton-meters (Nm).
"""

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import sys
import os
import argparse
import json
import statistics
import bisect
from typing import List, Tuple, Optional, Dict


# =============================================================================
# CONST
# =============================================================================

NAME = "Power lut mod"
VERSION = "0.9.6"
NM_RPM_TO_KW = 9549.3  # Nm | RPM to kVt
NM_RPM_TO_BHP = 7121.0  # Nm | RPM to BHP
BG_COLOR = (28/255, 20/255, 20/255)  # backgrnd for graphics
DEFAULT_FILE = "power.lut"  

# Глобальный флаг verbose режима
# Global flag for verbose mode
VERBOSE = False

def parse_lut_file(filepath: str) -> Tuple[List[float], List[float]]:
    """
    Парсинг .lut файла с форматом RPM|Момент(Nm).

    Args:
        filepath: Путь к файлу .lut

    Returns:
        Tuple с двумя списками: (rpm_values, torque_nm_values)

    Parse .lut file with RPM|Torque(Nm) format.

    Args:
        filepath: Path to .lut file

    Returns:
        Tuple with two lists: (rpm_values, torque_nm_values)
    """
    rpm_list = []
    torque_list = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                parts = line.split('|')
                if len(parts) != 2:
                    raise ValueError(
                        f"Expected 2 values, got {len(parts)}"
                    )

                rpm = float(parts[0].strip())
                torque = float(parts[1].strip())

                rpm_list.append(rpm)
                torque_list.append(torque)

            except (ValueError, IndexError) as e:
                print(
                    f"Warning: Skipping line {line_num}: {line} ({e})"
                )
                continue

    if not rpm_list:
        raise ValueError("No valid data points found in file")

    if VERBOSE:
        print(f"\n[DEBUG] parse_lut_file:")
        print(f"  File: {filepath}")
        print(f"  Points loaded: {len(rpm_list)}")
        print(
            f"  RPM range: {rpm_list[0]:.0f} - {rpm_list[-1]:.0f}"
        )
        print(
            f"  Torque range: {min(torque_list):.2f} - "
            f"{max(torque_list):.2f} Nm"
        )

    return rpm_list, torque_list


def calculate_power_bhp(
    rpm: List[float],
    torque_nm: List[float]
) -> List[float]:
    """
    Расчёт кривой мощности из момента (Nm) и оборотов.

    Формула: P(BHP) = T(Nm) × RPM / 7121

    Args:
        rpm: Список оборотов двигателя (RPM)
        torque_nm: Список значений крутящего момента в Nm

    Returns:
        List[float]: Мощность в лошадиных силах (BHP)

    Calculate power curve from torque (Nm) and RPM data.

    Formula: P(BHP) = T(Nm) × RPM / 7121

    Args:
        rpm: List of engine RPM values
        torque_nm: List of torque values in Nm

    Returns:
        List[float]: Power in brake horsepower (BHP)
    """
    power = []
    for r, t in zip(rpm, torque_nm):
        if r > 0:
            p = t * r / NM_RPM_TO_BHP
        else:
            p = 0.0
        power.append(p)

    if VERBOSE:
        print(f"\n[DEBUG] calculate_power_bhp:")
        print(f"  Input torque points: {len(torque_nm)}")
        print(
            f"  Output power range: {min(power):.2f} - "
            f"{max(power):.2f} BHP"
        )
        if max(power) > 0:
            peak_idx = power.index(max(power))
            print(
                f"  Peak power: {max(power):.2f} BHP @ "
                f"{rpm[peak_idx]:.0f} RPM"
            )

    return power


def find_working_range(
    rpm: List[float],
    values: List[float],
    is_power: bool = False
) -> Tuple[int, int]:
    """
    Поиск рабочего диапазона с отсечением нулей и резких падений.

    Args:
        rpm: Список оборотов
        values: Список значений
        is_power: Если True — не ищем рост в 2 раза слева (для мощности)

    Returns:
        Tuple: (start_index, end_index)

    Find the working range indices by trimming zeros and sharp drops.

    Args:
        rpm: List of RPM values
        values: List of values
        is_power: If True — don't search for 2x growth on left (for power)

    Returns:
        Tuple: (start_index, end_index)
    """
    if not values:
        return 0, 0

    n = len(values)

    # 1. Находим первый ненулевой элемент слева
    # 1. Find first non-zero element from left
    start_idx = 0
    for i in range(n):
        if values[i] > 0:
            start_idx = i
            break

    # 2. Находим последний ненулевой элемент справа
    # 2. Find last non-zero element from right
    end_idx = n - 1
    for i in range(n - 1, -1, -1):
        if values[i] > 0:
            end_idx = i
            break

    if start_idx >= end_idx:
        if VERBOSE:
            print(
                f"\n[DEBUG] find_working_range: "
                f"No valid range (start={start_idx}, end={end_idx})"
            )
        return start_idx, end_idx

    original_start = start_idx
    original_end = end_idx

    # 3. Для момента: ищем где значение ВЫРОСЛО в 2 раза слева
    # 3. For torque: search where value GREW 2x from left
    if not is_power:
        for i in range(start_idx + 1, end_idx + 1):
            if values[i-1] > 0 and values[i] >= values[i-1] * 2.0:
                start_idx = i
                break

    # 4. Справа: ищем где значение УПАЛО в 2 раза (идём с конца к началу)
    # 4. From right: search where value DROPPED 2x (iterate from end to start)
    for i in range(end_idx, start_idx, -1):
        if values[i] > 0 and values[i-1] > 0:
            if values[i] <= values[i-1] * 0.5:
                end_idx = i - 1
                break

    # 5. Если end_idx < start_idx, используем оригинальные значения
    # 5. If end_idx < start_idx, use original values
    if end_idx < start_idx:
        end_idx = original_end
        if VERBOSE:
            print(
                f"\n[DEBUG] find_working_range: "
                f"Warning! end_idx < start_idx, "
                f"using original_end={end_idx}"
            )

    if VERBOSE:
        print(f"\n[DEBUG] find_working_range:")
        print(f"  Input values: {len(values)} points")
        print(f"  is_power: {is_power}")
        print(
            f"  Start index: {start_idx} "
            f"(RPM: {rpm[start_idx]:.0f}, Value: {values[start_idx]:.2f})"
        )
        print(
            f"  End index: {end_idx} "
            f"(RPM: {rpm[end_idx]:.0f}, Value: {values[end_idx]:.2f})"
        )
        print(
            f"  Working range: {values[start_idx]:.2f} - "
            f"{values[end_idx]:.2f}"
        )

    return start_idx, end_idx


def find_effective_range(
    rpm: List[float],
    values: List[float]
) -> Tuple[Optional[float], Optional[float]]:
    """
    Поиск эффективного диапазона оборотов с отсечением нулей и порогов роста/падения.

    Алгоритм:
    1. Обрезать все нулевые значения слева и справа
    2. Слева: найти где значение выросло в 1.5 раза → начало диапазона
    3. Справа: найти где значение упало в 2 раза → конец диапазона

    Args:
        rpm: Список оборотов
        values: Список значений

    Returns:
        Tuple: (start_rpm, end_rpm) или (None, None)

    Find effective RPM range by trimming zeros and finding growth/drop thresholds.

    Algorithm:
    1. Trim all zero values from left and right
    2. Left: find where value grew 1.5x → start of range
    3. Right: find where value dropped 2x → end of range

    Args:
        rpm: List of RPM values
        values: List of values

    Returns:
        Tuple: (start_rpm, end_rpm) or (None, None)
    """
    if len(values) < 2:
        return None, None

    n = len(values)

    # 1. Находим первый ненулевой элемент слева
    # 1. Find first non-zero element from left
    start_idx = 0
    for i in range(n):
        if values[i] > 0:
            start_idx = i
            break

    # 2. Находим последний ненулевой элемент справа
    # 2. Find last non-zero element from right
    end_idx = n - 1
    for i in range(n - 1, -1, -1):
        if values[i] > 0:
            end_idx = i
            break

    if start_idx >= end_idx:
        return None, None

    original_end = end_idx

    # 3. Слева: ищем где значение ВЫРОСЛО в 1.5 раза
    # 3. From left: search where value GREW 1.5x
    for i in range(start_idx + 1, end_idx + 1):
        if values[i-1] > 0 and values[i] >= values[i-1] * 1.5:
            start_idx = i
            break

    # 4. Справа: идём с конца, ищем где значение УПАЛО в 2 раза
    # 4. From right: iterate from end, search where value DROPPED 2x
    for i in range(end_idx, start_idx, -1):
        if values[i] > 0 and values[i-1] > 0:
            if values[i] <= values[i-1] * 0.5:
                end_idx = i - 1
                break

    # 5. Защита
    # 5. Protection
    if end_idx < start_idx:
        end_idx = original_end

    if VERBOSE:
        print(f"\n[DEBUG] find_effective_range:")
        print(
            f"  Effective range: {rpm[start_idx]:.0f} - "
            f"{rpm[end_idx]:.0f} RPM"
        )

    return rpm[start_idx], rpm[end_idx]


def find_power_band_80percent(
    rpm: List[float],
    power: List[float]
) -> Tuple[Optional[float], Optional[float]]:
    """
    Поиск диапазона оборотов где мощность >= 80% от пиковой.

    Args:
        rpm: Список оборотов
        power: Список значений мощности

    Returns:
        Tuple: (start_rpm, end_rpm)

    Find RPM range where power is >= 80% of peak power.

    Args:
        rpm: List of RPM values
        power: List of power values

    Returns:
        Tuple: (start_rpm, end_rpm)
    """
    if not power:
        return None, None

    max_power = max(power)
    threshold = max_power * 0.8

    start_rpm = None
    end_rpm = None

    for i, p in enumerate(power):
        if p >= threshold:
            start_rpm = rpm[i]
            break

    if start_rpm is not None:
        for i in range(len(power) - 1, -1, -1):
            if power[i] >= threshold:
                end_rpm = rpm[i]
                break

    if VERBOSE:
        print(f"\n[DEBUG] find_power_band_80percent:")
        print(f"  Max power: {max_power:.2f} BHP")
        print(f"  80% threshold: {threshold:.2f} BHP")
        print(f"  Band: {start_rpm} - {end_rpm} RPM")

    return start_rpm, end_rpm


def modify_torque_curve(
    torque: List[float],
    modifier: str
) -> List[float]:
    """
    Применение линейной модификации к значениям момента (в Nm).

    При вычитании (-X) значения не уходят ниже 0.

    Args:
        torque: Исходный список значений момента
        modifier: Строка модификатора (+X, -X, *X)

    Returns:
        List[float]: Модифицированный список момента

    Apply linear modification to torque values (in Nm).

    When subtracting (-X) values don't go below 0.

    Args:
        torque: Original list of torque values
        modifier: Modifier string (+X, -X, *X)

    Returns:
        List[float]: Modified list of torque values
    """
    operator = modifier[0]
    value = float(modifier[1:])

    modified = []
    for t in torque:
        if operator == '+':
            modified.append(t + value)
        elif operator == '-':
            # Защита от отрицательных значений
            # Protection from negative values
            new_val = t - value
            modified.append(max(0.0, new_val))
        elif operator == '*':
            modified.append(t * value)
        else:
            modified.append(t)

    if VERBOSE:
        print(f"\n[DEBUG] modify_torque_curve:")
        print(f"  Modifier: {modifier}")
        print(f"  Operator: {operator}, Value: {value}")
        print(
            f"  Original range: {min(torque):.2f} - "
            f"{max(torque):.2f} Nm"
        )
        print(
            f"  Modified range: {min(modified):.2f} - "
            f"{max(modified):.2f} Nm"
        )
        print(
            f"  Values clamped to 0: "
            f"{sum(1 for m in modified if m == 0.0)}"
        )

    return modified


def save_lut_file(
    filepath: str,
    rpm: List[float],
    torque: List[float]
) -> None:
    """
    Сохранение данных RPM|Момент в .lut файл (в Nm).

    Args:
        filepath: Путь для сохранения
        rpm: Список оборотов
        torque: Список значений момента

    Save RPM|Torque data to .lut file (in Nm).

    Args:
        filepath: Path for saving
        rpm: List of RPM values
        torque: List of torque values
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        for r, t in zip(rpm, torque):
            f.write(f"{r:.0f}|{t:.2f}\n")

    if VERBOSE:
        print(
            f"\n[DEBUG] save_lut_file: "
            f"Saved {len(rpm)} points to {filepath}"
        )


def save_power_file(
    filepath: str,
    rpm: List[float],
    power_bhp: List[float]
) -> None:
    """
    Сохранение данных RPM|Мощность в текстовый файл (в BHP).

    Args:
        filepath: Путь для сохранения
        rpm: Список оборотов
        power_bhp: Список значений мощности (BHP)

    Save RPM|Power data to text file (in BHP).

    Args:
        filepath: Path for saving
        rpm: List of RPM values
        power_bhp: List of power values (BHP)
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# RPM|Power(BHP)\n")
        for r, p in zip(rpm, power_bhp):
            f.write(f"{r:.0f}|{p:.2f}\n")

    if VERBOSE:
        print(
            f"\n[DEBUG] save_power_file: "
            f"Saved {len(rpm)} points to {filepath}"
        )


def interpolate_curve(
    rpm: List[float],
    values: List[float],
    step: int = 100
) -> List[List[float]]:
    """
    Интерполяция значений кривой к фиксированному шагу RPM.

    Args:
        rpm: Список оборотов (исходные данные)
        values: Список значений (момент или мощность)
        step: Шаг интерполяции в RPM (по умолчанию 100)

    Returns:
        List[List[float]]: Массив [[rpm, value], ...] с шагом step

    Interpolate curve values to fixed RPM step.

    Args:
        rpm: List of RPM values (source data)
        values: List of values (torque or power)
        step: Interpolation step in RPM (default 100)

    Returns:
        List[List[float]]: Array [[rpm, value], ...] with step interval
    """
    # Находим максимальные обороты
    # Find maximum RPM
    max_rpm = int(max(rpm))

    # Создаём новый массив с шагом step
    # Create new array with step interval
    interpolated = []
    for r in range(0, max_rpm + step, step):
        # Находим позицию в исходных данных
        # Find position in source data
        idx = bisect.bisect_left(rpm, r)

        # Если точно совпадает
        # If exact match
        if idx < len(rpm) and rpm[idx] == r:
            interpolated.append([r, round(values[idx], 1)])
        # Если между точками — линейная интерполяция
        # If between points — linear interpolation
        elif 0 < idx < len(rpm):
            r0, r1 = rpm[idx-1], rpm[idx]
            v0, v1 = values[idx-1], values[idx]
            if r1 != r0:
                v = v0 + (v1 - v0) * (r - r0) / (r1 - r0)
            else:
                v = v0
            interpolated.append([r, round(v, 1)])
        # Если до первой точки
        # If before first point
        elif idx == 0:
            interpolated.append([r, round(values[0], 1)])
        # Если после последней точки
        # If after last point
        else:
            interpolated.append([r, round(values[-1], 1)])

    return interpolated


def save_json_curves(
    filepath: str,
    rpm: List[float],
    torque_nm: List[float],
    power_bhp: List[float]
) -> None:
    """
    Сохранение кривых момента и мощности в JSON файл в формате ui_car.json.

    Формат (без внешних {}, с запятой в конце, с переводом строки):
    "torqueCurve":[[0,10.0],[100,11.0],...],
    "powerCurve":[[0,0.0],[100,0.5],...]

    Args:
        filepath: Путь для сохранения файла
        rpm: Список оборотов
        torque_nm: Список значений момента (Nm)
        power_bhp: Список значений мощности (BHP)

    Save torque and power curves to JSON file in ui_car.json format.

    Format (no outer {}, with comma at end, with newline):
    "torqueCurve":[[0,10.0],[100,11.0],...],
    "powerCurve":[[0,0.0],[100,0.5],...]

    Args:
        filepath: Path for saving file
        rpm: List of RPM values
        torque_nm: List of torque values (Nm)
        power_bhp: List of power values (BHP)
    """
    # Интерполяция с шагом 100 RPM
    # Interpolation with 100 RPM step
    torque_curve = interpolate_curve(rpm, torque_nm, step=100)
    power_curve = interpolate_curve(rpm, power_bhp, step=100)

    # Формируем строки вручную (без внешних {})
    # Format strings manually (no outer {})
    torque_str = json.dumps(torque_curve, separators=(',', ':'))
    power_str = json.dumps(power_curve, separators=(',', ':'))

    # Собираем финальный формат с переводом строки перед powerCurve
    # Assemble final format with newline before powerCurve
    output = (
        f'"torqueCurve":{torque_str},\n'
        f'"powerCurve":{power_str},'
    )

    # Сохраняем в файл
    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(output)

    if VERBOSE:
        print(f"\n[DEBUG] save_json_curves:")
        print(f"  Saved {len(torque_curve)} points to {filepath}")
        print(f"  RPM step: 100")
        print(
            f"  Torque range: {torque_curve[0]} - {torque_curve[-1]}"
        )
        print(
            f"  Power range: {power_curve[0]} - {power_curve[-1]}"
        )


def calculate_statistics(
    rpm: List[float],
    torque_nm: List[float],
    power_bhp: List[float]
) -> Dict:
    """
    Расчёт статистики медианы и максимума для кривых момента и мощности.

    Только Median (по рабочему диапазону) и Peak.

    Args:
        rpm: Список оборотов
        torque_nm: Список значений момента (Nm)
        power_bhp: Список значений мощности (BHP)

    Returns:
        dict: Словарь со статистикой

    Calculate median and max statistics for torque and power curves.

    Only Median (by working range) and Peak.

    Args:
        rpm: List of RPM values
        torque_nm: List of torque values (Nm)
        power_bhp: List of power values (BHP)

    Returns:
        dict: Dictionary with statistics
    """
    # --- Статистика момента (в Nm) ---
    # --- Torque statistics (in Nm) ---
    max_trq = max(torque_nm)
    max_trq_idx = torque_nm.index(max_trq)
    max_trq_rpm = rpm[max_trq_idx]

    # Медиана по рабочему диапазону (is_power=False для момента)
    # Median by working range (is_power=False for torque)
    start_idx_trq, end_idx_trq = find_working_range(
        rpm, torque_nm, is_power=False
    )
    if start_idx_trq <= end_idx_trq and end_idx_trq < len(torque_nm):
        working_torque = torque_nm[start_idx_trq:end_idx_trq + 1]
        median_trq = (
            statistics.median(working_torque)
            if working_torque else 0.0
        )
    else:
        median_trq = 0.0

    # Эффективный диапазон для момента
    # Effective range for torque
    eff_start_trq, eff_end_trq = find_effective_range(rpm, torque_nm)

    # --- Статистика мощности (в BHP) ---
    # --- Power statistics (in BHP) ---
    max_pwr = max(power_bhp)
    max_pwr_idx = power_bhp.index(max_pwr)
    max_pwr_rpm = rpm[max_pwr_idx]

    # Медиана по рабочему диапазону (is_power=True для мощности!)
    # Median by working range (is_power=True for power!)
    start_idx_pwr, end_idx_pwr = find_working_range(
        rpm, power_bhp, is_power=True
    )
    if start_idx_pwr <= end_idx_pwr and end_idx_pwr < len(power_bhp):
        working_power = power_bhp[start_idx_pwr:end_idx_pwr + 1]
        median_pwr = (
            statistics.median(working_power)
            if working_power else 0.0
        )
    else:
        median_pwr = 0.0

    # Эффективный диапазон для мощности
    # Effective range for power
    eff_start_pwr, eff_end_pwr = find_effective_range(rpm, power_bhp)

    # Power Band (≥80% peak)
    band_start_pwr, band_end_pwr = find_power_band_80percent(
        rpm, power_bhp
    )

    if VERBOSE:
        print(f"\n[DEBUG] calculate_statistics:")
        print(f"  --- TORQUE ---")
        print(
            f"    Max: {max_trq:.2f} Nm @ {max_trq_rpm:.0f} RPM"
        )
        print(
            f"    Median: {median_trq:.2f} Nm "
            f"(range: {start_idx_trq}-{end_idx_trq})"
        )
        print(
            f"    Effective range: {eff_start_trq} - {eff_end_trq} RPM"
        )
        print(f"  --- POWER ---")
        print(
            f"    Max: {max_pwr:.2f} BHP @ {max_pwr_rpm:.0f} RPM"
        )
        print(
            f"    Median: {median_pwr:.2f} BHP "
            f"(range: {start_idx_pwr}-{end_idx_pwr})"
        )
        print(
            f"    Effective range: {eff_start_pwr} - {eff_end_pwr} RPM"
        )
        print(
            f"    Power Band: {band_start_pwr} - {band_end_pwr} RPM"
        )

    return {
        'torque': {
            'median': median_trq,
            'max': max_trq,
            'max_rpm': max_trq_rpm,
            'effective_start': eff_start_trq,
            'effective_end': eff_end_trq
        },
        'power': {
            'median': median_pwr,
            'max': max_pwr,
            'max_rpm': max_pwr_rpm,
            'effective_start': eff_start_pwr,
            'effective_end': eff_end_pwr,
            'band_start': band_start_pwr,
            'band_end': band_end_pwr
        }
    }


def plot_curves(
    rpm: List[float],
    torque_nm: List[float],
    power_bhp: List[float],
    stats: Dict,
    export_png: bool = False,
    source_file: str = 'power.lut'
) -> None:
    """
    Построение графиков момента (Nm) и мощности (BHP) со статистическими линиями.

    Args:
        rpm: Список оборотов для оси X
        torque_nm: Значения момента (Nm)
        power_bhp: Значения мощности (BHP)
        stats: Словарь со статистикой
        export_png: Если True — сохранить в PNG без показа окна
        source_file: Имя исходного файла для имени выходного PNG

    Plot torque (Nm) and power (BHP) curves with statistical reference lines.

    Args:
        rpm: List of RPM for X axis
        torque_nm: Torque values (Nm)
        power_bhp: Power values (BHP)
        stats: Dictionary with statistics
        export_png: If True — save to PNG without showing window
        source_file: Source filename for output PNG name
    """
    fig, ax1 = plt.subplots(figsize=(12, 7))

    # Цвета сетки и осей
    # Grid and axis colors
    grid_color = '#404040'
    label_color = '#CCCCCC'
    tick_color = '#808080'
    color_torque = 'yellow'
    color_power = 'red'
    color_torque_m = 'olive'
    color_power_m = '#901515'

    # Находим общий максимум для обеих осей Y
    # Find common maximum for both Y axes
    max_torque = max(torque_nm) if torque_nm else 0
    max_power = max(power_bhp) if power_bhp else 0
    y_max = max(max_torque, max_power)

    if y_max > 0:
        y_max = ((int(y_max) // 20) + 1) * 20

    # Настраиваем фон графика
    # Configure graph background
    fig.patch.set_facecolor(BG_COLOR)
    ax1.set_facecolor(BG_COLOR)

    # График крутящего момента (левая ось)
    # Torque curve (left axis)
    ax1.set_xlabel('Engine RPM', color=label_color, fontsize=12)
    ax1.set_ylabel('Torque (Nm)', color=color_torque, fontsize=12)
    ax1.plot(
        rpm, torque_nm,
        color=color_torque,
        linewidth=2.5,
        label='Torque'
    )
    ax1.tick_params(
        axis='y',
        labelcolor=color_torque,
        colors=tick_color
    )
    ax1.tick_params(axis='x', colors=tick_color)
    ax1.set_ylim(0, y_max)
    ax1.grid(
        True,
        alpha=0.3,
        color=grid_color,
        linestyle='-'
    )
    ax1.spines['bottom'].set_color(tick_color)
    ax1.spines['top'].set_color(tick_color)
    ax1.spines['left'].set_color(color_torque)
    ax1.spines['right'].set_color(color_power)

    # Вторая ось для мощности
    # Second axis for power
    ax2 = ax1.twinx()
    ax2.set_ylabel('Power (BHP)', color=color_power, fontsize=12)
    ax2.plot(
        rpm, power_bhp,
        color=color_power,
        linewidth=2.5,
        label='Power'
    )
    ax2.tick_params(
        axis='y',
        labelcolor=color_power,
        colors=tick_color
    )
    ax2.set_ylim(0, y_max)
    ax2.spines['right'].set_color(color_power)

    # Горизонтальная пунктирная линия для медианы момента (в Nm)
    # Horizontal dashed line for torque median (in Nm)
    ax1.axhline(
        y=stats['torque']['median'],
        color=color_torque_m,
        linestyle='--',
        linewidth=1.5,
        alpha=0.8,
        label=(
            f"Median Torque: "
            f"{stats['torque']['median']:.1f} Nm"
        )
    )

    # Горизонтальная пунктирная линия для медианы мощности (в BHP)
    # Horizontal dashed line for power median (in BHP)
    ax2.axhline(
        y=stats['power']['median'],
        color=color_power_m,
        linestyle='--',
        linewidth=1.5,
        alpha=0.8,
        label=(
            f"Median Power: "
            f"{stats['power']['median']:.1f} BHP"
        )
    )

    # Вертикальные линии для Power Band (≥80% peak)
    # Vertical lines for Power Band (≥80% peak)
    if stats['power']['band_start'] and stats['power']['band_end']:
        ax2.axvline(
            x=stats['power']['band_start'],
            color='white',
            linestyle=':',
            linewidth=1.5,
            alpha=0.5,
            label=f"Power Band (≥80%)"
        )
        ax2.axvline(
            x=stats['power']['band_end'],
            color='white',
            linestyle=':',
            linewidth=1.5,
            alpha=0.5
        )
        ax2.axvspan(
            stats['power']['band_start'],
            stats['power']['band_end'],
            color='white',
            alpha=0.08
        )

    # Цвет текста заголовка
    # Title text color
    plt.title(
        'Engine Torque (Nm) and Power (BHP) Curve',
        color=label_color,
        fontsize=14
    )

    # Объединяем легенды
    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    legend = ax1.legend(
        lines1 + lines2,
        labels1 + labels2,
        loc='best',
        facecolor=BG_COLOR,
        edgecolor=label_color,
        labelcolor=label_color
    )
    legend.get_frame().set_alpha(0.8)

    fig.tight_layout()

    if VERBOSE:
        print(f"\n[DEBUG] plot_curves:")
        print(f"  Export PNG: {export_png}")
        print(f"  Source file: {source_file}")
        print(f"  Y-axis max: {y_max}")

    # Экспорт в PNG или показ окна
    # Export to PNG or show window
    if export_png:
        output_file = (
            os.path.splitext(source_file)[0] + '_curve.png'
        )
        plt.savefig(
            output_file,
            dpi=300,
            bbox_inches='tight',
            facecolor=BG_COLOR
        )
        print(f"\n✓ Graph saved to '{output_file}'")
        plt.close(fig)
    else:
        plt.show()


def print_console_report(stats: Dict) -> None:
    """
    Вывод статистического отчёта в консоль на английском.

    Только Median и Peak.

    Print statistical report to console in English.

    Only Median and Peak.
    """
    print("\n" + "=" * 60)
    print("ENGINE CURVE STATISTICS REPORT")
    print("=" * 60)

    # Блок момента (в Nm)
    # Torque section (in Nm)
    print(f"\n[TORQUE]")
    print(
        f"  Peak Torque:     {stats['torque']['max']:.2f} Nm @ "
        f"{stats['torque']['max_rpm']:.0f} RPM"
    )
    print(
        f"  Median:          {stats['torque']['median']:.2f} Nm"
    )
    if stats['torque']['effective_start'] and stats['torque']['effective_end']:
        print(
            f"  Effective Range: {stats['torque']['effective_start']:.0f} – "
            f"{stats['torque']['effective_end']:.0f} RPM"
        )
    else:
        print(f"  Effective Range: N/A")

    # Блок мощности (в BHP)
    # Power section (in BHP)
    print(f"\n[POWER]")
    print(
        f"  Peak Power:      {stats['power']['max']:.2f} BHP @ "
        f"{stats['power']['max_rpm']:.0f} RPM"
    )
    if stats['power']['band_start'] and stats['power']['band_end']:
        print(
            f"  Power Band:      {stats['power']['band_start']:.0f} – "
            f"{stats['power']['band_end']:.0f} RPM (≥80% peak)"
        )
    else:
        print(f"  Power Band:      N/A")

    print(
        f"  Median:          {stats['power']['median']:.2f} BHP"
    )
    if stats['power']['effective_start'] and stats['power']['effective_end']:
        print(
            f"  Effective Range: {stats['power']['effective_start']:.0f} – "
            f"{stats['power']['effective_end']:.0f} RPM"
        )
    else:
        print(f"  Effective Range: N/A")

    print("\n" + "=" * 60)


def main():

    global VERBOSE

    print("=" * 30)
    print(f"{NAME} v{VERSION}")
    print("=" * 30)

    parser = argparse.ArgumentParser(
        description=(
            'Analyze engine torque/power curve from .lut file '
            '(torque in Nm, power in BHP)'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python powerlut.py                    # Analyze power.lut, show graph
  python powerlut.py mycar.lut          # Analyze custom file
  python powerlut.py power.lut +10      # Add 10 Nm to torque curve
  python powerlut.py power.lut -5       # Subtract 5 Nm (clamped to 0)
  python powerlut.py power.lut '*1.2'   # Multiply torque curve by 1.2
  python powerlut.py -v -png            # Verbose + PNG export
        '''
    )
    parser.add_argument(
        'file',
        nargs='?',
        default=DEFAULT_FILE,
        help='Path to .lut file (default: power.lut)'
    )
    parser.add_argument(
        'modifier',
        nargs='?',
        default=None,
        help=(
            'Torque modifier (in Nm): '
            '+X (add), -X (subtract), *X (multiply)'
        )
    )
    parser.add_argument(
        '-png',
        action='store_true',
        help=(
            'Export graph to PNG file only (no GUI window). '
            'Output: <filename>_curve.png'
        )
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose mode: print all intermediate calculations to console'
    )

    args = parser.parse_args()

    # Устанавливаем глобальный флаг verbose
    # Set global verbose flag
    VERBOSE = args.verbose

    needs_modification = (
        args.modifier is not None and
        args.modifier[0] in ['+', '-', '*']
    )

    # Шаг 1: Загружаем данные
    # Step 1: Load data
    try:
        rpm, torque_nm = parse_lut_file(args.file)
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found")
        parser.print_help()
        sys.exit(1)
    except ValueError as e:
        print(f"Error parsing file: {e}")
        sys.exit(1)

    # Шаг 2: Применяем модификатор
    # Step 2: Apply modifier
    if needs_modification:
        print(
            f"Applying modifier '{args.modifier}' "
            f"to torque curve (in Nm)..."
        )
        torque_modified = modify_torque_curve(torque_nm, args.modifier)

        base_name = os.path.splitext(args.file)[0]
        mod_file = f"{base_name}.lut_mod"
        save_lut_file(mod_file, rpm, torque_modified)
        print(
            f"Modified curve saved to '{mod_file}' (values in Nm)"
        )

        torque_nm = torque_modified

    # Шаг 3: Рассчитываем мощность
    # Step 3: Calculate power
    power_bhp = calculate_power_bhp(rpm, torque_nm)

    # Шаг 3.5: Сохраняем power_bph.txt в режиме verbose
    # Step 3.5: Save power_bph.txt in verbose mode
    if VERBOSE:
        power_file = os.path.splitext(args.file)[0] + '_bph.txt'
        save_power_file(power_file, rpm, power_bhp)
        print(f"Power data saved to '{power_file}'")

    # Шаг 3.6: Сохраняем кривые в JSON (всегда)
    # Step 3.6: Save curves to JSON (always)
    json_file = os.path.splitext(args.file)[0] + '.json'
    save_json_curves(json_file, rpm, torque_nm, power_bhp)
    print(f"Curves saved to '{json_file}'")

    # Шаг 4: Считаем статистику
    # Step 4: Calculate statistics
    stats = calculate_statistics(rpm, torque_nm, power_bhp)

    # Шаг 5: Вывод в консоль
    # Step 5: Print to console
    print_console_report(stats)

    # Шаг 6: Строим график (с опцией PNG)
    # Step 6: Plot graph (with PNG option)
    plot_curves(
        rpm, torque_nm, power_bhp, stats,
        export_png=args.png,
        source_file=args.file
    )


if __name__ == "__main__":
    main()