import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
import logging

class SQLUniversalBridge:
    def __init__(self, servidor=r'.\SQLEXPRESS', base_de_datos='BASED'):
        self.params = urllib.parse.quote_plus(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={servidor};'
            f'DATABASE={base_de_datos};'
            f'Trusted_Connection=yes;'
            f'TrustServerCertificate=yes;'
        )
        self.engine = create_engine(f'mssql+pyodbc:///?odbc_connect={self.params}')
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    def procesar_y_subir(self, df, nombre_tabla):
        """Aplica analítica y sube a SQL"""
        try:
            # --- LÓGICA DE NEGOCIO (Analítica Senior) ---
            df['TotalRevenue'] = df['Quantity'] * df['UnitPrice']
            
            # 1. Promedio general para comparar
            media_venta = df['TotalRevenue'].mean()
            df['Venta_Promedio_Global'] = media_venta
            
            # 2. Categorización VIP/Regular
            df['Categoria_Venta'] = df['TotalRevenue'].apply(
                lambda x: 'VIP (Alta)' if x > media_venta else 'Regular (Baja)'
            )
            
            # 3. Categorización de producto
            df['Tipo_Producto'] = df['UnitPrice'].apply(
                lambda x: 'Lujo/Premium' if x > 100 else 'Consumo Masivo'
            )

            # --- SUBIDA A SQL ---
            df.to_sql(nombre_tabla, con=self.engine, if_exists='replace', index=False, chunksize=10000)
            print(f"🔱 ¡ÉPICO! {len(df)} registros analizados y subidos a '{nombre_tabla}'.")
            
        except Exception as e:
            print(f"❌ Error en el proceso: {e}")

# Aquí termina el archivo. No pongas nada más abajo.