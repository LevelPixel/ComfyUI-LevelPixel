@echo off
setlocal

echo Please close the ComfyUI console before continuing.
set /p user_input=Did you close the ComfyUI console? (Y/n): 

if /I "%user_input%"=="Y" (
    echo Uninstalling onnxruntime...

    cd ..\..\..\..
    .\python_embeded\python.exe -m pip uninstall -y onnxruntime
    .\python_embeded\python.exe -m pip uninstall -y onnxruntime-gpu

    rmdir /s /q "python_embeded\Lib\site-packages\onnxruntime"
    for /d %%D in ("python_embeded\Lib\site-packages\onnxruntime-*") do rmdir /s /q "%%~fD"
) else (
    echo Please close the ComfyUI console first and run this script again.
)

endlocal
pause