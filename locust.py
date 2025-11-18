#Para inciarlo en WEB
#locust -f locust.py --host=http://localhost:8000
#Obtendremos el puerto http://0.0.0.0:8089 en la terminal

from locust import HttpUser, task, between
import random

class ArticulosCategoriaUser(HttpUser):
    wait_time = between(1, 2)
    categorias = ["Economia", "Política", "Deportes", "Cultura", "Entretenimiento", "Salud", "Tecnologia", "Medio Ambiente"]

    @task
    def test_articulos_por_categoria(self):
        # Selecciona una categoría aleatoria
        categoria = random.choice(self.categorias)
        
        with self.client.get(
            f"/api/articulos/api/articulos/por_categoria/?categoria={categoria}",
            headers={"Content-Type": "application/json"},
            catch_response=True,
            name="/api/articulos/api/articulos/por_categoria/?categoria=[categoria]"
        ) as response:
            # Verifica el código de estado
            if response.status_code != 200:
                response.failure(f"Error {response.status_code} con categoría '{categoria}'")
            
            # Opcional: Verifica que la respuesta contenga datos
            try:
                data = response.json()
                if not data.get("results"):
                    response.failure(f"La categoría '{categoria}' no devolvió resultados")
            except:
                response.failure(f"Error al decodificar JSON para categoría '{categoria}'")