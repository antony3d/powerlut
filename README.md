# Power Lut Mod Tool

Инструмент для анализа и модификации кривых крутящего момента двигателей для Assetto Corsa.

## Возможности

- Расчёт мощности (BHP) из крутящего момента (Nm)
- Построение графиков torque/power curves
- Модификация кривых (+X, -X, *X)
- Экспорт в формате ui_car.json
- Экспорт графиков в PNG (300 DPI)
- Подробная статистика (Median, Peak, Power Band)
- Verbose режим для отладки

## Библиотеки

```bash
pip install matplotlib

# Базовый запуск
python powerlut.py power.lut

# С модификатором
python powerlut.py power.lut +10

# Экспорт в PNG
python powerlut.py power.lut -png

# Verbose режим
python powerlut.py power.lut -v

# Комбинированный
python powerlut.py power.lut +10 -v -png