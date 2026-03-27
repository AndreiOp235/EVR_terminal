import os

# pune aici calea către folderul tău
folder_path = r"D:\WIP\EVR\EVR_terminal\CSV-uri"

for name in os.listdir(folder_path):
    old_path = os.path.join(folder_path, name)
    
    if os.path.isdir(old_path) and name.startswith("TEMP_"):
        try:
            # extrage numărul
            num = int(name.split("_")[1])
            
            # formatează la 3 cifre
            formatted = f"{num:03d}"
            
            # noul nume: "0xx xxx"
            new_name = f"TEMP_{formatted}"
            new_path = os.path.join(folder_path, new_name)
            
            os.rename(old_path, new_path)
            print(f"{name} -> {new_name}")
        
        except Exception as e:
            print(f"Eroare la {name}: {e}")