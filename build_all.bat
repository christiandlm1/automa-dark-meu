@echo off
echo Building AUTOMA...
cd backend
echo Building Backend...
python build_backend.py
cd ..
cd frontend
echo Building Frontend...
call npm install
call npm run build
cd ..
echo Launching InnoSetup Compiler...
iscc installer\automa.iss
echo Build Complete!
