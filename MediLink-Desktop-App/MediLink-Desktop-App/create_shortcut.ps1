$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.IO.Path]::Combine([System.Environment]::GetFolderPath('Desktop'), 'MediLink.lnk')
$TargetFolder = $PSScriptRoot

try {
    # Locate python.exe from PATH
    $PythonExe = (Get-Command python.exe -ErrorAction Stop).Source
    $PythonwExe = $PythonExe -replace 'python.exe', 'pythonw.exe'

    if (-not (Test-Path $PythonwExe)) {
        $PythonwExe = $PythonExe
    }

    # Create the shortcut
    $Shortcut = $WshShell.CreateShortcut($DesktopPath)
    $Shortcut.TargetPath = $PythonwExe
    $Shortcut.Arguments = "`"$TargetFolder\desktop_app.py`""
    $Shortcut.WorkingDirectory = $TargetFolder
    $Shortcut.IconLocation = "$TargetFolder\app_icon.ico"
    $Shortcut.Save()
    Write-Host "Shortcut created successfully on Desktop!"
} catch {
    Write-Error "Failed to create shortcut: $_"
    exit 1
}
