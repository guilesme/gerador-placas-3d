"""Service helpers for invoking Blender plate generation."""

import os
import subprocess
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent.parent
GENERATOR_SCRIPT = Path(__file__).parent.parent / "blender" / "generator.py"
OUTPUT_DIR = BASE_DIR / "output"

if not GENERATOR_SCRIPT.exists():
    GENERATOR_SCRIPT = Path("src/blender/generator.py")
    OUTPUT_DIR = Path("output")


def get_blender_bin():
    """Return the configured Blender executable path."""
    return os.environ.get("BLENDER_PATH", "blender")


def ensure_output_dir():
    """Create the output directory if needed."""
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


def generate_plate(text, font_size, align="CENTER", plate_height=180, footer_text="Condominio Astro"):
    """Run Blender in background mode and return (success, filepath, message)."""
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"placa_astro_{timestamp}.3mf"
    output_path = OUTPUT_DIR / filename
    blender_bin = get_blender_bin()

    cmd = [
        blender_bin,
        "--background",
        "--python", str(GENERATOR_SCRIPT),
        "--",
        text,
        str(output_path),
        str(font_size),
        align,
        str(plate_height),
        footer_text,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            return False, None, result.stderr + "\n" + result.stdout

        if not output_path.exists() or output_path.stat().st_size < 1000:
            return False, None, "Arquivo de saida invalido ou vazio"

        return True, output_path, "Sucesso"

    except subprocess.TimeoutExpired:
        return False, None, "Tempo limite atingido (120s). Tente um texto mais curto ou gere novamente."
    except FileNotFoundError:
        return False, None, (
            f"Executavel do Blender nao encontrado: {blender_bin}. "
            "Verifique se o container Docker foi construido corretamente e se BLENDER_PATH esta definido no container."
        )
    except OSError as e:
        return False, None, f"Erro de sistema ao executar o Blender: {e}"
    except Exception as e:
        return False, None, f"Erro inesperado: {type(e).__name__}: {e}"
