import os
import re
import sys
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = Path('d:/Descargas google/KairOs')
DOCS_DIR = BASE_DIR / 'docs'

# APA 7 Typography & Strict Color Standard: 100% BLACK
COLOR_BLACK = RGBColor(0, 0, 0)
FONT_NAME = 'Times New Roman'

def set_apa_margins(doc):
    """Sets standard APA 7 margins (1.0 inch / 2.54 cm on all sides)."""
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

def add_page_number_to_header(section):
    """Adds right-aligned APA 7 dynamic page number to the header."""
    header = section.header
    header.is_linked_to_previous = False
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.first_line_indent = Inches(0)
    
    r = p.add_run()
    r.font.name = FONT_NAME
    r.font.size = Pt(10)
    r.font.color.rgb = COLOR_BLACK
    
    # Dynamic Word PAGE field
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    r._r.append(fldChar1)
    r._r.append(instrText)
    r._r.append(fldChar2)
    r._r.append(fldChar3)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    """Sets internal padding for a table cell in dxa units."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def apply_apa7_table_borders(table):
    """Applies strict APA 7 table border formatting:
    - Top horizontal border (single, black, size 8)
    - Bottom horizontal border of header (single, black, size 8)
    - Bottom horizontal border of table (single, black, size 8)
    - NO vertical borders and NO inner horizontal borders.
    """
    tblPr = table._tbl.tblPr
    borders_elm = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>
            <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="none"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders_elm)
    
    # Bottom border for header row cells
    if len(table.rows) > 0:
        for cell in table.rows[0].cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(f'''
                <w:tcBorders {nsdecls("w")}>
                    <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>
                </w:tcBorders>
            ''')
            tcPr.append(tcBorders)

class DocumentState:
    def __init__(self):
        self.figure_count = 0
        self.table_count = 0

def parse_markdown_to_docx(md_path, doc, state=None):
    if state is None:
        state = DocumentState()
        
    print(f"  Procesando (APA 7): {md_path.relative_to(BASE_DIR)}")
    content = md_path.read_text(encoding='utf-8')
    lines = content.splitlines()
    
    in_code_block = False
    code_lang = ""
    code_lines = []
    
    in_table = False
    table_rows = []
    pending_table_title = ""
    
    def flush_table():
        nonlocal in_table, table_rows, pending_table_title
        if not table_rows:
            in_table = False
            return
            
        state.table_count += 1
        
        # 1. APA 7 Table Label: Tabla [N] (Bold, Left)
        p_tbl_num = doc.add_paragraph()
        p_tbl_num.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_tbl_num.paragraph_format.first_line_indent = Inches(0)
        p_tbl_num.paragraph_format.space_before = Pt(14)
        p_tbl_num.paragraph_format.space_after = Pt(2)
        r_num = p_tbl_num.add_run(f"Tabla {state.table_count}")
        r_num.font.name = FONT_NAME
        r_num.font.size = Pt(10.5)
        r_num.font.bold = True
        r_num.font.color.rgb = COLOR_BLACK
        
        # 2. APA 7 Table Title (Italics, Left)
        p_tbl_title = doc.add_paragraph()
        p_tbl_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_tbl_title.paragraph_format.first_line_indent = Inches(0)
        p_tbl_title.paragraph_format.space_after = Pt(6)
        title_text = pending_table_title if pending_table_title else f"Estructura y Especificación de Datos — Registro {state.table_count}"
        r_title = p_tbl_title.add_run(title_text)
        r_title.font.name = FONT_NAME
        r_title.font.size = Pt(10.5)
        r_title.font.italic = True
        r_title.font.color.rgb = COLOR_BLACK
        pending_table_title = ""
        
        # 3. Create Table
        header = table_rows[0]
        num_cols = len(header)
        data_rows = table_rows[1:]
        
        table = doc.add_table(rows=len(data_rows) + 1, cols=num_cols)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        apply_apa7_table_borders(table)
        
        # Header Row
        hdr_cells = table.rows[0].cells
        for idx, text in enumerate(header):
            if idx < len(hdr_cells):
                hdr_cells[idx].text = text.strip()
                set_cell_margins(hdr_cells[idx], top=100, bottom=100, left=120, right=120)
                p = hdr_cells[idx].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.first_line_indent = Inches(0)
                for r in p.runs:
                    r.font.name = FONT_NAME
                    r.font.bold = True
                    r.font.color.rgb = COLOR_BLACK
                    r.font.size = Pt(9.5)
                    
        # Data Rows
        for r_idx, row_data in enumerate(data_rows):
            row_cells = table.rows[r_idx + 1].cells
            for c_idx, cell_value in enumerate(row_data):
                if c_idx < len(row_cells):
                    row_cells[c_idx].text = cell_value.strip().replace('<br>', '\n')
                    set_cell_margins(row_cells[c_idx], top=70, bottom=70, left=120, right=120)
                    p = row_cells[c_idx].paragraphs[0]
                    p.paragraph_format.first_line_indent = Inches(0)
                    for r in p.runs:
                        r.font.name = FONT_NAME
                        r.font.size = Pt(9)
                        r.font.color.rgb = COLOR_BLACK
                        
        p_space = doc.add_paragraph()
        p_space.paragraph_format.space_before = Pt(2)
        p_space.paragraph_format.space_after = Pt(6)
        p_space.paragraph_format.first_line_indent = Inches(0)
        table_rows = []
        in_table = False

    def flush_code():
        nonlocal in_code_block, code_lines, code_lang
        if not code_lines:
            in_code_block = False
            return
            
        code_text = '\n'.join(code_lines).strip()
        
        # Filter raw mermaid diagram blocks in Word documents
        if code_lang == 'mermaid' or code_text.startswith(('erDiagram', 'sequenceDiagram', 'flowchart', 'graph')):
            # Do NOT dump raw mermaid text into Word document!
            code_lines = []
            in_code_block = False
            return
            
        # Regular Code Block (Formatted neatly in black Consolas font)
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.right_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(code_text)
        r.font.name = 'Consolas'
        r.font.size = Pt(8.5)
        r.font.color.rgb = COLOR_BLACK
        code_lines = []
        in_code_block = False

    idx = 0
    total_lines = len(lines)
    while idx < total_lines:
        line = lines[idx]
        stripped = line.strip()
        idx += 1
        
        # Code block delimiter
        if stripped.startswith('```'):
            if in_code_block:
                flush_code()
            else:
                if in_table:
                    flush_table()
                in_code_block = True
                code_lang = stripped[3:].strip().lower()
                code_lines = []
            continue
            
        if in_code_block:
            code_lines.append(line)
            continue
            
        # Table row
        if stripped.startswith('|') and stripped.endswith('|'):
            if re.match(r'^\|[\s\:\-\|]+$', stripped):
                continue
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            table_rows.append(cells)
            in_table = True
            continue
        elif in_table:
            flush_table()
            
        # Horizontal rule
        if re.match(r'^(?:---|\*\*\*|___)$', stripped):
            continue
            
        # Empty line
        if not stripped:
            continue
            
        # Headings (Strict APA 7 Hierarchy with Black Text)
        if stripped.startswith('# '):
            h1 = doc.add_paragraph()
            h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
            h1.paragraph_format.space_before = Pt(20)
            h1.paragraph_format.space_after = Pt(8)
            h1.paragraph_format.first_line_indent = Inches(0)
            r = h1.add_run(stripped[2:])
            r.font.name = FONT_NAME
            r.font.size = Pt(14)
            r.font.bold = True
            r.font.color.rgb = COLOR_BLACK
            continue
        elif stripped.startswith('## '):
            h2 = doc.add_paragraph()
            h2.alignment = WD_ALIGN_PARAGRAPH.LEFT
            h2.paragraph_format.space_before = Pt(16)
            h2.paragraph_format.space_after = Pt(6)
            h2.paragraph_format.first_line_indent = Inches(0)
            r = h2.add_run(stripped[3:])
            r.font.name = FONT_NAME
            r.font.size = Pt(12.5)
            r.font.bold = True
            r.font.color.rgb = COLOR_BLACK
            continue
        elif stripped.startswith('### '):
            h3 = doc.add_paragraph()
            h3.alignment = WD_ALIGN_PARAGRAPH.LEFT
            h3.paragraph_format.space_before = Pt(12)
            h3.paragraph_format.space_after = Pt(4)
            h3.paragraph_format.first_line_indent = Inches(0)
            r = h3.add_run(stripped[4:])
            r.font.name = FONT_NAME
            r.font.size = Pt(12)
            r.font.bold = True
            r.font.italic = True
            r.font.color.rgb = COLOR_BLACK
            continue
        elif stripped.startswith('#### '):
            h4 = doc.add_paragraph()
            h4.alignment = WD_ALIGN_PARAGRAPH.LEFT
            h4.paragraph_format.left_indent = Inches(0.5)
            h4.paragraph_format.first_line_indent = Inches(0)
            h4.paragraph_format.space_before = Pt(8)
            h4.paragraph_format.space_after = Pt(3)
            r = h4.add_run(stripped[5:])
            r.font.name = FONT_NAME
            r.font.size = Pt(11.5)
            r.font.bold = True
            r.font.color.rgb = COLOR_BLACK
            continue
            
        # Images: ![alt](path) - Strict APA 7 Figure Formatting
        img_match = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', stripped)
        if img_match:
            alt_text = img_match.group(1).strip()
            img_rel_path = img_match.group(2).strip()
            img_file = (md_path.parent / img_rel_path).resolve()
            
            state.figure_count += 1
            
            # Clean Alt Text / Title
            clean_title = alt_text
            if re.match(r'^Figura\s*\d+\s*:\s*', clean_title, re.IGNORECASE):
                clean_title = re.sub(r'^Figura\s*\d+\s*:\s*', '', clean_title, flags=re.IGNORECASE)
            if not clean_title:
                clean_title = f"Captura o Diagrama del Sistema KairOs ({img_file.stem})"
                
            # 1. APA 7 Figure Label: Figura [N] (Bold, Left, Black)
            p_fig_label = doc.add_paragraph()
            p_fig_label.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p_fig_label.paragraph_format.first_line_indent = Inches(0)
            p_fig_label.paragraph_format.space_before = Pt(14)
            p_fig_label.paragraph_format.space_after = Pt(2)
            r_fl = p_fig_label.add_run(f"Figura {state.figure_count}")
            r_fl.font.name = FONT_NAME
            r_fl.font.size = Pt(10.5)
            r_fl.font.bold = True
            r_fl.font.color.rgb = COLOR_BLACK
            
            # 2. APA 7 Figure Title (Italics, Left, Black)
            p_fig_title = doc.add_paragraph()
            p_fig_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p_fig_title.paragraph_format.first_line_indent = Inches(0)
            p_fig_title.paragraph_format.space_after = Pt(6)
            r_ft = p_fig_title.add_run(clean_title)
            r_ft.font.name = FONT_NAME
            r_ft.font.size = Pt(10.5)
            r_ft.font.italic = True
            r_ft.font.color.rgb = COLOR_BLACK
            
            # 3. Figure Picture (Centered)
            if img_file.exists():
                try:
                    p_pic = doc.add_paragraph()
                    p_pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_pic.paragraph_format.first_line_indent = Inches(0)
                    p_pic.paragraph_format.space_before = Pt(4)
                    p_pic.paragraph_format.space_after = Pt(6)
                    r_pic = p_pic.add_run()
                    r_pic.add_picture(str(img_file), width=Inches(6.0))
                except Exception as ex:
                    p_err = doc.add_paragraph(f"[Error al insertar imagen: {img_file.name}]")
                    p_err.paragraph_format.first_line_indent = Inches(0)
            else:
                p_err = doc.add_paragraph(f"[Imagen no encontrada: {img_rel_path}]")
                p_err.paragraph_format.first_line_indent = Inches(0)
                
            # 4. Check if next non-empty line is an APA Note: *Nota.* ...
            if idx < total_lines:
                next_line = lines[idx].strip()
                if next_line.startswith(('*Nota.*', '> Nota:', '*Nota:')):
                    idx += 1 # consume note line
                    note_text = next_line
                    p_note = doc.add_paragraph()
                    p_note.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    p_note.paragraph_format.first_line_indent = Inches(0)
                    p_note.paragraph_format.space_before = Pt(3)
                    p_note.paragraph_format.space_after = Pt(14)
                    
                    # Format "Nota." in italics, followed by description
                    r_lbl = p_note.add_run("Nota. ")
                    r_lbl.font.name = FONT_NAME
                    r_lbl.font.size = Pt(9.5)
                    r_lbl.font.italic = True
                    r_lbl.font.color.rgb = COLOR_BLACK
                    
                    clean_note = re.sub(r'^(\*Nota\.\*|> Nota:|\*Nota:)\s*', '', note_text)
                    r_desc = p_note.add_run(clean_note)
                    r_desc.font.name = FONT_NAME
                    r_desc.font.size = Pt(9.5)
                    r_desc.font.color.rgb = COLOR_BLACK
            continue
            
        # Bullet list
        if re.match(r'^[-*]\s+', stripped):
            item_text = re.sub(r'^[-*]\s+', '', stripped)
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            add_apa7_formatted_runs(p, item_text)
            continue
            
        # Numbered list
        if re.match(r'^\d+\.\s+', stripped):
            item_text = re.sub(r'^\d+\.\s+', '', stripped)
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            add_apa7_formatted_runs(p, item_text)
            continue
            
        # Blockquote: > text
        if stripped.startswith('> '):
            quote_text = stripped[2:]
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.right_indent = Inches(0.5)
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.space_after = Pt(4)
            r = p.add_run(quote_text)
            r.font.name = FONT_NAME
            r.font.size = Pt(10.5)
            r.font.italic = True
            r.font.color.rgb = COLOR_BLACK
            continue
            
        # Regular paragraph (Standard APA 7: First Line Indent 0.5 inches, 1.5 line spacing, 100% black font)
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = Inches(0.5)
        p.paragraph_format.line_spacing = 1.35
        p.paragraph_format.space_after = Pt(4)
        add_apa7_formatted_runs(p, stripped)

    if in_table:
        flush_table()
    if in_code_block:
        flush_code()

def add_apa7_formatted_runs(paragraph, text):
    """Parses text for bold, italic, and inline code with STRICT 100% BLACK font."""
    tokens = re.split(r'(\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)', text)
    for token in tokens:
        if not token:
            continue
        if token.startswith('***') and token.endswith('***'):
            r = paragraph.add_run(token[3:-3])
            r.font.name = FONT_NAME
            r.font.bold = True
            r.font.italic = True
            r.font.color.rgb = COLOR_BLACK
            r.font.size = Pt(11)
        elif token.startswith('**') and token.endswith('**'):
            r = paragraph.add_run(token[2:-2])
            r.font.name = FONT_NAME
            r.font.bold = True
            r.font.color.rgb = COLOR_BLACK
            r.font.size = Pt(11)
        elif token.startswith('*') and token.endswith('*'):
            r = paragraph.add_run(token[1:-1])
            r.font.name = FONT_NAME
            r.font.italic = True
            r.font.color.rgb = COLOR_BLACK
            r.font.size = Pt(11)
        elif token.startswith('`') and token.endswith('`'):
            r = paragraph.add_run(token[1:-1])
            r.font.name = 'Consolas'
            r.font.size = Pt(9.5)
            r.font.bold = True
            r.font.color.rgb = COLOR_BLACK
        else:
            r = paragraph.add_run(token)
            r.font.name = FONT_NAME
            r.font.color.rgb = COLOR_BLACK
            r.font.size = Pt(11)

def build_apa7_title_page(doc, title, subtitle, author, institution, note="Formato APA 7ma Edición"):
    """Creates a standardized APA 7 Cover / Title Page with pure black text."""
    set_apa_margins(doc)
    
    # Title paragraph
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(90)
    p_title.paragraph_format.space_after = Pt(12)
    p_title.paragraph_format.first_line_indent = Inches(0)
    r_title = p_title.add_run(title)
    r_title.font.name = FONT_NAME
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_BLACK
    
    # Subtitle
    if subtitle:
        p_sub = doc.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sub.paragraph_format.space_after = Pt(36)
        p_sub.paragraph_format.first_line_indent = Inches(0)
        r_sub = p_sub.add_run(subtitle)
        r_sub.font.name = FONT_NAME
        r_sub.font.size = Pt(13)
        r_sub.font.color.rgb = COLOR_BLACK
        
    # Metadata Block
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_before = Pt(30)
    p_meta.paragraph_format.space_after = Pt(4)
    p_meta.paragraph_format.first_line_indent = Inches(0)
    r_auth = p_meta.add_run(author)
    r_auth.font.name = FONT_NAME
    r_auth.font.size = Pt(12)
    r_auth.font.bold = True
    r_auth.font.color.rgb = COLOR_BLACK
    
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_after = Pt(4)
    p_inst.paragraph_format.first_line_indent = Inches(0)
    r_inst = p_inst.add_run(institution)
    r_inst.font.name = FONT_NAME
    r_inst.font.size = Pt(11.5)
    r_inst.font.color.rgb = COLOR_BLACK
    
    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_after = Pt(12)
    p_date.paragraph_format.first_line_indent = Inches(0)
    r_date = p_date.add_run(f"Septiembre 2026 • {note}")
    r_date.font.name = FONT_NAME
    r_date.font.size = Pt(11)
    r_date.font.italic = True
    r_date.font.color.rgb = COLOR_BLACK
    
    # Page Break after Title Page
    doc.add_page_break()
    
    # Add page number to header in main document section
    add_page_number_to_header(doc.sections[0])

def save_docx_safely(doc, target_file):
    """Saves a Document, falling back to a _APA7 suffixed file if locked by Microsoft Word."""
    target_path = Path(target_file)
    try:
        doc.save(str(target_path))
        print(f"[OK] Documento Word generado exitosamente: {target_path.resolve()}")
        return target_path
    except PermissionError:
        alt_path = target_path.with_name(f"{target_path.stem}_APA7{target_path.suffix}")
        try:
            doc.save(str(alt_path))
            print(f"\n[AVISO] '{target_path.name}' está actualmente abierto en Microsoft Word.")
            print(f"[OK] Se guardó la versión actualizada en: {alt_path.resolve()}")
            print(f"      (Cierra Microsoft Word para poder sobrescribir el archivo original directamente)\n")
            return alt_path
        except Exception as e:
            print(f"[ERROR] No se pudo guardar ni en {target_path.name} ni en {alt_path.name}: {e}")
            return None

def copy_file_safely(src_path, dst_path):
    """Copies a file safely, falling back to _APA7 if locked."""
    import shutil
    src = Path(src_path)
    dst = Path(dst_path)
    if not dst.parent.exists():
        return
    try:
        shutil.copy2(src, dst)
        print(f"[OK] Archivo sincronizado: {dst.resolve()}")
    except PermissionError:
        alt_dst = dst.with_name(f"{dst.stem}_APA7{dst.suffix}")
        try:
            shutil.copy2(src, alt_dst)
            print(f"[AVISO] '{dst.name}' está abierto en Word. Sincronizado en: {alt_dst.resolve()}")
        except Exception as e:
            print(f"[ERROR] No se pudo sincronizar: {e}")

def export_manual_usuario_word():
    doc = Document()
    build_apa7_title_page(
        doc,
        title="KairOs Campus & Labs",
        subtitle="Manual de Usuario Oficial — Guía Operativa Paso a Paso con Capturas de Pantalla Anotadas",
        author="Equipo de Aseguramiento de Calidad y Desarrollo de Software",
        institution="Dirección de Tecnologías de la Información • Universidad / Instituto KairOs",
        note="Formato APA 7ma Edición"
    )
    
    manual_md = DOCS_DIR / 'manual_usuario' / 'MANUAL_DE_USUARIO.md'
    state = DocumentState()
    parse_markdown_to_docx(manual_md, doc, state)
    
    out_file = DOCS_DIR / 'manual_usuario' / 'Manual_de_Usuario_KairOs.docx'
    saved_path = save_docx_safely(doc, out_file)
    
    if saved_path:
        root_out_file = BASE_DIR / 'manual_usuario' / 'Manual_de_Usuario_KairOs.docx'
        copy_file_safely(saved_path, root_out_file)

def export_documentacion_tecnica_word():
    doc = Document()
    build_apa7_title_page(
        doc,
        title="KairOs Campus & Labs — Documentación Técnica de Arquitectura",
        subtitle="Especificación de Backend Django DRF, Frontend Vue 3, Base de Datos Relacional y Módulos",
        author="Dirección de Arquitectura de Sistemas y Tecnologías de la Información",
        institution="Proyecto Institucional KairOs Campus & Labs",
        note="Formato APA 7ma Edición"
    )
    
    files_to_include = [
        DOCS_DIR / 'README.md',
        DOCS_DIR / 'MODULOS.md',
        DOCS_DIR / 'backend' / 'requerimientos_backend.md',
        DOCS_DIR / 'backend' / 'api_endpoints.md',
        DOCS_DIR / 'frontend' / 'requerimientos_frontend.md',
        DOCS_DIR / 'frontend' / 'rutas_y_vistas.md',
        DOCS_DIR / 'base-de-datos' / 'database_schema.md',
        DOCS_DIR / 'base-de-datos' / 'diccionario_de_datos.md',
    ]
    
    state = DocumentState()
    for f in files_to_include:
        if f.exists():
            parse_markdown_to_docx(f, doc, state)
            doc.add_page_break()
            
    out_file = DOCS_DIR / 'Documentacion_Tecnica_KairOs.docx'
    save_docx_safely(doc, out_file)

def export_documentacion_completa_word():
    doc = Document()
    build_apa7_title_page(
        doc,
        title="KairOs — Documentación Integral del Sistema",
        subtitle="Arquitectura Técnica, Base de Datos, Módulos Operativos y Manual de Usuario Oficial",
        author="Dirección de Tecnologías de la Información y Transformación Digital",
        institution="Sistema de Gestión de Infraestructura KairOs",
        note="Formato APA 7ma Edición"
    )
    
    files_to_include = [
        DOCS_DIR / 'README.md',
        DOCS_DIR / 'MODULOS.md',
        DOCS_DIR / 'backend' / 'requerimientos_backend.md',
        DOCS_DIR / 'backend' / 'api_endpoints.md',
        DOCS_DIR / 'frontend' / 'requerimientos_frontend.md',
        DOCS_DIR / 'frontend' / 'rutas_y_vistas.md',
        DOCS_DIR / 'base-de-datos' / 'database_schema.md',
        DOCS_DIR / 'base-de-datos' / 'diccionario_de_datos.md',
        DOCS_DIR / 'manual_usuario' / 'MANUAL_DE_USUARIO.md',
    ]
    
    state = DocumentState()
    for f in files_to_include:
        if f.exists():
            parse_markdown_to_docx(f, doc, state)
            doc.add_page_break()
            
    out_file = DOCS_DIR / 'Documentacion_Completa_KairOs.docx'
    save_docx_safely(doc, out_file)

def main():
    print("==================================================================")
    print("EXPORTADOR DE DOCUMENTACIÓN A MICROSOFT WORD — ESTÁNDAR APA 7MA ED.")
    print("  • Tipografía: Times New Roman")
    print("  • Color de Fuente: 100% Negro (#000000)")
    print("  • Márgenes: 2.54 cm (1.0 pulgada) en todos los lados")
    print("  • Tablas: Estructura APA 7 (sin líneas verticales)")
    print("  • Figuras: Numeración y notas APA 7 con diagramas en alta definición")
    print("==================================================================")
    export_manual_usuario_word()
    export_documentacion_tecnica_word()
    export_documentacion_completa_word()
    print("==================================================================")
    print("TODOS LOS DOCUMENTOS WORD EN FORMATO APA 7 HAN SIDO GENERADOS.")
    print("==================================================================")

if __name__ == '__main__':
    main()
