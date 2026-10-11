import unittest
from unittest.mock import patch

from app import app, LIMITES_CDE, ubicacion_en_ciudad_del_este


class GeolocalizacionTests(unittest.TestCase):
    def test_puntos_dentro_y_fuera_del_distrito(self):
        puntos = [
            (-25.509, -54.611, True),  # Centro de Ciudad del Este
            (-25.516, -54.633, True),  # Area 1
            (-25.495, -54.691, True),  # Km 9
            (-25.563, -54.611, False),  # Presidente Franco
            (-25.407, -54.643, False),  # Hernandarias
            (-25.505, -54.759, False),  # Minga Guazu
            (-25.547, -54.588, False),  # Foz do Iguacu
        ]
        for lat, lon, esperado in puntos:
            with self.subTest(lat=lat, lon=lon):
                self.assertEqual(ubicacion_en_ciudad_del_este(
                    f"https://www.google.com/maps?q={lat},{lon}"), esperado)

    def test_coordenadas_invalidas(self):
        for valor in ("", "https://example.com/maps?q=-25.509,-54.611",
                      "https://www.google.com/maps?q=nan,-54.611",
                      "https://www.google.com/maps?q=-25.509,inf",
                      "https://www.google.com/maps?q=abc,def",
                      "https://www.google.com/maps?q=91,181"):
            with self.subTest(valor=valor):
                self.assertFalse(ubicacion_en_ciudad_del_este(valor))

    def test_limite_incluido(self):
        punto = LIMITES_CDE[0].boundary.representative_point()
        self.assertTrue(ubicacion_en_ciudad_del_este(
            f"https://www.google.com/maps?q={punto.y},{punto.x}"))

    def test_envio_directo_fuera_no_guarda_reporte(self):
        with app.test_client() as cliente:
            with cliente.session_transaction() as sesion:
                sesion["csrf_token"] = "prueba-geocerca"
            with patch("app.insertar_reporte") as insertar, patch("app.guardar_imagen") as guardar:
                respuesta = cliente.post("/crear_reporte", data={
                    "csrf_token": "prueba-geocerca",
                    "mapa_url": "https://www.google.com/maps?q=-25.563,-54.611",
                }, follow_redirects=True)
                self.assertEqual(respuesta.status_code, 200)
                self.assertIn("dentro del distrito de Ciudad del Este", respuesta.get_data(as_text=True))
                insertar.assert_not_called()
                guardar.assert_not_called()

    def test_geojson_publicado_es_el_usado_por_servidor(self):
        with app.test_client() as cliente:
            respuesta = cliente.get("/api/geojson")
            self.assertEqual(respuesta.status_code, 200)
            self.assertEqual(respuesta.json["features"][0]["properties"]["codigo"], "K04")


if __name__ == "__main__":
    unittest.main()
