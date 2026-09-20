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
        context = browser.new_context(viewport={'width': 1500, 'height': 950}, accept_downloads=True)
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
        time.sleep(1.5)

        print("3. Probando botón 'Exportar PNG' y capturando evento de descarga...")
        # Localizar el boton Exportar PNG (usamos el de la barra superior o el del lienzo)
        export_btn = page.locator('button:has-text("Exportar PNG")').first
        export_btn.wait_for(state='visible')

        with page.expect_download(timeout=15000) as download_info:
            export_btn.click()
            print("   Clic en 'Exportar PNG' efectuado...")

        download = download_info.value
        downloaded_filename = download.suggested_filename
        print(f"   Descarga interceptada con éxito: {downloaded_filename}")

        save_path = output_dir / '09_organigrama_exportado.png'
        download.save_as(str(save_path))
        print(f"   Archivo guardado en: {save_path} (Tamaño: {save_path.stat().st_size} bytes)")

        # Esperar un momento para ver el Toast de éxito en la UI
        time.sleep(0.5)
        path_ui_screenshot = output_dir / '10_organigrama_export_toast_ui.png'
        page.screenshot(path=str(path_ui_screenshot))
        print(f"   Captura de UI con toast guardada: {path_ui_screenshot}")

        if artifact_dir.exists():
            shutil.copy2(save_path, artifact_dir / '09_organigrama_exportado.png')
            shutil.copy2(path_ui_screenshot, artifact_dir / '10_organigrama_export_toast_ui.png')
            print("   Copiado a artifacts con éxito.")

        browser.close()
        print("Verificación de Exportación a PNG completada con éxito!")

if __name__ == '__main__':
    verificar()
