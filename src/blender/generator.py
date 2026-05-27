"""
Gerador de Placas 3D para Bambu Lab A1
Versão corrigida com geometria sólida e sem non-manifold edges
"""

import bpy
import bmesh
import os
import sys
from pathlib import Path
from mathutils import Vector

# --- CONSTANTES ---
PLATE_WIDTH = 200.0
DEFAULT_PLATE_HEIGHT = 180.0
REDUCED_PLATE_HEIGHT = 128.0
PLATE_HEIGHT = DEFAULT_PLATE_HEIGHT
PLATE_DEPTH = 2.0
CORNER_CUT = 42.48

# Z-Logic (relativo à base Z=0)
Z_PLATE_TOP = PLATE_DEPTH  # 2.0mm
Z_TEXT_BASE = PLATE_DEPTH - 0.3  # 1.7mm (escavado)
Z_TEXT_TOP = PLATE_DEPTH + 0.4  # 2.4mm (salto)
TEXT_HEIGHT = Z_TEXT_TOP - Z_TEXT_BASE  # 0.7mm

# Texto
MARGIN_X = 20.0
MARGIN_Y = 30.0
MAX_TEXT_WIDTH = PLATE_WIDTH - (MARGIN_X * 2)
DEFAULT_FONT_SIZE = 20.0
MIN_FONT_SIZE = 5.0

# Rodapé
DEFAULT_FOOTER_TEXT = os.environ.get("CONDO_NAME", "Condominio Astro")
FOOTER_FONT_SIZE = 8.0
FOOTER_MARGIN_X = 15.0
FOOTER_MARGIN_Y = 12.0

DEBUG = os.environ.get("LOG_LEVEL", "INFO").upper() == "DEBUG"

def log(msg):
    if DEBUG:
        print(f"[GEN] {msg}")


def get_max_text_height(plate_height):
    """Return vertical space available for the main text."""
    return plate_height - (MARGIN_Y * 2) - 20


def normalize_plate_height(value):
    """Allow only the official plate heights."""
    try:
        height = float(value)
    except (TypeError, ValueError):
        return DEFAULT_PLATE_HEIGHT

    if abs(height - REDUCED_PLATE_HEIGHT) < 0.01:
        return REDUCED_PLATE_HEIGHT
    return DEFAULT_PLATE_HEIGHT


def normalize_footer_text(value):
    """Return a non-empty footer text."""
    if value is None:
        return DEFAULT_FOOTER_TEXT

    text = str(value).strip()
    return text if text else DEFAULT_FOOTER_TEXT


