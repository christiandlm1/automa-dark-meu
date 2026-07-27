import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from fastapi.responses import FileResponse
from config import settings
from utils.cache_manager import cache_manager

def clear_cache() -> bool:
    try:
        cache_manager.clear()
        return True
    except Exception as e:
        print(f"Error clearing cache: {e}")
        return False

def backup_database() -> str | None:
    db_path = settings.DATABASE_DIR / "automa.db"
    if not db_path.exists():
        return None
    backup_dir = settings.BASE_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"automa_db_backup_{timestamp}.sqlite"
    try:
        shutil.copy2(db_path, backup_file)
        return str(backup_file)
    except Exception as e:
        print(f"Error backing up db: {e}")
        return None

def generate_diagnostics() -> str | None:
    diagnostics_dir = settings.TEMP_DIR / "diagnostics"
    diagnostics_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = diagnostics_dir / f"automa_diagnostics_{timestamp}.zip"
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add logs
            if settings.LOGS_DIR.exists():
                for root, _, files in os.walk(settings.LOGS_DIR):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.join("logs", file))
            # Add sqlite db
            db_path = settings.DATABASE_DIR / "automa.db"
            if db_path.exists():
                zipf.write(db_path, "automa.db")
        return str(zip_path)
    except Exception as e:
        print(f"Error generating diagnostics: {e}")
        return None
