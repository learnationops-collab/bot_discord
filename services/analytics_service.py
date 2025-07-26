# Archivo: services/analytics_service.py
# Este servicio maneja la lógica de negocio para el análisis de datos de ventas,
# identificación de tendencias y futuras predicciones.

import datetime
import pandas as pd # Para el análisis de datos
from database.db_manager import DBManager # Importa el gestor de la base de datos

class AnalyticsService:
    """
    Clase que proporciona métodos para analizar datos de ventas,
    identificar tendencias y realizar predicciones.
    Interactúa con DBManager para obtener los datos brutos.
    """
    def __init__(self):
        """
        Inicializa el AnalyticsService y una instancia de DBManager.
        """
        self.db_manager = DBManager()

    async def connect_db(self):
        """
        Intenta conectar el DBManager. Se llama al iniciar el servicio o antes de operaciones.
        """
        if not self.db_manager.connect():
            print("❌ Error: No se pudo conectar a la base de datos de Notion para AnalyticsService.")
            return False
        print("✅ DBManager conectado para AnalyticsService.")
        return True

    async def analyze_sales_trends(self, start_date: str = None, end_date: str = None, product: str = None, region: str = None) -> dict:
        """
        Analiza las tendencias de ventas basándose en los filtros proporcionados.
        Retorna un diccionario con métricas y resúmenes.

        Args:
            start_date (str, optional): Fecha de inicio para el análisis (AAAA-MM-DD).
            end_date (str, optional): Fecha de fin para el análisis (AAAA-MM-DD).
            product (str, optional): Filtra por nombre de producto.
            region (str, optional): Filtra por región.

        Returns:
            dict: Un diccionario con los resultados del análisis, como ventas totales,
                  ventas por producto, ventas por región, etc.
                  Retorna un diccionario vacío si no hay datos o hay un error.
        """
        if not await self.connect_db():
            return {"error": "No se pudo conectar a la base de datos."}

        try:
            sales_data = await self.db_manager.get_sales_data(
                start_date=start_date,
                end_date=end_date,
                product=product,
                region=region
            )

            if not sales_data:
                return {"message": "No se encontraron datos de ventas para el análisis."}

            # Convertir a DataFrame de pandas para facilitar el análisis
            df = pd.DataFrame(sales_data)
            
            # Asegurarse de que 'sales_amount' sea numérico
            df['sales_amount'] = pd.to_numeric(df['sales_amount'], errors='coerce').fillna(0)

            total_sales = df['sales_amount'].sum()
            sales_by_product = df.groupby('product')['sales_amount'].sum().to_dict()
            sales_by_region = df.groupby('region')['sales_amount'].sum().to_dict()

            # Puedes añadir más análisis aquí, como:
            # - Promedio de ventas diarias/semanales
            # - Producto más vendido
            # - Región con mayor crecimiento
            # - Tendencias a lo largo del tiempo (requeriría convertir 'date' a datetime)

            analysis_results = {
                "total_sales": total_sales,
                "sales_by_product": sales_by_product,
                "sales_by_region": sales_by_region,
                "record_count": len(df)
            }
            print(f"Análisis de ventas completado. Registros procesados: {len(df)}")
            return analysis_results

        except Exception as e:
            print(f"Error al analizar tendencias de ventas: {e}")
            return {"error": f"Ocurrió un error durante el análisis: {e}"}

    async def predict_sales(self, period: str = "monthly", num_periods: int = 1) -> dict:
        """
        Realiza una predicción de ventas (placeholder).
        En una implementación real, esto usaría modelos de machine learning.

        Args:
            period (str): El período de tiempo para la predicción (ej. "daily", "weekly", "monthly").
            num_periods (int): Número de períodos a predecir.

        Returns:
            dict: Un diccionario con los resultados de la predicción.
        """
        print(f"Iniciando predicción de ventas para {num_periods} {period}(s)...")
        # Aquí iría la lógica compleja de predicción, por ejemplo:
        # 1. Obtener datos históricos de ventas
        # 2. Preprocesar los datos (manejar nulos, convertir tipos, crear características)
        # 3. Entrenar un modelo de series de tiempo (ARIMA, Prophet, LSTM, etc.)
        # 4. Realizar la predicción
        # 5. Devolver los resultados

        # Placeholder de predicción
        predicted_sales = {
            "period": period,
            "num_periods": num_periods,
            "predicted_amount": 0.0, # Valor de ejemplo
            "confidence_interval": (0.0, 0.0), # Valor de ejemplo
            "message": "La funcionalidad de predicción está en desarrollo. Los datos son ficticios."
        }

        # Simular una predicción simple basada en el último dato o un promedio
        if await self.connect_db():
            try:
                sales_data = await self.db_manager.get_sales_data() # Obtener todos los datos para simular
                if sales_data:
                    df = pd.DataFrame(sales_data)
                    df['sales_amount'] = pd.to_numeric(df['sales_amount'], errors='coerce').fillna(0)
                    if not df.empty:
                        last_month_avg = df['sales_amount'].tail(30).mean() # Promedio del último mes
                        predicted_sales["predicted_amount"] = last_month_avg * num_periods # Predicción simple
                        predicted_sales["confidence_interval"] = (last_month_avg * num_periods * 0.8, last_month_avg * num_periods * 1.2)
                        predicted_sales["message"] = "Predicción basada en un promedio simple de datos históricos recientes."
            except Exception as e:
                print(f"Error en la simulación de predicción: {e}")

        print(f"Predicción de ventas completada para {num_periods} {period}(s).")
        return predicted_sales

# Ejemplo de uso (solo para pruebas, no se ejecutará directamente en el bot)
if __name__ == "__main__":
    # Para ejecutar este ejemplo, asegúrate de tener las variables de entorno de Notion
    # (NOTION_TOKEN, NOTION_DATABASE_SALES_ID) configuradas en tu .env

    async def test_analytics_service():
        from dotenv import load_dotenv
        load_dotenv()

        service = AnalyticsService()

        # Prueba de análisis de tendencias
        print("\n--- Probando análisis de tendencias de ventas ---")
        analysis_results = await service.analyze_sales_trends(
            start_date="2025-01-01",
            end_date="2025-12-31"
        )
        print("Resultados del análisis:")
        for key, value in analysis_results.items():
            print(f"  {key}: {value}")

        # Prueba de predicción de ventas
        print("\n--- Probando predicción de ventas ---")
        prediction_results = await service.predict_sales(period="quarterly", num_periods=2)
        print("Resultados de la predicción:")
        for key, value in prediction_results.items():
            print(f"  {key}: {value}")

        # Cerrar la conexión de la base de datos al finalizar las pruebas
        service.db_manager.close()

    import asyncio
    asyncio.run(test_analytics_service())
