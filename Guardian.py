import pandas as pd
import logging
import os
import sys
import io
from bridge import SQLUniversalBridge


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


logging.basicConfig(
    level=logging.INFO, 
    format='%(levelname)s: %(message)s'
)

class DataGuardian:
    def __init__(self, archivo_entrada):
        self.archivo = archivo_entrada
        self.df = None
        self.errores = None

    def cargar_y_validar(self):
        """Carga el archivo validando su existencia"""
        if not os.path.exists(self.archivo):
            logging.error(f"ERROR: Archivo no encontrado: {self.archivo}")
            return False
        
        try:
            
            self.df = pd.read_csv(self.archivo, encoding='latin1')
            logging.info(f"DATOS CARGADOS: {len(self.df)} registros.")
            return True
        except Exception as e:
            logging.error(f"ERROR AL LEER CSV: {e}")
            return False

    def auditoria_profunda(self):
        """Limpia y separa datos de calidad de los errores"""
        logging.info("INICIANDO AUDITORIA...")

       
        self.df['Description'] = self.df['Description'].str.strip().str.upper()
        
      
        self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'])
        
       
        self.df['CustomerID'] = self.df['CustomerID'].fillna(0).astype(int)

        mascara_validos = (self.df['UnitPrice'] > 0) & (self.df['Quantity'] > 0)
        
        datos_certificados = self.df[mascara_validos].copy()
        self.errores = self.df[~mascara_validos].copy()

      
        if not self.errores.empty:
            self.errores.to_csv("cuarentena_errores.csv", index=False)
            logging.info(f"REPORTE: {len(self.errores)} errores mandados a 'cuarentena_errores.csv'")

        logging.info(f"CERTIFICACION: {len(datos_certificados)} registros listos.")
        return datos_certificados

# --- FLUJO PRINCIPAL ---
if __name__ == "__main__":
  
    archivo_csv = "CLEANPROYECT.csv" 
    
    guardian = DataGuardian(archivo_csv)
    
    if guardian.cargar_y_validar():
        
        df_para_sql = guardian.auditoria_profunda()
        
       
        try:
            db_sql = SQLUniversalBridge()
           
            db_sql.procesar_y_subir(df_para_sql, "Ventas_Auditadas_Final")
        except Exception as e:
            logging.error(f"ERROR DE CONEXION SQL: {e}")
