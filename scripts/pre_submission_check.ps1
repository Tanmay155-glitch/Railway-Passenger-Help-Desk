# Pre-Submission Checklist Script
# Run this before committing final code to ensure compliance

$separator = "======================================================================"
$dashes = "----------------------------------------------------------------------"

Write-Host $separator
Write-Host "PRE-SUBMISSION COMPLIANCE CHECK"
Write-Host "Railway Passenger Help Desk - GenAI Nexus Capstone"
Write-Host $separator
Write-Host ""

$AllPassed = $true

function Test-Requirement {
    param(
        [string]$Name,
        [scriptblock]$Check
    )
    
    Write-Host "Checking: $Name..." -NoNewline
    try {
        $result = & $Check
        if ($result) {
            Write-Host " PASS" -ForegroundColor Green
            return $true
        } else {
            Write-Host " FAIL" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host " ERROR: $_" -ForegroundColor Red
        return $false
    }
}

Write-Host "SECTION 1: File Structure" -ForegroundColor Cyan
Write-Host $dashes

$AllPassed = (Test-Requirement "README.md exists" { Test-Path "README.md" }) -and $AllPassed
$AllPassed = (Test-Requirement "requirements.txt exists" { Test-Path "requirements.txt" }) -and $AllPassed
$AllPassed = (Test-Requirement ".env.example exists" { Test-Path ".env.example" }) -and $AllPassed
$AllPassed = (Test-Requirement ".gitignore exists" { Test-Path ".gitignore" }) -and $AllPassed
$AllPassed = (Test-Requirement "helpdesk/pipeline.py exists" { Test-Path "helpdesk/pipeline.py" }) -and $AllPassed
$AllPassed = (Test-Requirement "build_index.py exists" { Test-Path "build_index.py" }) -and $AllPassed
$AllPassed = (Test-Requirement "ask.py exists" { Test-Path "ask.py" }) -and $AllPassed
$AllPassed = (Test-Requirement "run_questions.py exists" { Test-Path "run_questions.py" }) -and $AllPassed
$AllPassed = (Test-Requirement "eval/test_set.json exists" { Test-Path "eval/test_set.json" }) -and $AllPassed
$AllPassed = (Test-Requirement "eval/evaluate.py exists" { Test-Path "eval/evaluate.py" }) -and $AllPassed

Write-Host ""
Write-Host "SECTION 2: Forbidden Items" -ForegroundColor Cyan
Write-Host $dashes

$AllPassed = (Test-Requirement "No Flask web UI (app.py)" { -not (Test-Path "app.py") }) -and $AllPassed
$AllPassed = (Test-Requirement "No templates directory" { -not (Test-Path "templates") }) -and $AllPassed
$AllPassed = (Test-Requirement "No .env file committed" { -not (git ls-files ".env") }) -and $AllPassed

Write-Host ""
Write-Host "SECTION 3: Index Files" -ForegroundColor Cyan
Write-Host $dashes

$AllPassed = (Test-Requirement "index/chunks.json exists" { Test-Path "index/chunks.json" }) -and $AllPassed
$AllPassed = (Test-Requirement "index/schema.txt exists" { Test-Path "index/schema.txt" }) -and $AllPassed
$AllPassed = (Test-Requirement "index/bm25.pkl exists" { Test-Path "index/bm25.pkl" }) -and $AllPassed
$AllPassed = (Test-Requirement "index/manifest.json exists" { Test-Path "index/manifest.json" }) -and $AllPassed

Write-Host ""
Write-Host "SECTION 4: Tests" -ForegroundColor Cyan
Write-Host $dashes

$AllPassed = (Test-Requirement "tests/test_contract.py exists" { Test-Path "tests/test_contract.py" }) -and $AllPassed
$AllPassed = (Test-Requirement "tests/test_sql_guard.py exists" { Test-Path "tests/test_sql_guard.py" }) -and $AllPassed
$AllPassed = (Test-Requirement "tests/test_chunking.py exists" { Test-Path "tests/test_chunking.py" }) -and $AllPassed
$AllPassed = (Test-Requirement "tests/test_sources.py exists" { Test-Path "tests/test_sources.py" }) -and $AllPassed
$AllPassed = (Test-Requirement "tests/test_entity_extraction.py exists" { Test-Path "tests/test_entity_extraction.py" }) -and $AllPassed

Write-Host ""
Write-Host "SECTION 5: API Key Safety" -ForegroundColor Cyan
Write-Host $dashes

$AllPassed = (Test-Requirement "No API keys in committed files" {
    $keys = git grep -E "AIza[0-9A-Za-z-_]{35}" 2>$null
    $null -eq $keys
}) -and $AllPassed

Write-Host ""
Write-Host "SECTION 6: Code Quality" -ForegroundColor Cyan
Write-Host $dashes

$AllPassed = (Test-Requirement "All Python files have docstrings" {
    $missingDocs = Get-ChildItem helpdesk/*.py | Where-Object {
        $content = Get-Content $_.FullName -Raw
        -not ($content -match '"""' -or $content -match "'''")
    }
    ($null -eq $missingDocs) -or ($missingDocs.Count -eq 0)
}) -and $AllPassed

Write-Host ""
Write-Host "SECTION 7: Evaluation Files" -ForegroundColor Cyan
Write-Host $dashes

$AllPassed = (Test-Requirement "eval/experiments.md exists" { Test-Path "eval/experiments.md" }) -and $AllPassed

$AllPassed = (Test-Requirement "Test set has 10+ questions" {
    if (Test-Path "eval/test_set.json") {
        $testSet = Get-Content "eval/test_set.json" | ConvertFrom-Json
        $testSet.Count -ge 10
    } else {
        $false
    }
}) -and $AllPassed

Write-Host ""
Write-Host "SECTION 8: Contract Compliance" -ForegroundColor Cyan
Write-Host $dashes

Write-Host "Checking: Output contract compliance..." -NoNewline
Write-Host " SKIP (requires manual venv activation)" -ForegroundColor Yellow
# This check requires the virtual environment to be activated
# Run manually: python -c "from helpdesk.pipeline import ask; result = ask('test'); print(result.keys())"

Write-Host ""
Write-Host "SECTION 9: Git Status" -ForegroundColor Cyan
Write-Host $dashes

$AllPassed = (Test-Requirement "On main/master branch" {
    $branch = git branch --show-current
    ($branch -eq "main") -or ($branch -eq "master")
}) -and $AllPassed

Write-Host ""
Write-Host $separator
if ($AllPassed) {
    Write-Host "ALL CHECKS PASSED - Ready for submission!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Final steps before deadline:" -ForegroundColor Yellow
    Write-Host "1. Run: pytest tests/ -v" -ForegroundColor Yellow
    Write-Host "2. Run: python run_questions.py eval/test_set.json eval/results.json" -ForegroundColor Yellow
    Write-Host "3. Review eval/results.json" -ForegroundColor Yellow
    Write-Host "4. Push to GitHub" -ForegroundColor Yellow
    Write-Host "5. Submit repo link on LMS" -ForegroundColor Yellow
} else {
    Write-Host "SOME CHECKS FAILED - Fix issues before submission!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Review the failures above and fix them." -ForegroundColor Yellow
}
Write-Host $separator
Write-Host ""

if ($AllPassed) {
    exit 0
} else {
    exit 1
}
