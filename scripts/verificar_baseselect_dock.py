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

        print("1. Iniciando sesión como SuperAdmin...")
        page.goto('http://localhost:5173/auth/login')
        page.wait_for_load_state('networkidle')
        page.fill('#correo', 'admin@kairos.test')
        page.fill('#password', 'Admin123!')
        page.click('#btn-iniciar')
        page.wait_for_url('**/dashboard**')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        print("2. Navegando a /usuarios y cambiando a pestaña Organigrama...")
        page.goto('http://localhost:5173/usuarios')
        page.wait_for_load_state('networkidle')
        page.locator('button:has-text("Organigrama")').click()
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        print("3. Abriendo Action Dock (Sin Supervisor)...")
        page.locator('button:has-text("Sin Supervisor")').click()
        time.sleep(1)
        dock = page.locator('aside[aria-label="Panel de accion rapida del organigrama"]')
        dock.wait_for(state='visible')

        print("4. Abriendo el BaseSelect del primer usuario sin supervisor...")
        combobox = dock.locator('button[role="combobox"]').first
        combobox.wait_for(state='visible')
        combobox.click()
        time.sleep(0.8)

        dropdown = page.locator('div[role="listbox"]')
        dropdown.wait_for(state='visible')

        path_img = output_dir / '08_dock_baseselect_custom.png'
        page.screenshot(path=str(path_img))
        print(f"   Captura de BaseSelect personalizado guardada: {path_img}")

        if artifact_dir.exists():
            shutil.copy2(path_img, artifact_dir / '08_dock_baseselect_custom.png')
            print("   Copiado a artifacts: 08_dock_baseselect_custom.png")

        browser.close()
        print("Verificación de BaseSelect completada con éxito!")

if __name__ == '__main__':
    verificar()
