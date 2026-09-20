import os
import sys
import time
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

def verificar_organigrama():
    output_dir = Path('docs/capturas_verificacion')
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_dir = Path(r'C:\Users\leona\.gemini\antigravity\brain\b6337a83-82d0-4659-944e-de724c8ee01e')

    # 0. Restablecer supervisor del usuario de prueba para idempotencia
    backend_dir = Path(__file__).resolve().parent.parent / 'backend'
    sys.path.insert(0, str(backend_dir))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
    import django
    django.setup()
    from usuarios.models import Usuario
    u = Usuario.objects.filter(correo='leonardojarenceferino123@gmail.com').first()
    if u:
        u.supervisor = None
        u.save(update_fields=['supervisor'])
        print("   Usuario de prueba restablecido (supervisor = None).")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(viewport={'width': 1500, 'height': 950})
        page = context.new_page()
        page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
        page.on("response", lambda resp: print(f"HTTP {resp.status} {resp.url}") if '/usuarios/' in resp.url else None)

        print("1. Iniciando sesion como SuperAdmin...")
        page.goto('http://localhost:5173/auth/login')
        page.wait_for_load_state('networkidle')
        page.fill('#correo', 'admin@kairos.test')
        page.fill('#password', 'Admin123!')
        page.click('#btn-iniciar')

        page.wait_for_url('**/dashboard**', timeout=15000)
        page.wait_for_load_state('networkidle')
        print("   Sesion iniciada exitosamente.")

        print("2. Navegando a /usuarios y cambiando a vista Organigrama...")
        page.goto('http://localhost:5173/usuarios')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        # Clic en el boton Organigrama
        btn_organigrama = page.locator("button:has-text('Organigrama')")
        btn_organigrama.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

        # Captura 1: Vista compacta y centrada de Linea de Mando
        print("3. Capturando vista Linea de Mando...")
        canvas = page.locator("div.relative.w-full.h-\\[740px\\]")
        canvas.wait_for(state='visible', timeout=10000)
        time.sleep(1)

        path_01 = output_dir / '01_organigrama_linea_mando.png'
        page.screenshot(path=str(path_01))
        print(f"   Captura 1 guardada: {path_01}")

        # Captura 2: Abrir Action Dock en 'Sin Supervisor'
        print("4. Abriendo dock en pestana 'Sin Supervisor'...")
        btn_sin_supervisor = page.locator("button:has-text('Sin Supervisor')")
        btn_sin_supervisor.click()
        time.sleep(1)

        dock = page.locator("aside[aria-label='Panel de accion rapida del organigrama']")
        dock.wait_for(state='visible', timeout=5000)

        path_02 = output_dir / '02_organigrama_dock_sin_supervisor.png'
        page.screenshot(path=str(path_02))
        print(f"   Captura 2 guardada: {path_02}")

        # Captura 3: Cambiar a pestana 'Docentes' en el dock
        print("5. Cambiando a pestana 'Docentes' en el dock...")
        btn_tab_docentes = dock.locator("button:has-text('Docentes')")
        btn_tab_docentes.click()
        time.sleep(1)

        path_03 = output_dir / '03_organigrama_dock_docentes.png'
        page.screenshot(path=str(path_03))
        print(f"   Captura 3 guardada: {path_03}")

        # Captura 4: Cerrar dock y activar vista 'Todos los Nodos'
        print("6. Cerrando dock y seleccionando vista 'Todos'...")
        btn_close_dock = dock.locator("button[title='Cerrar panel lateral']")
        btn_close_dock.click()
        time.sleep(0.5)

        btn_todos = page.locator("button:has-text('Todos')")
        btn_todos.click()
        time.sleep(1.5)

        path_04 = output_dir / '04_organigrama_todos_nodos.png'
        page.screenshot(path=str(path_04))
        print(f"   Captura 4 guardada: {path_04}")

        # Captura 5: Regresar a Linea de Mando y probar asignacion rapida inline
        print("7. Regresando a Linea de Mando y probando asignacion inline...")
        btn_mando = page.locator("button:has-text('Linea de Mando')")
        btn_mando.click()
        time.sleep(1)

        # Abrir dock en Sin Supervisor
        btn_sin_supervisor.click()
        time.sleep(1)
        dock.wait_for(state='visible', timeout=5000)

        # Buscar el primer select de supervisor dentro de una tarjeta
        supervisor_select = dock.locator("article select").first
        if supervisor_select.count() > 0:
            options = supervisor_select.locator("option")
            count = options.count()
            print(f"   Opciones de supervisor disponibles en el select: {count}")
            if count > 1:
                val = options.nth(1).get_attribute('value')
                text = options.nth(1).inner_text()
                print(f"   Seleccionando supervisor: val={val}, text={text}")
                supervisor_select.select_option(value=val)
                time.sleep(1)

                btn_asignar = dock.locator("article button:has-text('Asignar')").first
                is_disabled = btn_asignar.is_disabled()
                print(f"   Boton asignar is_disabled={is_disabled}")
                btn_asignar.click()
                print("   Clic en boton 'Asignar' realizado.")
                time.sleep(2.5)
        
        path_05 = output_dir / '05_organigrama_asignacion_exitosa.png'
        page.screenshot(path=str(path_05))
        print(f"   Captura 5 guardada: {path_05}")
        page.screenshot(path=str(path_05))
        print(f"   Captura 5 guardada: {path_05}")

        # Copiar a artifacts
        for img in [path_01, path_02, path_03, path_04, path_05]:
            if img.exists() and artifact_dir.exists():
                shutil.copy(str(img), str(artifact_dir / img.name))
                print(f"   Copiado a artifacts: {img.name}")

        browser.close()
        print("\nVerificacion visual del Organigrama completada exitosamente!")

if __name__ == '__main__':
    verificar_organigrama()
