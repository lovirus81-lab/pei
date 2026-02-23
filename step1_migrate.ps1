$ErrorActionPreference = "Continue"

# 1. Archive
New-Item -ItemType Directory -Force -Path docs/antigravity-archive | Out-Null
if (Test-Path .agent) { Move-Item -Path .agent -Destination docs/antigravity-archive/agent -Force }
if (Test-Path .context) { Move-Item -Path .context -Destination docs/antigravity-archive/context -Force }

# 2. Cleanup
New-Item -ItemType Directory -Force -Path scripts/test_scripts | Out-Null
$pyFiles = @("test_offsets.py", "test_repair.py", "test_validate.py", "verify_layout.py", "clean_db.py", "mock_output.py")
foreach ($file in $pyFiles) {
    if (Test-Path "backend/$file") { Move-Item -Path "backend/$file" -Destination "scripts/test_scripts/" -Force }
}

Remove-Item -Path backend/*.txt, backend/*.log, backend/*.json -Force -ErrorAction SilentlyContinue
Remove-Item -Path backend_output.txt, Makefile.txt, tree.txt, log.txt, *.txt -Force -ErrorAction SilentlyContinue

# 3. Monorepo structure
New-Item -ItemType Directory -Force -Path apps | Out-Null
if (Test-Path frontend) { Rename-Item -Path frontend -NewName web ; Move-Item -Path web -Destination apps/ -Force }
if (Test-Path backend) { Rename-Item -Path backend -NewName api ; Move-Item -Path api -Destination apps/ -Force }

Write-Host "Cleanup and move done."
