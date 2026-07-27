import json
import zipfile
from pathlib import Path
from datetime import datetime
from config import settings

def export_template_to_file(template_data: dict) -> Path:
    export_dir = settings.EXPORTS_DIR / "templates"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in template_data.get("name", "template"))
    filename = f"{safe_name}_{timestamp}.automa_template"
    file_path = export_dir / filename
    
    with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("template.json", json.dumps(template_data, indent=4))
        
    return file_path

def import_template_from_file(file_path: Path) -> dict:
    if not file_path.exists() or not zipfile.is_zipfile(file_path):
        raise ValueError("Invalid template file")
        
    with zipfile.ZipFile(file_path, 'r') as zipf:
        if "template.json" not in zipf.namelist():
            raise ValueError("No template.json found in package")
            
        with zipf.open("template.json") as f:
            template_data = json.load(f)
            
    return template_data
