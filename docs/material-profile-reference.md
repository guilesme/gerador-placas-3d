# Referencia de Materiais e Perfil Bambu

Baseado nos arquivos validados pelo usuario:

- `C:\Users\bigus\Documents\Projetos 3D\Condominio Astro\Utilização da Churrasqueira.3mf`
- `C:\Users\bigus\Documents\Projetos 3D\Condominio Astro\Placa_Astro_PETG_4h36m.gcode`

Objetivo: servir como referencia para a `IMP-003`, que padroniza filamentos, cores e vinculo do texto ao segundo material no Bambu Studio.

## Observacao Manual

O `.3mf` gerado pela aplicacao abriu corretamente no Bambu Studio, mas o usuario precisou:

- adicionar uma segunda cor/filamento;
- vincular manualmente o objeto `Text` ao segundo filamento.

O objetivo futuro e eliminar esse ajuste manual.

## Estrutura 3MF Validada

O arquivo `.3mf` de referencia possui:

```text
[Content_Types].xml
_rels/.rels
3D/3dmodel.model
3D/_rels/3dmodel.model.rels
3D/Objects/objects.model
Metadata/model_settings.config
Metadata/filament_settings_1.config
Metadata/filament_settings_2.config
```

Trecho relevante de `Metadata/model_settings.config`:

```xml
<part id="1" subtype="normal_part">
  <metadata key="name" value="Placa"/>
  <metadata key="extruder" value="1"/>
</part>
<part id="2" subtype="normal_part">
  <metadata key="name" value="Texto"/>
  <metadata key="extruder" value="2"/>
</part>
```

Isso indica que a separacao `Placa -> extruder 1` e `Texto -> extruder 2` ja esta presente no `.3mf` de referencia.

## Diferenca Principal Identificada

Os `filament_settings_*.config` do `.3mf` de referencia atual ainda usam nomes genericos:

```json
{
  "name": "PLA Brown",
  "default_filament_colour": ["#8B4513"]
}
```

```json
{
  "name": "PLA White",
  "default_filament_colour": ["#FFFFFF"]
}
```

Ja o G-code final validado aponta para o perfil real usado no Bambu Studio:

```text
filament_type = PETG;PETG
filament_settings_id = "Voolt3D PETG Premium - Marrom";"Voolt3D PETG Premium - White"
filament_colour = #804000;#FFFFFF
default_filament_colour = #804000;#FFFFFF
filament_vendor = Voolt3D;Generic
filament_ids = P2ea0049;GFG99
filament_density = 1.27,1.27
filament_diameter = 1.75,1.75
filament_max_volumetric_speed = 10,10
filament_flow_ratio = 1,1
```

## Parametros de Impressao Relevantes

Do G-code validado:

```text
BambuStudio = 02.07.00.55
default_print_profile = 0.20mm Standard @BBL A1
curr_bed_type = Cool Plate
total layer number = 19
max_z_height = 2.36
filament = 1,2
model printing time = 4h 28m 47s
total estimated time = 4h 35m 47s
```

Temperaturas:

```text
nozzle_temperature = 235,235
nozzle_temperature_initial_layer = 235,235
nozzle_temperature_range_low = 225,225
nozzle_temperature_range_high = 245,245
cool_plate_temp = 60,60
cool_plate_temp_initial_layer = 60,60
hot_plate_temp = 70,70
hot_plate_temp_initial_layer = 70,70
textured_plate_temp = 70,70
textured_plate_temp_initial_layer = 70,70
```

Troca de material / prime tower:

```text
enable_prime_tower = 1
prime_tower_width = 35
prime_tower_brim_width = 3
prime_tower_infill_gap = 100%
flush_volumes_matrix = 0,596,243,0
flush_volumes_vector = 140,140,140,140
```

Consumo estimado:

```text
total filament length [mm] = 27752.84,1297.10
total filament weight [g] = 84.78,3.96
```

## Implementacao Aplicada

### Fase 1 - Atualizar metadados de filamento do 3MF

`build_filament_settings()` passou a usar os perfis padronizados abaixo:

- material 1:
  - nome: `Voolt3D PETG Premium - Marrom`
  - cor: `#804000`
  - tipo: `PETG`
- material 2:
  - nome: `Voolt3D PETG Premium - White`
  - cor: `#FFFFFF`
  - tipo: `PETG`

### Fase 2 - Melhorar metadados Bambu

Validar manualmente se o `.3mf` precisa incluir metadados extras do projeto Bambu para que a lista de filamentos e o vinculo do objeto `Texto` sejam reconhecidos automaticamente sem ajuste manual.

Pontos a investigar:

- se `Metadata/filament_settings_*.config` precisa espelhar mais campos do G-code;
- se `Metadata/model_settings.config` precisa de metadados adicionais por `part`;
- se ha arquivos extras em `.3mf` salvo pelo Bambu Studio apos ajuste manual.

### Fase 3 - Teste de aceitacao

Um `.3mf` novo gerado pela aplicacao deve:

- abrir no Bambu Studio;
- listar dois filamentos PETG;
- mostrar marrom `#804000` para a base;
- mostrar branco `#FFFFFF` para o texto;
- manter `Texto` vinculado ao segundo material;
- permitir slice sem ajuste manual de cor/material.

