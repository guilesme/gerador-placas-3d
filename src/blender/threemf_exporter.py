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


def build_filament_settings(extruder, color, name):
    return json.dumps({
        "default_filament_colour": [color],
        "filament_settings_id": [name],
        "from": "project",
        "name": name,
        "version": "2.3.0.70"
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
        zf.writestr('Metadata/filament_settings_1.config', build_filament_settings(1, "#8B4513", "PLA Brown"))
        zf.writestr('Metadata/filament_settings_2.config', build_filament_settings(2, "#FFFFFF", "PLA White"))
    
    log(f"Arquivo: {os.path.getsize(filepath)} bytes")
    log("=== CONCLUÍDO ===")
    return filepath
