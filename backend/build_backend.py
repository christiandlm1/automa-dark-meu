import subprocess
import os

def build():
    print("Building AUTOMA Backend with PyInstaller...")
    # Add data files that are needed
    command = [
        "pyinstaller",
        "--name=automa-backend",
        "--onefile",
        "--hidden-import=aiosqlite",
        "--hidden-import=sqlalchemy.ext.asyncio",
        "--hidden-import=moviepy",
        "--hidden-import=uvicorn",
        "--hidden-import=fastapi",
        "--hidden-import=pydantic",
        "main.py"
    ]
    subprocess.run(command, check=True)
    print("Backend build complete.")

if __name__ == "__main__":
    build()