def clear_scene():
    """Limpa a cena completamente"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)
    for font in bpy.data.fonts:
        if font.users == 0:
            bpy.data.fonts.remove(font)


def get_font():
    """Carrega fonte Roboto Bold"""
    paths = [
        "/app/assets/fonts/Roboto-Bold.ttf",
        "/usr/share/fonts/truetype/Roboto-Bold.ttf",
        str(Path(__file__).parent.parent.parent / "assets" / "fonts" / "Roboto-Bold.ttf"),
    ]
    for p in paths:
        if os.path.exists(p):
            log(f"Fonte: {p}")
            return bpy.data.fonts.load(p)
    log("Fonte não encontrada, usando padrão")
    return None


def create_plate(plate_height=DEFAULT_PLATE_HEIGHT):
    """Cria placa base como mesh sólido com chanfro"""
    log(f"Criando placa {PLATE_WIDTH}x{plate_height}x{PLATE_DEPTH}mm")
    
    half_w = PLATE_WIDTH / 2
    half_h = plate_height / 2
    
    # Vértices do pentágono (base e topo)
    verts = [
        # Base (Z=0)
        Vector((-half_w, half_h, 0)),           # 0 TL
        Vector((half_w, half_h, 0)),            # 1 TR
        Vector((half_w, -half_h + CORNER_CUT, 0)),  # 2 BR início chanfro
        Vector((half_w - CORNER_CUT, -half_h, 0)),  # 3 BR fim chanfro
        Vector((-half_w, -half_h, 0)),          # 4 BL
        # Topo (Z=PLATE_DEPTH)
        Vector((-half_w, half_h, PLATE_DEPTH)),
        Vector((half_w, half_h, PLATE_DEPTH)),
        Vector((half_w, -half_h + CORNER_CUT, PLATE_DEPTH)),
        Vector((half_w - CORNER_CUT, -half_h, PLATE_DEPTH)),
        Vector((-half_w, -half_h, PLATE_DEPTH)),
    ]
    
    # Faces (ordem anti-horária para normais externas)
    faces = [
        (0, 1, 2, 3, 4),     # Base (invertida para normal para baixo)
        (9, 8, 7, 6, 5),     # Topo
        (0, 5, 6, 1),        # Frente (Y+)
        (1, 6, 7, 2),        # Direita (X+)
        (2, 7, 8, 3),        # Chanfro
        (3, 8, 9, 4),        # Baixo (Y-)
        (4, 9, 5, 0),        # Esquerda (X-)
    ]
    
    mesh = bpy.data.meshes.new("Placa_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Recalcula normais
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    
    plate = bpy.data.objects.new("Placa", mesh)
    bpy.context.collection.objects.link(plate)
    
    log(f"Placa: {len(mesh.vertices)} verts, {len(mesh.polygons)} faces")
    return plate


def create_solid_text(text, size, location, align='CENTER', name="Texto"):
    """Cria texto 3D sólido e manifold"""
    log(f"Criando texto: '{text[:30]}...' @ {size}mm")
    
    # Cria objeto de texto
    curve = bpy.data.curves.new(name=name, type='FONT')
    curve.body = text
    curve.size = size
    curve.align_x = align
    curve.align_y = 'CENTER'
    
    # Extrusão para criar volume (metade da altura total)
    curve.extrude = TEXT_HEIGHT / 2
    curve.bevel_depth = 0
    curve.bevel_resolution = 0
    
    # Carrega fonte
    font = get_font()
    if font:
        curve.font = font
    
    # Cria objeto
    text_obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(text_obj)
    
    # Posiciona (centro do texto no Z_TEXT_BASE + metade da altura)
    z_center = Z_TEXT_BASE + TEXT_HEIGHT / 2
    text_obj.location = (location[0], location[1], z_center)
    
    # Converte para mesh
    bpy.context.view_layer.objects.active = text_obj
    text_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    
    # Limpa geometria
    mesh = text_obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    # Remove vértices duplicados
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    
    # Recalcula normais
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    bm.to_mesh(mesh)
    bm.free()
    
    log(f"  Resultado: {len(mesh.vertices)} verts, {len(mesh.polygons)} faces")
    return text_obj


def wrap_text_to_fit(text, font, font_size, max_width):
    """Quebra o texto em múltiplas linhas garantindo que cabe na largura"""
    curve = bpy.data.curves.new("temp_wrap", type='FONT')
    if font:
        curve.font = font
    curve.size = font_size
    temp = bpy.data.objects.new("temp_wrap", curve)
    bpy.context.collection.objects.link(temp)
    
    wrapped_lines = []
    for p in text.split('\n'):
        if not p.strip():
            wrapped_lines.append("")
            continue
        words = p.split(' ')
        current_line = words[0]
        
        for word in words[1:]:
            test_line = current_line + " " + word
            curve.body = test_line
            bpy.context.view_layer.update()
            
            if temp.dimensions.x > max_width:
                wrapped_lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        wrapped_lines.append(current_line)
        
    bpy.data.objects.remove(temp)
    bpy.data.curves.remove(curve)
    return '\n'.join(wrapped_lines)

def calculate_font_size(text, font, plate_height=DEFAULT_PLATE_HEIGHT):
    """Calcula tamanho de fonte para caber na área, aplicando quebra de texto"""
    size = DEFAULT_FONT_SIZE
    best_text = text
    max_text_height = get_max_text_height(plate_height)
    
    while size > MIN_FONT_SIZE:
        wrapped_text = wrap_text_to_fit(text, font, size, MAX_TEXT_WIDTH)
        lines = wrapped_text.split('\n')
        total_height = len(lines) * size * 1.3
        
        # Testa se a altura total não excede o máximo permitido
        if total_height <= max_text_height:
            best_text = wrapped_text
            break
            
        size -= 1.0
        
    if size <= MIN_FONT_SIZE:
        size = MIN_FONT_SIZE
        best_text = wrap_text_to_fit(text, font, size, MAX_TEXT_WIDTH)
    
    log(f"Tamanho calculado: {size}mm")
    return size, best_text


def generate_plate(text, output_path, custom_font_size=None, align='CENTER', plate_height=DEFAULT_PLATE_HEIGHT, footer_text=DEFAULT_FOOTER_TEXT):
    """Função principal de geração"""
    plate_height = normalize_plate_height(plate_height)
    footer_text = normalize_footer_text(footer_text)
    log("=" * 50)
    log("INICIANDO GERAÇÃO DE PLACA")
    log("=" * 50)
    log(f"Texto: {text}")
    log(f"Output: {output_path}")
    log(f"Fonte customizada: {custom_font_size}")
    log(f"Altura da placa: {plate_height}mm")
    log(f"Rodape: {footer_text}")
    
    clear_scene()
    
    # 1. Criar placa base
    plate = create_plate(plate_height)
    
    # 2. Determinar tamanho de fonte e quebrar o texto
    font = get_font()
    if custom_font_size and custom_font_size >= MIN_FONT_SIZE:
        font_size = custom_font_size
        log(f"Usando fonte customizada: {font_size}mm")
        text = wrap_text_to_fit(text, font, font_size, MAX_TEXT_WIDTH)
    else:
        font_size, text = calculate_font_size(text, font, plate_height)
    
    # 3. Criar texto principal (centralizado)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    text_objects = []
    
    total_height = len(lines) * font_size * 1.3
    start_y = total_height / 2 - font_size / 2
    
    for i, line in enumerate(lines):
        y = start_y - (i * font_size * 1.3)
        if align == 'LEFT' or (align == 'LEFT_CENTER_TITLE' and i > 0):
            x = -PLATE_WIDTH/2 + MARGIN_X
            current_align = 'LEFT'
        elif align == 'RIGHT':
            x = PLATE_WIDTH/2 - MARGIN_X
            current_align = 'RIGHT'
        else:
            x = 0
            current_align = 'CENTER'
        txt = create_solid_text(line, font_size, (x, y), align=current_align, name=f"Texto_{i}")
        text_objects.append(txt)
    
    # 4. Criar rodapé
    footer_x = -PLATE_WIDTH/2 + FOOTER_MARGIN_X
    footer_y = -plate_height/2 + FOOTER_MARGIN_Y
    footer = create_solid_text(footer_text, FOOTER_FONT_SIZE, 
                               (footer_x, footer_y), 
                               align='LEFT', name="Rodape")
    text_objects.append(footer)
    
    # 5. Juntar todos os textos
    bpy.ops.object.select_all(action='DESELECT')
    for obj in text_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = text_objects[0]
    bpy.ops.object.join()
    
    combined_text = bpy.context.active_object
    combined_text.name = "Texto"
    
    # 6. Limpar geometria final
    mesh = combined_text.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    
    log(f"Texto final: {len(mesh.vertices)} verts, {len(mesh.polygons)} faces")
    
    # 7. Verificar geometria
    log("--- VERIFICAÇÃO ---")
    for obj in [plate, combined_text]:
        log(f"{obj.name}: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} faces")
    
    # 8. Exportar
    log("Exportando 3MF...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    import threemf_exporter
    
    # Importante: recuperar objetos pelo nome
    plate_obj = bpy.data.objects.get("Placa")
    text_obj = bpy.data.objects.get("Texto")
    
    if not plate_obj or not text_obj:
        log("ERRO: Objetos não encontrados!")
        return None
    
    objects = [
        {"obj": plate_obj, "extruder": 1, "name": "Placa"},
        {"obj": text_obj, "extruder": 2, "name": "Texto"},
    ]
    
    result = threemf_exporter.export(output_path, objects)
    
    if result and os.path.exists(output_path):
        log(f"Sucesso! Arquivo: {os.path.getsize(output_path)} bytes")
    else:
        log("ERRO na exportação!")
    
    log("=" * 50)
    return result


def main():
    argv = sys.argv
    if '--' in argv:
        argv = argv[argv.index('--') + 1:]
    
    if len(argv) < 1:
        print("Uso: blender --background --python generator.py -- 'TEXTO' output.3mf [font_size] [align] [plate_height] [footer_text]")
        sys.exit(1)
    
    text = argv[0]
    default_output = Path(__file__).parent.parent.parent / "output" / "placa.3mf"
    default_output.parent.mkdir(exist_ok=True, parents=True)
    output = argv[1] if len(argv) > 1 else str(default_output)
    
    # Novo: Tamanho de fonte customizado (opcional)
    custom_font_size = None
    if len(argv) > 2:
        try:
            custom_font_size = float(argv[2])
        except ValueError:
            pass
    
    align = 'CENTER'
    if len(argv) > 3:
        align = argv[3]

    plate_height = DEFAULT_PLATE_HEIGHT
    if len(argv) > 4:
        plate_height = normalize_plate_height(argv[4])

    footer_text = DEFAULT_FOOTER_TEXT
    if len(argv) > 5:
        footer_text = normalize_footer_text(argv[5])
    
    try:
        result = generate_plate(text, output, custom_font_size, align, plate_height, footer_text)
        sys.exit(0 if result else 1)
    except Exception as e:
        import traceback
        print(f"ERRO: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
