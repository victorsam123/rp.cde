import unittest

from cde_deployment import validar_configuracion_cde


class ConfiguracionCDETests(unittest.TestCase):
    def setUp(self):
        self.env = {"CDE_DEPLOYMENT": "1", "MUNICIPALITY_ID": "ciudad_del_este", "DB_HOST": "postgres-cde.railway.internal",
                    "DB_NAME": "rp_cde", "DB_USER": "rp_cde_app", "DB_PASSWORD": "test-only-password",
                    "SECRET_KEY": "a" * 64, "ADMIN_PASSWORD": "test-admin-password", "SESSION_COOKIE_SECURE": "1"}

    def test_configuracion_propia(self):
        validar_configuracion_cde(self.env)

    def test_rechaza_otra_base(self):
        for database in ("railway", "presidente_franco", "rp_franco", ""):
            with self.subTest(database=database):
                with self.assertRaises(RuntimeError):
                    validar_configuracion_cde({**self.env, "DB_NAME": database})

    def test_rechaza_otra_municipalidad(self):
        with self.assertRaises(RuntimeError):
            validar_configuracion_cde({**self.env, "MUNICIPALITY_ID": "presidente_franco"})

    def test_railway_activa_validacion_sin_bandera(self):
        env = {**self.env, "CDE_DEPLOYMENT": "0", "RAILWAY_ENVIRONMENT_ID": "test-environment", "DB_NAME": "railway"}
        with self.assertRaises(RuntimeError):
            validar_configuracion_cde(env)

    def test_rechaza_configuracion_incompleta(self):
        for key in ("DB_HOST", "DB_PASSWORD", "SECRET_KEY", "ADMIN_PASSWORD"):
            with self.subTest(key=key):
                with self.assertRaises(RuntimeError):
                    validar_configuracion_cde({**self.env, key: ""})

    def test_rechaza_secretos_predeterminados(self):
        for change in ({"SECRET_KEY": "corta"}, {"SECRET_KEY": "REEMPLAZAR" + "x" * 40},
                       {"ADMIN_PASSWORD": "Admin@2026!"}, {"SESSION_COOKIE_SECURE": "0"}):
            with self.assertRaises(RuntimeError):
                validar_configuracion_cde({**self.env, **change})

    def test_desarrollo_local_no_cambia_configuracion(self):
        validar_configuracion_cde({})


if __name__ == "__main__":
    unittest.main()
