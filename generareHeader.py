import csv

# --- Config ---
input_csv = "adc_temp.csv"
output_header = "temp_lut.h"
array_name = "temp_lut"

scale = 1   # pentru 2 zecimale (ex: 25.34 -> 2534)
ctype = "uint16_t"  # tipul in C
offset = 0  # daca vrei sa adaugi un offset (ex: -40 pentru a avea 0 la -40C)

# --- Citire CSV ---
adc_values = []
temp_values = []

with open(input_csv, newline='') as csvfile:
    reader = csv.reader(csvfile)
    
    header = next(reader)  # skip header
    
    for row in reader:
        adc = int(float(row[0]))
        temp = float(row[1])
        
        adc_values.append(adc)
        temp_values.append(int(round((temp + offset) * scale)))

# --- Generare header ---
with open(output_header, "w") as f:
    
    f.write("#ifndef TEMP_LUT_H\n")
    f.write("#define TEMP_LUT_H\n\n")
    
    f.write("#include <stdint.h>\n\n")
    
    f.write(f"#define LUT_SIZE {len(temp_values)}\n\n")
    
    f.write(f"static const {ctype} {array_name}[LUT_SIZE] = {{\n")
    
    # scriere valori (format frumos)
    for i, val in enumerate(temp_values):
        if i % 8 == 0:
            f.write("    ")
        
        f.write(f"{val}")
        
        if i != len(temp_values) - 1:
            f.write(", ")
        
        if (i + 1) % 8 == 0:
            f.write("\n")
    
    f.write("\n};\n\n")
    
    f.write("#endif // TEMP_LUT_H\n")

print("Header generat:", output_header)