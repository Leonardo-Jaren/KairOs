import os
import shutil
import sys
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

OUTPUT_DIRS = [
    Path('d:/Descargas google/KairOs/docs/manual_usuario/capturas'),
    Path('d:/Descargas google/KairOs/manual_usuario/capturas'),
]
for d in OUTPUT_DIRS:
    d.mkdir(parents=True, exist_ok=True)

def resolve_box(page, selector_or_list, padding=4):
    """
    Obtiene dinámicamente las coordenadas del DOM mediante Playwright.
    Soporta selector individual, lista de selectores (para agrupar controles contiguos),
    o diccionario con selector y parámetros personalizados.
    """
    if isinstance(selector_or_list, (list, tuple)):
        rects = []
        for sel in selector_or_list:
            actual_sel = sel['selector'] if isinstance(sel, dict) else sel
            loc = page.locator(actual_sel).first
            loc.wait_for(state='visible', timeout=8000)
            b = loc.bounding_box()
            if b:
                rects.append(b)
        if not rects:
            raise ValueError(f"No se encontró bounding_box para {selector_or_list}")
        min_x = min(r['x'] for r in rects)
        min_y = min(r['y'] for r in rects)
        max_x = max(r['x'] + r['width'] for r in rects)
        max_y = max(r['y'] + r['height'] for r in rects)
        return {
            'x1': int(min_x - padding),
            'y1': int(min_y - padding),
            'x2': int(max_x + padding),
            'y2': int(max_y + padding),
        }
    else:
        actual_sel = selector_or_list['selector'] if isinstance(selector_or_list, dict) else selector_or_list
        loc = page.locator(actual_sel).first
        loc.wait_for(state='visible', timeout=8000)
        b = loc.bounding_box()
        if not b:
            raise ValueError(f"No se encontró bounding_box para {actual_sel}")
        return {
            'x1': int(b['x'] - padding),
            'y1': int(b['y'] - padding),
            'x2': int(b['x'] + b['width'] + padding),
            'y2': int(b['y'] + b['height'] + padding),
        }

def annotate_image(image_path, annotations):
    """
    Dibuja recuadros rojos (#EF4444) de 3px y badges circulares numerados
    en la esquina superior izquierda de cada zona de interés obtenida dinámicamente.
    Alinea el badge milimétricamente sin tapar texto interior ni etiquetas.
    """
    img = Image.open(image_path).convert('RGB')
    draw = ImageDraw.Draw(img)
    w, h = img.size

    red_color = (239, 68, 68)      # #EF4444 rojo institucional KairOs
    white_color = (255, 255, 255)

    try:
        font_badge = ImageFont.truetype("arialbd.ttf", 13)
    except Exception:
        font_badge = ImageFont.load_default()

    badge_radius = 11

    for ann in annotations:
        box = ann['box']
        step = ann.get('step', 1)
        x1 = box['x1']
        y1 = box['y1']
        x2 = box['x2']
        y2 = box['y2']

        # Ajustar a las dimensiones de la imagen con margen de seguridad
        x1 = max(3, min(x1, w - 8))
        y1 = max(3, min(y1, h - 8))
        x2 = max(x1 + 10, min(x2, w - 3))
        y2 = max(y1 + 10, min(y2, h - 3))

        # Dibujar marco rojo exterior e interior de 3px
        for i in range(3):
            draw.rectangle([x1 - i, y1 - i, x2 + i, y2 + i], outline=red_color)

        # Ubicación del badge circular
        if 'badge_xy' in ann:
            bx, by = ann['badge_xy']
        else:
            # Si el elemento está pegado al borde superior o izquierdo de la pantalla,
            # desplazar hacia adentro para que el badge no se corte
            if x1 <= 4 and y1 <= 4:
                bx = 24
                by = 24
            elif y1 <= 4:
                bx = max(badge_radius + 2, min(x1 + 14, w - badge_radius - 2))
                by = 22
            else:
                dx, dy = ann.get('badge_offset', (0, -3))
                bx = max(badge_radius + 2, min(x1 + dx, w - badge_radius - 2))
                by = max(badge_radius + 2, min(y1 + dy, h - badge_radius - 2))

        # Dibujar badge circular con borde blanco
        draw.ellipse(
            [bx - badge_radius, by - badge_radius, bx + badge_radius, by + badge_radius],
            fill=red_color,
            outline=white_color,
            width=2
        )

        # Texto del badge
        draw.text((bx, by), str(step), fill=white_color, font=font_badge, anchor="mm")

    img.save(image_path)
    
    # Copiar a todas las rutas de salida
    for out_dir in OUTPUT_DIRS:
        dest = out_dir / Path(image_path).name
        if dest.resolve() != Path(image_path).resolve():
            shutil.copy2(image_path, dest)
            
    print(f"  [OK] Anotada y sincronizada: {Path(image_path).name}")

