import os
import numpy as np
import pandas as pd

# Директория для сохранения файлов
output_directory = 'tests/analysis/correction/check-tables/2021-syntetic-epsilon-iron-III/time_test'
os.makedirs(output_directory, exist_ok=True)

# Количество файлов
num_files = 1000

# Количество строк в каждом файле
num_rows = 160

for file_index in range(num_files):
    # Генерация данных
    temp_values = np.linspace(-193, 0, num_rows)
    tsusc_values = np.linspace(-90, -110, num_rows)
    csusc_values = np.random.uniform(35, 45, num_rows)
    nsusc_values = np.random.uniform(0.8, 1.0, num_rows)
    bulks_values = np.random.uniform(0, 1, num_rows)
    ferrt_values = np.random.uniform(0, 1, num_rows)
    ferrb_values = np.random.uniform(0, 1, num_rows)
    timeec_values = np.random.uniform(0, 200, num_rows)

    # Создание DataFrame
    data = {
        'TEMP': temp_values,
        'TSUSC': tsusc_values,
        'CSUSC': csusc_values,
        'NSUSC': nsusc_values,
        'BULKS': bulks_values,
        'FERRT': ferrt_values,
        'FERRB': ferrb_values,
        'TIMEEC-220111': timeec_values
    }
    df = pd.DataFrame(data)

    file_name = f'generated_data_{file_index + 1}.clw'
    file_path = os.path.join(output_directory, file_name)
    df.to_csv(file_path, sep='\t', index=False, float_format='%.4f')

    print(f"File saved to {file_path}")
