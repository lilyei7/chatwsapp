import sys
import pandas as pd
from openpyxl import load_workbook

data = {
    'Nombre': [sys.argv[1]],
    'Teléfono': [sys.argv[2]],
    'Correo': [sys.argv[3]],
    'Fecha Reserva': [sys.argv[4]],
    'Personas': [sys.argv[5]],
    'Preferencia': [sys.argv[6]],
    'Cumpleaños': [sys.argv[7]],
    'Comentarios': [sys.argv[8]]
}

df = pd.DataFrame(data)

file_path = 'path/to/cabaret_clientes.xlsx'

try:
    book = load_workbook(file_path)
    writer = pd.ExcelWriter(file_path, engine='openpyxl')
    writer.book = book
    writer.sheets = {ws.title: ws for ws in book.worksheets}
    reader = pd.read_excel(file_path)
    df.to_excel(writer, index=False, header=False, startrow=len(reader) + 1)
    writer.close()
except FileNotFoundError:
    df.to_excel(file_path, index=False)

print('Reserva guardada exitosamente')