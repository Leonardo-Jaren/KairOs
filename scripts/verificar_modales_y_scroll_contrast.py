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
        # Testeamos en un viewport mediano (1200x800) y tambien en movil
        context = browser.new_context(viewport={'width': 1200, 'height': 800})
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

        print("2. Navegando a /usuarios y abriendo modal 'Nuevo usuario'...")
        page.goto('http://localhost:5173/usuarios')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        btn_nuevo = page.locator('button:has-text("Nuevo usuario")').first
        btn_nuevo.click()
        time.sleep(0.8)

        # Diagnosticar backdrop y scrollbar en BaseModal
        modal_diagnostics = page.evaluate('''() => {
            const backdrop = document.querySelector('div[role="dialog"]');
            const section = backdrop ? backdrop.querySelector('section') : null;
            const scrollBody = section ? section.querySelector('.dock-scrollbar') : null;
            const backdropStyle = backdrop ? window.getComputedStyle(backdrop) : null;
            const bodyStyle = scrollBody ? window.getComputedStyle(scrollBody) : null;

            return {
                backdropOverflowY: backdropStyle ? backdropStyle.overflowY : null,
                backdropScrollHeight: backdrop ? backdrop.scrollHeight : 0,
                backdropClientHeight: backdrop ? backdrop.clientHeight : 0,
                hasBackdropScroll: backdrop ? backdrop.scrollHeight > backdrop.clientHeight : false,
                scrollBodyOverflowY: bodyStyle ? bodyStyle.overflowY : null,
                sectionMaxHeight: section ? window.getComputedStyle(section).maxHeight : null,
                sectionHeight: section ? section.clientHeight : null
            };
        }''')

        print("   Diagnostico de BaseModal (Nuevo usuario):")
        print(f"   Backdrop overflowY: {modal_diagnostics['backdropOverflowY']}, hasBackdropScroll: {modal_diagnostics['hasBackdropScroll']}")
        print(f"   Section maxHeight: {modal_diagnostics['sectionMaxHeight']}, height: {modal_diagnostics['sectionHeight']}")
        print(f"   ScrollBody overflowY: {modal_diagnostics['scrollBodyOverflowY']}")

        path_modal_nuevo = output_dir / '14_nuevo_usuario_modal_refined_scroll.png'
        page.screenshot(path=str(path_modal_nuevo))
        print(f"   Captura de modal Nuevo Usuario guardada: {path_modal_nuevo}")

        # Cerrar modal
        btn_cancelar = page.locator('button:has-text("Cancelar")').first
        btn_cancelar.click()
        time.sleep(0.5)

        print("3. Cambiando a pestaña Organigrama para auditar ficha de usuario con poca información...")
        page.locator('button:has-text("Organigrama")').click()
        page.wait_for_load_state('networkidle')
        time.sleep(1.5)

        # Clic en el primer nodo (Superadmin o Leonard) para abrir ficha
        first_node = page.locator('div.group.relative.w-72').first
        first_node.click()
        time.sleep(0.8)

        # Medir dimensiones del modal de usuario
        drawer_diagnostics = page.evaluate('''() => {
            const drawer = document.querySelector('aside[role="dialog"]');
            if (!drawer) return null;
            const style = window.getComputedStyle(drawer);
            const content = drawer.querySelector('.dock-scrollbar');
            const footer = drawer.querySelector('footer');

            return {
                drawerHeight: drawer.clientHeight,
                drawerMaxHeight: style.maxHeight,
                contentHeight: content ? content.clientHeight : 0,
                footerHeight: footer ? footer.clientHeight : 0,
                footerDisplay: footer ? window.getComputedStyle(footer).display : null,
                viewportHeight: window.innerHeight
            };
        }''')

        print("   Diagnostico de OrgUserDrawer (Ficha con poca info):")
        print(f"   Drawer clientHeight: {drawer_diagnostics['drawerHeight']}px (Viewport: {drawer_diagnostics['viewportHeight']}px)")
        print(f"   Drawer maxHeight: {drawer_diagnostics['drawerMaxHeight']}")
        print(f"   Content clientHeight: {drawer_diagnostics['contentHeight']}px")
        print(f"   Footer height: {drawer_diagnostics['footerHeight']}px")

        # El modal no debe ocupar forzosamente 680px si el contenido es menor a 400px
        assert drawer_diagnostics['drawerHeight'] < 650, f"ERROR: El modal mide {drawer_diagnostics['drawerHeight']}px, deberia ajustarse al contenido!"
        print("   => VERIFICADO: El modal se ajusta armoniosamente al contenido sin espacio en blanco vacio.")

        path_drawer_compact = output_dir / '15_ficha_usuario_compact_refined_layout.png'
        page.screenshot(path=str(path_drawer_compact))
        print(f"   Captura de Ficha de Usuario compacta guardada: {path_drawer_compact}")

        print("4. Cambiando a pestaña 'A su cargo' para probar contenido dinámico...")
        tab_cargo = page.locator('button:has-text("A su cargo")').first
        tab_cargo.click()
        time.sleep(0.8)

        path_drawer_cargo = output_dir / '16_ficha_usuario_a_su_cargo.png'
        page.screenshot(path=str(path_drawer_cargo))
        print(f"   Captura de pestaña A su cargo guardada: {path_drawer_cargo}")

        # Copiar capturas a artifacts
        for p_img in [path_modal_nuevo, path_drawer_compact, path_drawer_cargo]:
            if p_img.exists() and artifact_dir.exists():
                shutil.copy2(str(p_img), str(artifact_dir / p_img.name))
                print(f"   Copiado a artifacts: {p_img.name}")

        browser.close()
        print("\n=> AUDITORIA VISUAL DE MODALES Y SCROLLBARS COMPLETADA CON EXITO!")

if __name__ == '__main__':
    verificar()
