# create_shortcuts.ps1
# Crea los 11 accesos directos de Marina Image Tools en el escritorio del usuario.
# Ejecutar con: powershell -ExecutionPolicy Bypass -File .\create_shortcuts.ps1

$ErrorActionPreference = "Stop"
$shell   = New-Object -ComObject WScript.Shell
$desktop = [System.Environment]::GetFolderPath("Desktop")
$root    = $PSScriptRoot

$tools = @(
    @{ Name = "Split Poses";       Bat = "$root\tools\split_poses\split_poses.bat";             Dir = "$root\tools\split_poses" },
    @{ Name = "1 Remove BG";       Bat = "$root\tools\01_remove_bg\remove_bg.bat";              Dir = "$root\tools\01_remove_bg" },
    @{ Name = "2 LoRA Organizer";  Bat = "$root\tools\02_lora_organizer\lora_organizer.bat";    Dir = "$root\tools\02_lora_organizer" },
    @{ Name = "3 Social Resize";   Bat = "$root\tools\03_social_resize\social_resize.bat";      Dir = "$root\tools\03_social_resize" },
    @{ Name = "4 Dup Finder";      Bat = "$root\tools\04_dup_finder\dup_finder.bat";            Dir = "$root\tools\04_dup_finder" },
    @{ Name = "5 Folder Watcher";  Bat = "$root\tools\05_folder_watcher\folder_watcher.bat";   Dir = "$root\tools\05_folder_watcher" },
    @{ Name = "6 Seq to MP4";      Bat = "$root\tools\06_seq_to_mp4\seq_to_mp4.bat";           Dir = "$root\tools\06_seq_to_mp4" },
    @{ Name = "7 Meta Viewer";     Bat = "$root\tools\07_meta_viewer\meta_viewer.bat";          Dir = "$root\tools\07_meta_viewer" },
    @{ Name = "8 Grid Maker";      Bat = "$root\tools\08_grid_maker\grid_maker.bat";            Dir = "$root\tools\08_grid_maker" },
    @{ Name = "9 Frame Extractor"; Bat = "$root\tools\09_frame_extractor\frame_extractor.bat"; Dir = "$root\tools\09_frame_extractor" },
    @{ Name = "10 EXR to PNG";     Bat = "$root\tools\10_exr_to_png\exr_to_png.bat";           Dir = "$root\tools\10_exr_to_png" }
)

Write-Host ""
Write-Host "  Creando accesos directos en el Escritorio..." -ForegroundColor Cyan
Write-Host ""

foreach ($tool in $tools) {
    if (-not (Test-Path $tool.Bat)) {
        Write-Host "  [SKIP] $($tool.Name) — no encontrado" -ForegroundColor Yellow
        continue
    }
    $lnkPath = Join-Path $desktop "$($tool.Name).lnk"
    $lnk = $shell.CreateShortcut($lnkPath)
    $lnk.TargetPath       = $tool.Bat
    $lnk.WorkingDirectory = $tool.Dir
    $lnk.WindowStyle      = 1
    $lnk.Save()
    Write-Host "  OK  $($tool.Name)" -ForegroundColor Green
}

Write-Host ""
Write-Host "  Listo. Iconos creados en el Escritorio." -ForegroundColor Cyan
Write-Host ""
