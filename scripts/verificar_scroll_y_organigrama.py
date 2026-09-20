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

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(viewport={'width': 1500, 'height': 950})
        page = context.new_page()

        print("1. Iniciando sesion como SuperAdmin...")
        page.goto('http://localhost:5173/auth/login')
        page.wait_for_load_state('networkidle')
        page.fill('#correo', 'admin@kairos.test')
        page.fill('#password', 'Admin123!')
        page.click('#btn-iniciar')
        page.wait_for_url('**/dashboard**')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        print("2. Navegando a /usuarios (Vista Lista) para auditar barras de desplazamiento...")
        page.goto('http://localhost:5173/usuarios')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        # Analisis de overflow y scroll en #app y documentElement
        scroll_diagnostics = page.evaluate('''() => {
            const app = document.querySelector('#app');
            const html = document.documentElement;
            const body = document.body;

            const appStyle = window.getComputedStyle(app);
            const htmlStyle = window.getComputedStyle(html);
            const bodyStyle = window.getComputedStyle(body);

            return {
                app: {
                    overflowX: appStyle.overflowX,
                    overflowY: appStyle.overflowY,
                    clientHeight: app.clientHeight,
                    scrollHeight: app.scrollHeight,
                    hasScrollbar: app.scrollHeight > app.clientHeight && (appStyle.overflowY === 'auto' || appStyle.overflowY === 'scroll')
                },
                html: {
                    overflowX: htmlStyle.overflowX,
                    overflowY: htmlStyle.overflowY,
                    clientHeight: html.clientHeight,
                    scrollHeight: html.scrollHeight
                },
                windowInnerHeight: window.innerHeight
            };
        }''')

        print("   Diagnostico de Scroll en Vista Lista:")
        print(f"   #app overflowY: {scroll_diagnostics['app']['overflowY']}, hasScrollbar: {scroll_diagnostics['app']['hasScrollbar']}")
        print(f"   html overflowX: {scroll_diagnostics['html']['overflowX']}, overflowY: {scroll_diagnostics['html']['overflowY']}")
        print(f"   html scrollHeight: {scroll_diagnostics['html']['scrollHeight']}, clientHeight: {scroll_diagnostics['html']['clientHeight']}")

        assert not scroll_diagnostics['app']['hasScrollbar'], "ERROR: #app tiene barra de desplazamiento anidada duplicada!"
        print("   => VERIFICADO: No existe barra de scroll duplicada en #app. La navegacion vertical es unificada y limpia.")

        path_lista = output_dir / '11_usuarios_lista_single_scroll.png'
        page.screenshot(path=str(path_lista))
        print(f"   Captura de Lista guardada: {path_lista}")

        print("3. Cambiando a pestaña 'Organigrama'...")
        page.locator('button:has-text("Organigrama")').click()
        page.wait_for_load_state('networkidle')
        time.sleep(1.5)

        # Verificar contenedor del organigrama
        org_diagnostics = page.evaluate('''() => {
            const orgContainer = document.querySelector('[data-testid="org-chart"]');
            const canvas = document.querySelector('[data-testid="org-chart-canvas"]');
            const style = window.getComputedStyle(orgContainer);

            return {
                containerOverflow: style.overflow,
                containerOverflowX: style.overflowX,
                containerOverflowY: style.overflowY,
                canvasTransform: canvas ? canvas.style.transform : null,
                isCursorGrab: orgContainer.classList.contains('cursor-grab') || orgContainer.classList.contains('cursor-grabbing')
            };
        }''')

        print("   Diagnostico de OrgChartTree:")
        print(f"   Contenedor overflow: {org_diagnostics['containerOverflowX']} / {org_diagnostics['containerOverflowY']}")
        print(f"   Canvas transform inicial: {org_diagnostics['canvasTransform']}")
        print(f"   Clase cursor grab activa: {org_diagnostics['isCursorGrab']}")

        assert org_diagnostics['containerOverflowY'] == 'hidden', f"ERROR: Contenedor tiene overflow-y '{org_diagnostics['containerOverflowY']}', se esperaba 'hidden'!"
        assert org_diagnostics['isCursorGrab'], "ERROR: No tiene cursor-grab en el lienzo!"

        print("4. Probando interaccion de arrastre (pan) en el lienzo...")
        canvas_box = page.locator('[data-testid="org-chart"]').bounding_box()
        # Arrastramos desde una zona despejada
        start_x = canvas_box['x'] + 100
        start_y = canvas_box['y'] + 200

        page.mouse.move(start_x, start_y)
        page.mouse.down()
        page.mouse.move(start_x + 150, start_y + 90, steps=10)
        page.mouse.up()
        time.sleep(0.5)

        # Confirmar que tras arrastrar el drawer NO se haya abierto indebidamente
        drawer_open = page.evaluate('() => !!document.querySelector("aside[role=\\"dialog\\"]")')
        print(f"   Drawer abierto tras arrastrar: {drawer_open}")
        assert not drawer_open, "ERROR: Arrastrar el lienzo no debio abrir la ficha del usuario!"

        transform_after_drag = page.evaluate('''() => {
            const canvas = document.querySelector('[data-testid="org-chart-canvas"]');
            return canvas ? canvas.style.transform : null;
        }''')
        print(f"   Transform tras arrastrar (+150, +90): {transform_after_drag}")
        assert 'translate' in transform_after_drag, "ERROR: El canvas no se desplazo con el arrastre de mouse!"

        print("5. Probando controles de zoom...")
        zoom_in_btn = page.locator('button[title*="Acercar"]').first
        zoom_in_btn.wait_for(state='visible')
        zoom_in_btn.click()
        time.sleep(0.3)
        zoom_in_btn.click()
        time.sleep(0.5)

        transform_after_zoom = page.evaluate('''() => {
            const canvas = document.querySelector('[data-testid="org-chart-canvas"]');
            return canvas ? canvas.style.transform : null;
        }''')
        print(f"   Transform tras Zoom In: {transform_after_zoom}")

        path_org_panned = output_dir / '12_organigrama_canvas_panned_zoomed.png'
        page.screenshot(path=str(path_org_panned))
        print(f"   Captura de Organigrama interactivo guardada: {path_org_panned}")

        print("6. Probando vista 'Todos' en columnas horizontales...")
        page.locator('button:has-text("Todos")').click()
        time.sleep(1)

        # Restablecer vista para centrar
        page.locator('button[title*="Restablecer vista"]').first.click()
        time.sleep(0.5)

        path_org_todos = output_dir / '13_organigrama_todos_responsive_grid.png'
        page.screenshot(path=str(path_org_todos))
        print(f"   Captura de vista Todos guardada: {path_org_todos}")

        # Copiar capturas a artifacts
        for p_img in [path_lista, path_org_panned, path_org_todos]:
            if p_img.exists() and artifact_dir.exists():
                shutil.copy2(str(p_img), str(artifact_dir / p_img.name))
                print(f"   Copiado a artifacts: {p_img.name}")

        browser.close()
        print("\n=> TODAS LAS VERIFICACIONES VISUALES Y FUNCIONALES COMPLETADAS EXITOSAMENTE!")

if __name__ == '__main__':
    verificar()
