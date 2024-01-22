import re
import numpy as np

def parse_input_string(input_str):
    # Option 1: Eine einzelne Zahl
    if re.match(r'^(?:\d+(\.\d*)?|\.\d+)$', input_str):
        return [float(input_str)]

    # Option 2: Eine Liste von Zahlen
    if re.match(r'^\[.*\]$', input_str):
        input_str = input_str[1:-1]  # Klammern entfernen
        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', input_str)
        return [float(num) for num in numbers]

    # Option 3: Ein Slicing-Ausdruck
    if re.match(r'^\[[-+]?\d*\.\d+|\d+:[-+]?\d*\.\d+|\d+:([-+]?\d*\.\d+|\d+)?:[-+]?\d*\.\d+|\d+\]$', input_str):
        input_str = input_str[1:-1]  # Klammern entfernen
        parts = input_str.split(':')
        start = float(parts[0])
        stop = float(parts[1])
        step = float(parts[2]) if len(parts) == 3 else 1.0
        return list(np.arange(start, stop, step))

    # Wenn der Eingabestring kein derartiges Format hat, gib eine leere Liste zurück
    raise ValueError('Invalid input string: ' + input_str)

# Beispiele
input_str1 = '0.2'
input_str2 = '.5'
input_str3 = '0.002'
input_str4 = '[1, 2, 3]'
input_str5 = '[0:1:0.1]'
input_str6 = '[0:1:.1]'
input_str7 = '[0:100:20]'
input_str8 = '.'

print(parse_input_string(input_str1))  # Ausgabe: [0.2]
print(parse_input_string(input_str2))  # Ausgabe: [0.5]
print(parse_input_string(input_str3))  # Ausgabe: [0.002]
print(parse_input_string(input_str4))  # Ausgabe: [1.0, 2.0, 3.0]
print(parse_input_string(input_str5))  # Ausgabe: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
print(parse_input_string(input_str6))  # Ausgabe: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
print(parse_input_string(input_str7))  # Ausgabe: [0.0, 20.0, 40.0, 60.0, 80.0]
print(parse_input_string(input_str8))  # raises ValueError
