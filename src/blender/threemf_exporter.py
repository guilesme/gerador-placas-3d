"""
Exportador 3MF para Bambu Studio
Estrutura compatível com formato Bambu Lab
"""

import zipfile
import os
import uuid
import datetime
import json
from xml.sax.saxutils import quoteattr

NS_CORE = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
NS_P = 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
NS_BAMBU = 'http://schemas.bambulab.com/package/2021'

DEBUG = os.environ.get("LOG_LEVEL", "INFO").upper() == "DEBUG"

BAMBU_FILAMENT_PROFILES = {
    1: {
        "name": "Voolt3D PETG Premium - Marrom",
        "type": "PETG",
        "color": "#804000",
        "vendor": "Voolt3D",
        "filament_id": "P2ea0049",
        "density": "1.27",
        "diameter": "1.75",
        "max_volumetric_speed": "10",
        "flow_ratio": "1",
        "nozzle_temperature": "235",
        "nozzle_temperature_initial_layer": "235",
        "cool_plate_temp": "60",
        "cool_plate_temp_initial_layer": "60",
        "hot_plate_temp": "70",
        "hot_plate_temp_initial_layer": "70",
        "textured_plate_temp": "70",
        "textured_plate_temp_initial_layer": "70",
    },
    2: {
        "name": "Voolt3D PETG Premium - White",
        "type": "PETG",
        "color": "#FFFFFF",
        "vendor": "Generic",
        "filament_id": "GFG99",
        "density": "1.27",
        "diameter": "1.75",
        "max_volumetric_speed": "10",
        "flow_ratio": "1",
        "nozzle_temperature": "235",
        "nozzle_temperature_initial_layer": "235",
        "cool_plate_temp": "60",
        "cool_plate_temp_initial_layer": "60",
        "hot_plate_temp": "70",
        "hot_plate_temp_initial_layer": "70",
        "textured_plate_temp": "70",
        "textured_plate_temp_initial_layer": "70",
    },
}

def log(msg):
    if DEBUG:
        print(f"[3MF] {msg}")


def xml_attr(value):
    """Return a safely quoted XML attribute value."""
    return quoteattr(str(value))


def get_mesh_data(obj):
    """Extrai dados de malha com transformação mundial"""
    import bpy
    import bmesh
    
    log(f"Extraindo: {obj.name}")
    
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()
    
    if mesh is None:
        return [], []
    
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    # Aplica transformação
    bmesh.ops.transform(bm, matrix=obj.matrix_world, verts=bm.verts)
    
    # Triangula
    bmesh.ops.triangulate(bm, faces=bm.faces)
    
    vertices = [(v.co.x, v.co.y, v.co.z) for v in bm.verts]
    triangles = [(f.verts[0].index, f.verts[1].index, f.verts[2].index) for f in bm.faces]
    
    bm.free()
    obj_eval.to_mesh_clear()
    
    log(f"  -> {len(vertices)} verts, {len(triangles)} tris")
    return vertices, triangles


def build_combined_objects_model(objects_data):
    """Gera um arquivo de modelo com TODOS os objetos (formato Bambu)"""
    log("Gerando modelo combinado...")
    
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<model unit="millimeter" xml:lang="en-US" xmlns="{NS_CORE}" xmlns:BambuStudio="{NS_BAMBU}" xmlns:p="{NS_P}" requiredextensions="p">',
        ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
        ' <resources>',
    ]
    
    for obj_data in objects_data:
        obj_id = obj_data['id']
        obj_uuid = obj_data['uuid']
        vertices = obj_data['vertices']
        triangles = obj_data['triangles']
        
        lines.append(f'  <object id="{obj_id}" p:UUID="{obj_uuid}" type="model">')
        lines.append('   <mesh>')
        lines.append('    <vertices>')
        
        for v in vertices:
            lines.append(f'     <vertex x="{v[0]}" y="{v[1]}" z="{v[2]}"/>')
        
        lines.append('    </vertices>')
        lines.append('    <triangles>')
        
        for t in triangles:
            lines.append(f'     <triangle v1="{t[0]}" v2="{t[1]}" v3="{t[2]}"/>')
        
        lines.append('    </triangles>')
        lines.append('   </mesh>')
        lines.append('  </object>')
    
    lines.extend([
        ' </resources>',
        '</model>'
    ])
    
    return '\n'.join(lines)


