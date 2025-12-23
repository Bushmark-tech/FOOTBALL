# PowerShell script to fix Python environment for model testing

Write-Host "=" * 70
Write-Host "FIXING PYTHON ENVIRONMENT"
Write-Host "=" * 70

Write-Host "`nStep 1: Uninstalling corrupted packages..."
pip uninstall numpy pandas scikit-learn joblib -y

Write-Host "`nStep 2: Clearing pip cache..."
pip cache purge

Write-Host "`nStep 3: Reinstalling packages..."
pip install numpy==1.25.2 pandas==2.0.3 scikit-learn==1.6.1 joblib

Write-Host "`nStep 4: Verifying installation..."
python -c "import numpy; import pandas; import sklearn; import joblib; print('✓ All packages imported successfully')"

Write-Host "`nStep 5: Clearing Python cache..."
Get-ChildItem -Path . -Include __pycache__,*.pyc -Recurse -Force | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
Write-Host "✓ Python cache cleared"

Write-Host "`n" + "=" * 70
Write-Host "Environment fix complete! You can now test the model."
Write-Host "=" * 70



