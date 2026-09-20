import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

def verificar_navbar_docente():
    capturas_dir = Path('docs/capturas_verificacion')
    capturas_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        # Iniciar navegador Chrome del sistema en modo headless
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(
            viewport={'width': 1366, 'height': 768},
            device_scale_factor=1.0,
        )
        page = context.new_page()

        print("1. Navegando al formulario de inicio de sesión...")
        page.goto('http://localhost:5173/auth/login')
        page.wait_for_load_state('networkidle')

        print("2. Ingresando credenciales de docente (docente@kairos.test)...")
        page.fill('#correo', 'docente@kairos.test')
        page.fill('#password', 'Admin123!')
        page.click('#btn-iniciar')

        print("3. Esperando carga del panel de control (Dashboard)...")
        page.wait_for_url('**/dashboard**', timeout=15000)
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        # Localizar los enlaces del menú lateral de navegación
        menu_locators = page.locator('aside nav a').all()
        items_encontrados = [loc.inner_text().strip() for loc in menu_locators]
        print(f"Items encontrados en la barra lateral: {items_encontrados}")

        items_esperados = ['Dashboard', 'Software', 'Instalaciones', 'Incidencias']
        items_prohibidos = [
            'Campus',
            'Espacios',
            'Usuarios por espacio',
            'Equipos',
            'Componentes',
            'Mantenimiento',
            'Historial',
            'Usuarios',
        ]

        # Comprobar que los items esperados estén presentes
        for esperado in items_esperados:
            assert esperado in items_encontrados, f"Falta el modulo autorizado: {esperado}"

        # Comprobar que ningún item prohibido esté presente
        for prohibido in items_prohibidos:
            assert prohibido not in items_encontrados, f"Se encontro modulo no autorizado para docente: {prohibido}"

        print("Verificacion exitosa: La barra lateral solo contiene los 4 modulos autorizados.")

        # Tomar captura de pantalla completa del panel con la barra lateral
        screenshot_full = capturas_dir / '01_docente_dashboard_navbar.png'
        page.screenshot(path=str(screenshot_full))
        print(f"Captura general guardada en: {screenshot_full}")

        # Tomar captura detallada enfocada en la barra lateral
        sidebar_locator = page.locator('aside')
        screenshot_sidebar = capturas_dir / '02_docente_sidebar_zoom.png'
        sidebar_locator.screenshot(path=str(screenshot_sidebar))
        print(f"Captura de barra lateral guardada en: {screenshot_sidebar}")

        # Probar navegacion a Software para confirmar acceso
        print("4. Navegando al modulo de Software...")
        page.click('aside nav a:has-text("Software")')
        page.wait_for_url('**/software**', timeout=10000)
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        screenshot_software = capturas_dir / '03_docente_modulo_software.png'
        page.screenshot(path=str(screenshot_software))
        print(f"Captura de modulo software guardada en: {screenshot_software}")

        # Probar navegacion a Incidencias para confirmar acceso
        print("5. Navegando al modulo de Incidencias...")
        page.click('aside nav a:has-text("Incidencias")')
        page.wait_for_url('**/incidencias**', timeout=10000)
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        screenshot_incidencias = capturas_dir / '04_docente_modulo_incidencias.png'
        page.screenshot(path=str(screenshot_incidencias))
        print(f"Captura de modulo incidencias guardada en: {screenshot_incidencias}")

        # Intentar acceder a una ruta restringida por URL directa (ej. /espacios)
        print("6. Verificando que la navegacion directa a rutas restringidas sea rechazada...")
        for restricted_path in ['/espacios', '/equipos', '/usuarios']:
            page.goto(f'http://localhost:5173{restricted_path}')
            page.wait_for_load_state('networkidle')
            time.sleep(1)
            current_url = page.url
            print(f"URL resultante al intentar acceder a {restricted_path}: {current_url}")
            assert '/dashboard' in current_url, f"El docente no debio poder acceder a {restricted_path} y debio ser redirigido a /dashboard"

        browser.close()
        print("Verificacion integral completada satisfactoriamente.")


if __name__ == '__main__':
    verificar_navbar_docente()