def build_main_model(objects_data):
    """Gera 3dmodel.model principal com componentes"""
    assembly_id = 60  # ID típico do Bambu
    assembly_uuid = str(uuid.uuid4())
    build_uuid = str(uuid.uuid4())
    item_uuid = str(uuid.uuid4())
    
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<model unit="millimeter" xml:lang="en-US" xmlns="{NS_CORE}" xmlns:BambuStudio="{NS_BAMBU}" xmlns:p="{NS_P}" requiredextensions="p">',
        ' <metadata name="Application">PlateGenerator-1.0</metadata>',
        ' <metadata name="BambuStudio:3mfVersion">1</metadata>',
        f' <metadata name="CreationDate">{datetime.datetime.now().strftime("%Y-%m-%d")}</metadata>',
        ' <metadata name="Title">Placa Astro</metadata>',
        ' <resources>',
        f'  <object id="{assembly_id}" p:UUID="{assembly_uuid}" type="model">',
        '   <components>',
    ]
    
    for obj_data in objects_data:
        lines.append(f'    <component p:path="/3D/Objects/objects.model" objectid="{obj_data["id"]}" p:UUID="{obj_data["comp_uuid"]}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>')
    
    lines.extend([
        '   </components>',
        '  </object>',
        ' </resources>',
        f' <build p:UUID="{build_uuid}">',
        f'  <item objectid="{assembly_id}" p:UUID="{item_uuid}" transform="1 0 0 0 1 0 0 0 1 100 90 0" printable="1"/>',
        ' </build>',
        '</model>'
    ])
    
    return '\n'.join(lines), assembly_id


def build_model_settings(objects_data, assembly_id):
    """Gera model_settings.config"""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<config>',
        f'  <object id="{assembly_id}">',
        f'    <metadata key="name" value="Placa_Astro"/>',
        f'    <metadata key="extruder" value="1"/>',
    ]
    
    for obj_data in objects_data:
        lines.extend([
            f'    <part id="{obj_data["id"]}" subtype="normal_part">',
            f'      <metadata key="name" value={xml_attr(obj_data["name"])}/>',
            f'      <metadata key="extruder" value="{obj_data["extruder"]}"/>',
            f'      <mesh_stat face_count="{obj_data["face_count"]}"/>',
            '    </part>',
        ])
    
    lines.extend([
        '  </object>',
        '  <plate>',
        '    <metadata key="plater_id" value="1"/>',
        '  </plate>',
        '</config>'
    ])
    
    return '\n'.join(lines)


def build_content_types():
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
</Types>'''


def build_rels():
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>'''


