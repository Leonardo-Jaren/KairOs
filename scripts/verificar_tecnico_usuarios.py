import os
import sys
import time
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

def verificar_tecnico():
    output_dir = Path('docs/capturas_verificacion')
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_dir = Path(r'C:\Users\leona\.gemini\antigravity\brain\b6337a83-82d0-4659-944e-de724c8ee01e')

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()

        print("1. Iniciando sesion como tecnico...")
        page.goto('http://localhost:5173/auth/login')
        page.wait_for_load_state('networkidle')
        page.fill('#correo', 'tecnico@kairos.test')
        page.fill('#password', 'Admin123!')
        page.click('#btn-iniciar')

        page.wait_for_url('**/dashboard**', timeout=15000)
        page.wait_for_load_state('networkidle')
        print("   Sesion iniciada en Dashboard.")

        print("2. Navegando a /usuarios...")
        page.goto('http://localhost:5173/usuarios')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        # 3. Comprobar que NO existe el boton "+ Nuevo usuario"
        btn_nuevo = page.query_selector("button:has-text('Nuevo usuario')")
        if btn_nuevo:
            print("   ERROR: El boton '+ Nuevo usuario' es visible para el tecnico!")
        else:
            print("   CORRECTO: El boton '+ Nuevo usuario' NO aparece para el rol tecnico.")

        # Captura general de la pantalla de usuarios
        path_01 = output_dir / '01_tecnico_usuarios_lista.png'
        page.screenshot(path=str(path_01))
        print(f"   Captura 1 guardada: {path_01}")

        # 4. Comprobar el selector de Sede
        print("3. Seleccionando Sede La Esperanza...")
        sede_select = page.locator('#users-sede')
        sede_select.wait_for(state='visible', timeout=5000)
        sede_select.click()
        time.sleep(0.5)

        esperanza_option = page.locator("#users-sede-options button:has-text('La Esperanza')")
        esperanza_option.wait_for(state='visible', timeout=5000)
        esperanza_option.click()
        time.sleep(1.5)

        filter_section = page.locator('section.rounded-2xl.border.border-slate-200.bg-white')
        path_02 = output_dir / '02_tecnico_select_sede_zoom.png'
        filter_section.screenshot(path=str(path_02))
        print(f"   Captura 2 guardada (Zoom filtros): {path_02}")

        # 5. Comprobar usuarios listados
        filas = page.locator('table tbody tr')
        print(f"   Total filas para La Esperanza: {filas.count()}")

        path_03 = output_dir / '03_tecnico_usuarios_esperanza_filtrados.png'
        page.screenshot(path=str(path_03))
        print(f"   Captura 3 guardada: {path_03}")

        # 6. Comprobar que NO existen botones de editar ni desactivar en la tabla
        pencils = page.locator("table tbody button[title='Editar usuario']").count()
        user_x = page.locator("table tbody button[title='Desactivar usuario']").count()
        key_round = page.locator("table tbody button[title='Configurar matriz de permisos']").count()
        eye_buttons = page.locator("table tbody button[title='Ver ficha de usuario']").count()

        print(f"   Botones 'Ver ficha': {eye_buttons}")
        print(f"   Botones 'Editar usuario': {pencils} (debe ser 0)")
        print(f"   Botones 'Desactivar usuario': {user_x} (debe ser 0)")
        print(f"   Botones 'Configurar permisos': {key_round} (debe ser 0)")

        first_row = page.locator('table tbody tr').first
        path_04 = output_dir / '04_tecnico_acciones_tabla_zoom.png'
        first_row.screenshot(path=str(path_04))
        print(f"   Captura 4 guardada (Zoom fila): {path_04}")

        browser.close()

    for fname in ['01_tecnico_usuarios_lista.png', '02_tecnico_select_sede_zoom.png', '03_tecnico_usuarios_esperanza_filtrados.png', '04_tecnico_acciones_tabla_zoom.png']:
        src = output_dir / fname
        dst = artifact_dir / fname
        if src.exists():
            shutil.copy2(src, dst)
            print(f"   Copiado a artefacto: {dst}")

    print("VERIFICACION COMPLETADA CON EXITO")

if __name__ == '__main__':
    verificar_tecnico()
