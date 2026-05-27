import json
import sys
import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock


ROOT_DIR = Path(__file__).resolve().parents[1]
BLENDER_DIR = ROOT_DIR / "src" / "blender"
sys.path.insert(0, str(BLENDER_DIR))

import threemf_exporter


def sample_objects_data():
    return [
        {
            "id": 1,
            "uuid": "aaaaaaaa-0000-0000-0000-000000000001",
            "comp_uuid": "bbbbbbbb-0000-0000-0000-000000000001",
            "name": "Placa",
            "extruder": 1,
            "vertices": [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
            "triangles": [(0, 1, 2)],
            "face_count": 1,
        },
        {
            "id": 2,
            "uuid": "aaaaaaaa-0000-0000-0000-000000000002",
            "comp_uuid": "bbbbbbbb-0000-0000-0000-000000000002",
            "name": "Texto",
            "extruder": 2,
            "vertices": [(0.0, 0.0, 2.0), (0.5, 0.0, 2.0), (0.0, 0.5, 2.0)],
            "triangles": [(0, 1, 2)],
            "face_count": 1,
        },
    ]


class ThreeMfExporterTests(unittest.TestCase):
    def test_combined_model_is_parseable_xml(self):
        xml_text = threemf_exporter.build_combined_objects_model(sample_objects_data())

        root = ET.fromstring(xml_text)

        self.assertTrue(root.tag.endswith("model"))

    def test_main_model_is_parseable_xml(self):
        xml_text, assembly_id = threemf_exporter.build_main_model(sample_objects_data())

        root = ET.fromstring(xml_text)

        self.assertEqual(assembly_id, 60)
        self.assertTrue(root.tag.endswith("model"))

    def test_model_settings_contains_extruder_metadata(self):
        xml_text = threemf_exporter.build_model_settings(sample_objects_data(), assembly_id=60)

        root = ET.fromstring(xml_text)

        self.assertEqual(root.tag, "config")
        self.assertIn('key="extruder"', xml_text)
        self.assertIn('value="1"', xml_text)
        self.assertIn('value="2"', xml_text)

    def test_model_settings_escapes_xml_attribute_values(self):
        data = sample_objects_data()
        data[1]["name"] = 'Texto <Especial> & "Teste"'

        xml_text = threemf_exporter.build_model_settings(data, assembly_id=60)
        root = ET.fromstring(xml_text)

        metadata_values = [
            node.attrib["value"]
            for node in root.findall(".//metadata")
            if node.attrib.get("key") == "name"
        ]
        self.assertIn('Texto <Especial> & "Teste"', metadata_values)

    def test_filament_settings_are_valid_json(self):
        data = json.loads(threemf_exporter.build_filament_settings(1))

        self.assertEqual(data["name"], "Voolt3D PETG Premium - Marrom")
        self.assertEqual(data["from"], "project")
        self.assertEqual(data["filament_type"], ["PETG"])
        self.assertEqual(data["filament_settings_id"], ["Voolt3D PETG Premium - Marrom"])
        self.assertEqual(data["default_filament_colour"], ["#804000"])
        self.assertEqual(data["filament_id"], ["P2ea0049"])
        self.assertEqual(data["nozzle_temperature"], ["235"])

    def test_second_filament_profile_uses_white_petg(self):
        data = json.loads(threemf_exporter.build_filament_settings(2))

        self.assertEqual(data["name"], "Voolt3D PETG Premium - White")
        self.assertEqual(data["filament_type"], ["PETG"])
        self.assertEqual(data["filament_settings_id"], ["Voolt3D PETG Premium - White"])
        self.assertEqual(data["default_filament_colour"], ["#FFFFFF"])
        self.assertEqual(data["filament_id"], ["GFG99"])

    def test_export_creates_required_3mf_entries(self):
        objects_data = sample_objects_data()
        mock_objects = [
            {"obj": data, "extruder": data["extruder"], "name": data["name"]}
            for data in objects_data
        ]

        def fake_get_mesh_data(obj):
            return obj["vertices"], obj["triangles"]

        output_dir = ROOT_DIR / "output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "test_unittest_export.3mf"
        if output_path.exists():
            output_path.unlink()

        with mock.patch.object(threemf_exporter, "get_mesh_data", side_effect=fake_get_mesh_data):
            result = threemf_exporter.export(str(output_path), mock_objects)

        self.assertEqual(result, str(output_path))
        self.assertTrue(output_path.exists())

        with zipfile.ZipFile(output_path, "r") as archive:
            entries = set(archive.namelist())
            filament_1 = json.loads(archive.read("Metadata/filament_settings_1.config"))
            filament_2 = json.loads(archive.read("Metadata/filament_settings_2.config"))

        expected_entries = {
            "[Content_Types].xml",
            "_rels/.rels",
            "3D/3dmodel.model",
            "3D/_rels/3dmodel.model.rels",
            "3D/Objects/objects.model",
            "Metadata/model_settings.config",
            "Metadata/filament_settings_1.config",
            "Metadata/filament_settings_2.config",
        }
        self.assertTrue(expected_entries.issubset(entries))
        self.assertEqual(filament_1["filament_settings_id"], ["Voolt3D PETG Premium - Marrom"])
        self.assertEqual(filament_2["filament_settings_id"], ["Voolt3D PETG Premium - White"])


if __name__ == "__main__":
    unittest.main()