def build_model_rels(objects_file):
    """Gera _rels para o modelo principal"""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/Objects/{objects_file}" Id="rel1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>'''


def build_project_settings():
    """Gera a configuração de projeto esperada pelo Bambu Studio atual.

    Perfis de filamento são propriedades do projeto, não arquivos de perfil
    independentes. Essa estrutura segue um 3MF salvo pelo Bambu Studio para a
    A1 com bico de 0,4 mm e mantém as identificações dos materiais Voolt.
    """
    profiles = [BAMBU_FILAMENT_PROFILES[index] for index in sorted(BAMBU_FILAMENT_PROFILES)]

    def values(key):
        return [profile[key] for profile in profiles]

    return json.dumps({
        "from": "project",
        "name": "project_settings",
        "version": "02.08.02.61",
        "printer_model": "Bambu Lab A1",
        "printer_settings_id": "Bambu Lab A1 0.4 nozzle",
        "printer_technology": "FFF",
        "printer_variant": "0.4",
        "nozzle_diameter": ["0.4"],
        "curr_bed_type": "Cool Plate",
        "default_print_profile": "0.20mm Standard @BBL A1",
        "print_settings_id": "0.12mm - PETG Placas",
        "default_filament_profile": values("name"),
        "default_filament_colour": values("color"),
        "filament_colour": values("color"),
        "filament_ids": values("filament_id"),
        "filament_settings_id": values("name"),
        "filament_type": values("type"),
        "filament_vendor": values("vendor"),
        "filament_density": values("density"),
        "filament_diameter": values("diameter"),
        "filament_flow_ratio": values("flow_ratio"),
        "filament_max_volumetric_speed": values("max_volumetric_speed"),
        "nozzle_temperature": values("nozzle_temperature"),
        "nozzle_temperature_initial_layer": values("nozzle_temperature_initial_layer"),
        "cool_plate_temp": values("cool_plate_temp"),
        "cool_plate_temp_initial_layer": values("cool_plate_temp_initial_layer"),
        "hot_plate_temp": values("hot_plate_temp"),
        "hot_plate_temp_initial_layer": values("hot_plate_temp_initial_layer"),
        "textured_plate_temp": values("textured_plate_temp"),
        "textured_plate_temp_initial_layer": values("textured_plate_temp_initial_layer"),
        "filament_printable": ["3", "3"],
        "filament_is_support": ["0", "0"],
        "filament_map": ["1", "1"],
        "filament_map_mode": "Auto For Flush",
        "filament_volume_map": ["0", "0"],
        "filament_self_index": ["1", "2"],
        "filament_extruder_compatibility": ["0", "0"],
        "flush_volumes_matrix": ["0", "596", "243", "0"],
        "flush_volumes_vector": ["140", "140", "140", "140"],
        "enable_prime_tower": "1",
        "different_settings_to_system": [
            "filament_colour",
            "filament_ids",
            "filament_settings_id",
            "filament_vendor",
            "filament_type",
            "nozzle_temperature",
        ],
    }, indent=4)


def export(filepath, objects):
    """Exporta para 3MF no formato Bambu"""
    log("=== EXPORTAÇÃO 3MF ===")
    
    # Prepara dados
    objects_data = []
    for i, obj_info in enumerate(objects):
        vertices, triangles = get_mesh_data(obj_info['obj'])
        if not vertices:
            continue
            
        objects_data.append({
            'id': i + 1,
            'uuid': str(uuid.uuid4()),
            'comp_uuid': str(uuid.uuid4()),
            'name': obj_info['name'],
            'extruder': obj_info['extruder'],
            'vertices': vertices,
            'triangles': triangles,
            'face_count': len(triangles)
        })
    
    if not objects_data:
        log("ERRO: Sem objetos!")
        return None
    
    log(f"Objetos: {len(objects_data)}")
    
    # Cria ZIP
    with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', build_content_types())
        zf.writestr('_rels/.rels', build_rels())
        
        # Modelo principal
        main_model, assembly_id = build_main_model(objects_data)
        zf.writestr('3D/3dmodel.model', main_model)
        
        # Relacionamentos do modelo
        zf.writestr('3D/_rels/3dmodel.model.rels', build_model_rels('objects.model'))
        
        # Arquivo com todos os objetos
        combined = build_combined_objects_model(objects_data)
        zf.writestr('3D/Objects/objects.model', combined)
        
        # Metadata
        zf.writestr('Metadata/model_settings.config', build_model_settings(objects_data, assembly_id))
        zf.writestr('Metadata/project_settings.config', build_project_settings())
    
    log(f"Arquivo: {os.path.getsize(filepath)} bytes")
    log("=== CONCLUÍDO ===")
    return filepath
