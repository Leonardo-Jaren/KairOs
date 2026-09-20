import os
import sys
import time
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

def verificar_permisos_sync():
    output_dir = Path('docs/capturas_verificacion')
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_dir = Path(r'C:\Users\leona\.gemini\antigravity\brain\b6337a83-82d0-4659-944e-de724c8ee01e')

    # 0. Limpiar permisos personalizados previos de Jorge para comenzar con plantilla base de tecnico
    backend_dir = Path(__file__).resolve().parent.parent / 'backend'
    sys.path.insert(0, str(backend_dir))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
    import django
    django.setup()
    from usuarios.models import PermisoPersonalizado, Usuario
    u = Usuario.objects.filter(username='tecnico_soporte').first()
    if u:
        PermisoPersonalizado.objects.filter(usuario=u).delete()
    print("   Permisos previos de Jorge eliminados, listo para prueba.")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)

        # Contexto 1: Admin
        context_admin = browser.new_context(viewport={'width': 1440, 'height': 900})
        page_admin = context_admin.new_page()

        # Contexto 2: Jorge Alvarez (Técnico)
        context_tecnico = browser.new_context(viewport={'width': 1440, 'height': 900})
        page_tecnico = context_tecnico.new_page()

        print("1. Iniciando sesion como Jorge Alvarez (Técnico) en contexto 2...")
        page_tecnico.goto('http://localhost:5173/auth/login')
        page_tecnico.wait_for_load_state('networkidle')
        page_tecnico.fill('#correo', 'tecnico@kairos.test')
        page_tecnico.fill('#password', 'Admin123!')
        page_tecnico.click('#btn-iniciar')
        page_tecnico.wait_for_url('**/dashboard**', timeout=15000)
        page_tecnico.wait_for_load_state('networkidle')

        # Captura 1: Navbar inicial del técnico (con Software e Instalaciones)
        time.sleep(2)
        sidebar_tecnico = page_tecnico.locator('aside')
        path_01 = output_dir / '01_tecnico_navbar_con_software.png'
        sidebar_tecnico.screenshot(path=str(path_01))
        print(f"   Captura 1 guardada: {path_01}")

        # Comprobar que inicialmente ve Software
        tiene_software_inicial = page_tecnico.locator("aside nav a:has-text('Software')").count() > 0
        print(f"   Técnico tiene enlace Software inicialmente: {tiene_software_inicial}")

        print("2. Iniciando sesion como Admin en contexto 1...")
        page_admin.goto('http://localhost:5173/auth/login')
        page_admin.wait_for_load_state('networkidle')
        page_admin.fill('#correo', 'admin@kairos.test')
        page_admin.fill('#password', 'Admin123!')
        page_admin.click('#btn-iniciar')
        page_admin.wait_for_url('**/dashboard**', timeout=15000)
        page_admin.wait_for_load_state('networkidle')

        print("3. Admin navega a /usuarios y abre modal de permisos para Jorge Alvarez...")
        page_admin.goto('http://localhost:5173/usuarios')
        page_admin.wait_for_load_state('networkidle')
        time.sleep(2)

        # Buscar a Jorge Alvarez en la tabla y abrir su modal de permisos
        row_jorge = page_admin.locator("tr:has-text('Jorge Alvarez')")
        row_jorge.wait_for(state='visible', timeout=10000)
        btn_permisos = row_jorge.locator("button[aria-label='Gestionar permisos']")
        btn_permisos.click()

        modal = page_admin.locator("div[role='dialog'][aria-label='Matriz de Permisos Granulares (CRUD)']")
        modal.wait_for(state='visible', timeout=10000)
        time.sleep(1.5)

        # Captura 2: Modal con los iconos del navbar en la primera columna
        path_02 = output_dir / '02_matriz_permisos_con_iconos_navbar.png'
        modal.locator('section').screenshot(path=str(path_02))
        print(f"   Captura 2 guardada: {path_02}")

        print("4. Revocando permiso de 'Software y Licencias' (VER) para Jorge Alvarez...")
        fila_software = modal.locator("tr:has-text('Software y Licencias')")
        checkbox_ver_software = fila_software.locator("input[type='checkbox']").first
        checkbox_ver_software.click(force=True)
        time.sleep(0.5)

        # Guardar cambios
        btn_guardar = modal.locator("button:has-text('Guardar permisos')")
        btn_guardar.click()
        time.sleep(2)
        print("   Permisos guardados por el Administrador.")

        print("5. Técnico en sesión activa hace clic en Software (disparando 403 Forbidden y sincronización)...")
        page_tecnico.bring_to_front()
        # Hacer clic en Software en el navbar del técnico
        enlace_software = page_tecnico.locator("aside nav a:has-text('Software')")
        if enlace_software.count() > 0:
            enlace_software.click()
            time.sleep(2)
            page_tecnico.wait_for_load_state('networkidle')

        # Comprobar si 'Software' desapareció del navbar tras recibir el 403 y actualizar perfil
        tiene_software_despues = page_tecnico.locator("aside nav a:has-text('Software')").count() > 0
        print(f"   Técnico tiene enlace Software después de revocación y 403: {tiene_software_despues}")

        # Captura 3: Navbar del técnico actualizado (sin Software ni Instalaciones)
        path_03 = output_dir / '03_tecnico_navbar_sin_software.png'
        sidebar_tecnico.screenshot(path=str(path_03))
        print(f"   Captura 3 guardada: {path_03}")

        # Intentar navegación directa a /software
        print("6. Técnico intenta navegar directamente a /software...")
        page_tecnico.goto('http://localhost:5173/software')
        time.sleep(2)
        page_tecnico.wait_for_load_state('networkidle')
        print(f"   URL resultante: {page_tecnico.url}")

        path_04 = output_dir / '04_tecnico_intento_navegacion_software_redirect.png'
        page_tecnico.screenshot(path=str(path_04))
        print(f"   Captura 4 guardada: {path_04}")

        # 7. Restaurar permisos para dejar el usuario limpio
        print("7. Restaurando permisos de Jorge Alvarez a plantilla de rol...")
        page_admin.bring_to_front()
        btn_permisos.click()
        modal.wait_for(state='visible', timeout=10000)
        time.sleep(1)
        btn_reset = modal.locator("button:has-text('Restablecer a plantilla del rol')")
        if btn_reset.is_enabled():
            btn_reset.click()
            time.sleep(1.5)
            print("   Permisos de Jorge restablecidos exitosamente.")

        # Copiar todas las capturas a artifacts
        for p_file in [path_01, path_02, path_03, path_04]:
            if p_file.exists():
                shutil.copy(p_file, artifact_dir / p_file.name)
                print(f"   Copiado a artifacts: {p_file.name}")

        browser.close()
        print("Verificación Playwright completada con éxito.")

if __name__ == '__main__':
    verificar_permisos_sync()
