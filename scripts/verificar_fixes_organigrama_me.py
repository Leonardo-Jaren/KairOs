import os
import sys
import time
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

def verificar():
    output_dir = Path('docs/capturas_verificacion')
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_dir = Path(r'C:\Users\leona\.gemini\antigravity\brain\b6337a83-82d0-4659-944e-de724c8ee01e')

    auth_me_calls = []

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(viewport={'width': 1500, 'height': 950})
        page = context.new_page()

        def on_response(resp):
            if '/api/v1/auth/me/' in resp.url:
                auth_me_calls.append((time.time(), resp.status))
                print(f"   [NETWORK] /api/v1/auth/me/ llamado: status={resp.status}")

        page.on('response', on_response)

        print("1. Iniciando sesión como SuperAdmin...")
        page.goto('http://localhost:5173/auth/login')
        page.wait_for_load_state('networkidle')
        page.fill('#correo', 'admin@kairos.test')
        page.fill('#password', 'Admin123!')
        page.click('#btn-iniciar')
        page.wait_for_url('**/dashboard**')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        print("2. Evaluando throttling de /api/v1/auth/me/ ante cambios de foco y visibilidad...")
        initial_calls_count = len(auth_me_calls)
        print(f"   Llamadas iniciales a /auth/me/: {initial_calls_count}")

        # Simular cambio de pestaña / foco 5 veces seguidas
        for i in range(5):
            page.evaluate("() => { window.dispatchEvent(new Event('blur')); }")
            time.sleep(0.2)
            page.evaluate("() => { window.dispatchEvent(new Event('focus')); }")
            time.sleep(0.2)
            page.evaluate("() => { document.dispatchEvent(new Event('visibilitychange')); }")
            time.sleep(0.2)

        calls_after_focus = len(auth_me_calls)
        print(f"   Llamadas tras 5 cambios de foco/visibilidad seguidos: {calls_after_focus}")
        if calls_after_focus == initial_calls_count:
            print("   -> ÉXITO: El throttling de /auth/me/ impidió ráfagas y consultas repetitivas innecesarias.")
        else:
            print(f"   -> AVISO: Se realizaron {calls_after_focus - initial_calls_count} llamadas adicionales.")

        print("3. Navegando a /usuarios y cambiando a Organigrama...")
        page.goto('http://localhost:5173/usuarios')
        page.wait_for_load_state('networkidle')
        page.locator('button:has-text("Organigrama")').click()
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        print("4. Abriendo Action Dock y verificando scroll vertical...")
        page.locator('button:has-text("Sin Supervisor")').click()
        time.sleep(1)
        dock = page.locator('aside[aria-label="Panel de accion rapida del organigrama"]')
        dock.wait_for(state='visible')

        scroll_container = dock.locator('div.dock-scrollbar')
        scroll_top_initial = scroll_container.evaluate('el => el.scrollTop')
        print(f"   Scroll top inicial: {scroll_top_initial}")

        # Realizar scroll vertical hacia abajo en el contenedor
        scroll_container.evaluate('el => { el.scrollTop = el.scrollHeight; }')
        time.sleep(1)
        scroll_top_scrolled = scroll_container.evaluate('el => el.scrollTop')
        print(f"   Scroll top tras desplazarse al final: {scroll_top_scrolled}")

        path_01 = output_dir / '06_dock_scroll_vertical.png'
        page.screenshot(path=str(path_01))
        print(f"   Captura de scroll guardada: {path_01}")

        print("5. Verificando vista 'Todos' con disposición en columnas y cuadrícula...")
        # Cerrar dock
        dock.locator('button[title="Cerrar panel lateral"]').click()
        time.sleep(0.5)

        # Clic en badge Todos
        page.locator('button:has-text("Todos")').click()
        time.sleep(1)

        # Alejar zoom para apreciar el panorama general en cuadrícula
        btn_zoom_out = page.locator('button[title*="Alejar"]')
        for _ in range(3):
            btn_zoom_out.click()
            time.sleep(0.3)
        # Arrastrar el lienzo hacia arriba para enfocar la cuadrícula de colaboradores independientes
        canvas = page.locator("div.relative.w-full.h-\\[740px\\]")
        box = canvas.bounding_box()
        page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
        page.mouse.down()
        page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2 - 350)
        page.mouse.up()
        time.sleep(1)

        path_02 = output_dir / '07_todos_columnas_grid.png'
        page.screenshot(path=str(path_02))
        print(f"   Captura de vista Todos en columnas guardada: {path_02}")

        # Copiar capturas a artifacts
        for p_img in [path_01, path_02]:
            if p_img.exists() and artifact_dir.exists():
                shutil.copy(str(p_img), str(artifact_dir / p_img.name))
                print(f"   Copiado a artifacts: {p_img.name}")

        browser.close()
        print("\nVerificación de fixes completada!")

if __name__ == '__main__':
    verificar()