def capture_and_annotate(page, filename, step_selectors, wait_ms=1000, padding=4):
    """
    Captura la pantalla actual, obtiene los bounding boxes de los selectores,
    anota la imagen con recuadros y badges perfectamente alineados.
    """
    time.sleep(wait_ms / 1000.0)
    
    annotations = []
    for step, item in enumerate(step_selectors, start=1):
        item_padding = padding
        badge_offset = (0, -3)
        badge_xy = None
        
        if isinstance(item, dict) and 'selector' in item:
            sel = item['selector']
            item_padding = item.get('padding', padding)
            badge_offset = item.get('badge_offset', (0, -3))
            badge_xy = item.get('badge_xy')
        else:
            sel = item

        box = resolve_box(page, sel, padding=item_padding)
        ann = {'box': box, 'step': step, 'badge_offset': badge_offset}
        if badge_xy:
            ann['badge_xy'] = badge_xy
        annotations.append(ann)
        
    primary_path = OUTPUT_DIRS[0] / filename
    page.screenshot(path=str(primary_path))
    annotate_image(primary_path, annotations)

def run_capture_pipeline():
    print("================================================================")
    print("EJECUTANDO PIPELINE DINÁMICO DE CAPTURAS PARA EL MANUAL DE USUARIO")
    print("================================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(
            viewport={'width': 1366, 'height': 768},
            device_scale_factor=1.0,
        )
        page = context.new_page()

        # -------------------------------------------------------------
        # 1. LOGIN
        # -------------------------------------------------------------
        print("\n[1/17] Pantalla de Login...")
        page.goto('http://localhost:5173/auth/login')
        page.wait_for_load_state('networkidle')
        capture_and_annotate(page, '01_login_general.png', [
            'form > div:has(#correo)',
            'form > div:has(#password)',
            {'selector': 'label:has(input[type="checkbox"])', 'badge_offset': (-6, -6)},
            '#btn-iniciar',
            'div:has-text("o continuar con") + div',
            {'selector': 'a[href*="password-reset"]', 'badge_offset': (-6, -6)},
        ], wait_ms=1000)

        # -------------------------------------------------------------
        # 2. RECUPERAR CONTRASEÑA
        # -------------------------------------------------------------
        print("\n[2/17] Pantalla de Recuperación de Contraseña...")
        page.goto('http://localhost:5173/auth/password-reset')
        page.wait_for_load_state('networkidle')
        capture_and_annotate(page, '02_recuperar_password.png', [
            'form > div:has(#reset-correo)',
            '#btn-request-reset',
            {'selector': 'a[href*="/auth/login"]', 'badge_offset': (-6, -6)},
        ], wait_ms=1000)

        # -------------------------------------------------------------
        # INICIAR SESIÓN COMO ADMIN
        # -------------------------------------------------------------
        print("\nIniciando sesión como admin@kairos.test...")
        page.goto('http://localhost:5173/auth/login')
        page.wait_for_load_state('networkidle')
        page.fill('#correo', 'admin@kairos.test')
        page.fill('#password', 'Admin123!')
        page.click('#btn-iniciar')
        page.wait_for_url('**/dashboard**', timeout=10000)
        page.wait_for_load_state('networkidle')
        time.sleep(1.5)

        # -------------------------------------------------------------
        # 3. DASHBOARD
        # -------------------------------------------------------------
        print("\n[3/17] Panel de Control (Dashboard)...")
        capture_and_annotate(page, '03_dashboard_principal.png', [
            {'selector': 'section[aria-labelledby="dashboard-metrics-title"]', 'badge_offset': (14, -10)},
            {'selector': 'article:has-text("Salud del Inventario de Hardware")', 'badge_offset': (14, -10)},
            {'selector': 'article:has-text("Mesa de Soporte")', 'badge_offset': (14, -10)},
            {'selector': 'aside', 'badge_xy': (24, 135)},
        ], wait_ms=1500)

        # -------------------------------------------------------------
        # 4. USUARIOS - LISTADO
        # -------------------------------------------------------------
        print("\n[4/17] Catálogo de Usuarios...")
        page.goto('http://localhost:5173/usuarios')
        page.wait_for_load_state('networkidle')
        capture_and_annotate(page, '04_usuarios_catalogo.png', [
            'div:has(> #users-search)',
            ['div:has(> #users-role)', 'button:has-text("Limpiar")'],
            'header button:has-text("Nuevo usuario")',
            'table',
        ], wait_ms=1500)

        # -------------------------------------------------------------
        # 5. USUARIOS - MODAL REGISTRO
        # -------------------------------------------------------------
        print("\n[5/17] Modal de Registro de Usuario...")
        page.click('header button:has-text("Nuevo usuario")')
        page.wait_for_selector('form#user-form', state='visible', timeout=5000)
        capture_and_annotate(page, '05_usuarios_modal_registro.png', [
            'form#user-form > div:nth-child(1)',
            'form#user-form > div:nth-child(2)',
            'form#user-form > div:nth-child(3)',
            'form#user-form > div:nth-child(4)',
            'form#user-form > div:nth-child(5)',
            'form#user-form > div:nth-child(6)',
            'form#user-form > div:nth-child(7)',
            'button[type="submit"][form="user-form"], button:has-text("Crear usuario")',
        ], wait_ms=800, padding=3)
        page.keyboard.press('Escape')
        time.sleep(0.5)

        # -------------------------------------------------------------
        # 6. ESPACIOS - LISTADO
        # -------------------------------------------------------------
        print("\n[6/17] Módulo de Espacios...")
        page.goto('http://localhost:5173/espacios')
        page.wait_for_load_state('networkidle')
        capture_and_annotate(page, '06_espacios_listado.png', [
            'div:has(> #spaces-search)',
            ['div:has(> #spaces-type)', 'button:has-text("Limpiar")'],
            'header button:has-text("Nuevo espacio")',
            'table',
        ], wait_ms=1500)

        # -------------------------------------------------------------
        # 7. CAMPUS TECNOLÓGICO / MAPA (/espacios/mapa)
        # -------------------------------------------------------------
        print("\n[7/17] Campus Tecnológico (/espacios/mapa)...")
        page.goto('http://localhost:5173/espacios/mapa')
        page.wait_for_load_state('networkidle')
        capture_and_annotate(page, '07_espacios_mapa_campus.png', [
            ['section:has(#campus-city) > div > div:first-child', 'div:has(> #campus-local)'],
            'section:has(#campus-city) button:has-text("Nuevo local")',
            'header button:has-text("Agregar pabellón")',
            'section:has-text("Pabellones"):has-text("Pisos activos")',
            'section:has-text("Elige un pabellón")',
        ], wait_ms=1500)

        # -------------------------------------------------------------
        # 8. PLANO INTERACTIVO DE ESPACIO (/espacios/2)
        # -------------------------------------------------------------
        print("\n[8/17] Plano Interactivo (/espacios/2)...")
        page.goto('http://localhost:5173/espacios/2')
        page.wait_for_load_state('networkidle')
        time.sleep(1.5)
        # Click en la estación para abrir la ficha lateral
        try:
            station = page.locator('button:has(span.font-mono)').first
            if station.count() > 0:
                station.click()
                time.sleep(0.8)
        except Exception as e:
            print("  [Aviso] No se pudo hacer click en estación:", e)

        # Cuando la ficha lateral (drawer) está abierta, acotar los elementos del fondo:
        drawer_box = resolve_box(page, 'aside.ml-auto, aside:has-text("Ficha del equipo")', padding=4)
        clip_right = drawer_box['x1'] - 8

        b1 = resolve_box(page, 'header.grid', padding=4)
        b1['x2'] = min(b1['x2'], clip_right)

        b2 = resolve_box(page, 'section.overflow-hidden.rounded-3xl', padding=4)
        b2['x2'] = min(b2['x2'], clip_right)
        b2['y2'] = min(b2['y2'], 760)

        b3 = {
            'x1': drawer_box['x1'],
            'y1': 4,
            'x2': 1362,
            'y2': 764
        }
        b4 = resolve_box(page, 'aside button:has-text("Registrar falla")', padding=4)

        primary_path = OUTPUT_DIRS[0] / '08_espacios_plano_interactivo.png'
        page.screenshot(path=str(primary_path))
        annotate_image(primary_path, [
            {'box': b1, 'step': 1},
            {'box': b2, 'step': 2},
            {'box': b3, 'step': 3, 'badge_xy': (b3['x1'] - 14, 28)},
            {'box': b4, 'step': 4},
        ])

        # -------------------------------------------------------------
        # 9. ASIGNACIONES POR ESPACIO (/espacios/usuarios)
        # -------------------------------------------------------------
        print("\n[9/17] Asignaciones de Usuarios (/espacios/usuarios)...")
        page.goto('http://localhost:5173/espacios/usuarios')
        page.wait_for_load_state('networkidle')
        capture_and_annotate(page, '09_espacios_usuarios_asignados.png', [
            'div:has(> #assignments-search)',
            'header button:has-text("Nueva asignación")',
            'table',
        ], wait_ms=1500)

        # -------------------------------------------------------------
        # 10. EQUIPOS - LISTADO
        # -------------------------------------------------------------
        print("\n[10/17] Inventario de Equipos (/equipos)...")
        page.goto('http://localhost:5173/equipos')
        page.wait_for_load_state('networkidle')
        capture_and_annotate(page, '10_equipos_inventario.png', [
            'div:has(> #equipos-search)',
            ['div:has(> #equipos-tipo)', 'button:has-text("Limpiar")'],
            'header button:has-text("Agregar")',
            'table',
        ], wait_ms=1500)

        # -------------------------------------------------------------
        # 11. EQUIPOS - MODAL REGISTRO
        # -------------------------------------------------------------
        print("\n[11/17] Modal de Registro de Equipo...")
        page.click('header button:has-text("Agregar")')
        page.wait_for_selector('form#equipo-form', state='visible', timeout=5000)
        capture_and_annotate(page, '11_equipos_modal_registro.png', [
            'form#equipo-form > div:nth-child(1)',
            'form#equipo-form > div:nth-child(2)',
            'form#equipo-form > div:nth-child(3)',
            'form#equipo-form > div:nth-child(4)',
            ['form#equipo-form > div:nth-child(5)', 'form#equipo-form > div:nth-child(6)'],
            'button[type="submit"][form="equipo-form"], button:has-text("Crear equipo")',
        ], wait_ms=800, padding=3)
        page.keyboard.press('Escape')
        time.sleep(0.5)

        # -------------------------------------------------------------
        # 12. COMPONENTES DE HARDWARE (/componentes)
        # -------------------------------------------------------------
        print("\n[12/17] Componentes de Hardware (/componentes)...")
        page.goto('http://localhost:5173/componentes')
        page.wait_for_load_state('networkidle')
        capture_and_annotate(page, '12_componentes_hardware.png', [
            'section.flex.flex-wrap.gap-2',
            'header button:has-text("Agregar")',
            'table',
        ], wait_ms=1500)

        # -------------------------------------------------------------
        # 13. SOFTWARE - CATÁLOGO (/software)
        # -------------------------------------------------------------
        print("\n[13/17] Catálogo de Software (/software)...")
        page.goto('http://localhost:5173/software')
        page.wait_for_load_state('networkidle')
        capture_and_annotate(page, '13_software_catalogo.png', [
            'div:has(> #software-search)',
            'div:has(> #software-tipo-licencia)',
            'header button:has-text("Agregar")',
            'table',
        ], wait_ms=1500)

        # -------------------------------------------------------------
        # 14. SOFTWARE - INSTALACIONES (/software/instalaciones)
        # -------------------------------------------------------------
        print("\n[14/17] Instalaciones de Software (/software/instalaciones)...")
        page.goto('http://localhost:5173/software/instalaciones')
        page.wait_for_load_state('networkidle')
        capture_and_annotate(page, '14_software_instalaciones.png', [
            'section:has(#instalaciones-search) form',
            'header button:has-text("Instalar software")',
            'table',
        ], wait_ms=1500)

        # -------------------------------------------------------------
        # 15. MANTENIMIENTO - TABLERO (/mantenimiento)
        # -------------------------------------------------------------
        print("\n[15/17] Órdenes de Mantenimiento (/mantenimiento)...")
        page.goto('http://localhost:5173/mantenimiento')
        page.wait_for_load_state('networkidle')
        capture_and_annotate(page, '15_mantenimiento_tablero.png', [
            'div:has(> #mant-search)',
            ['div:has(> #mant-tipo)', 'button:has-text("Limpiar")'],
            'header button:has-text("Agregar")',
            'table',
        ], wait_ms=1500)

        # -------------------------------------------------------------
        # 16. INCIDENCIAS (/incidencias)
        # -------------------------------------------------------------
        print("\n[16/17] Reportes de Incidencias (/incidencias)...")
        page.goto('http://localhost:5173/incidencias')
        page.wait_for_load_state('networkidle')
        capture_and_annotate(page, '16_incidencias_reportes.png', [
            'div:has(> #incidencias-search)',
            'div.flex.flex-wrap.items-end.gap-3:has(#incidencias-espacio)',
            'header button:has-text("Reportar")',
            'table',
        ], wait_ms=1500)

        # -------------------------------------------------------------
        # 17. HISTORIAL Y AUDITORÍA (/historial)
        # -------------------------------------------------------------
        print("\n[17/17] Historial de Auditoría (/historial)...")
        page.goto('http://localhost:5173/historial')
        page.wait_for_load_state('networkidle')
        capture_and_annotate(page, '17_historial_auditoria.png', [
            ['div:has(> #historial-modulo)', 'div:has(> #historial-evento)'],
            ['div:has(> #historial-desde)', 'div:has(> #historial-hasta)'],
            'table',
        ], wait_ms=1500)

        browser.close()

    print("\n================================================================")
    print("PIPELINE DINÁMICO COMPLETADO — 17 CAPTURAS ANOTADAS CON ÉXITO")
    for d in OUTPUT_DIRS:
        print(f"Ruta actualizada: {d.resolve()}")
    print("================================================================")

if __name__ == '__main__':
    run_capture_pipeline()
