# Setup Verification Script
# Run this to check if your environment is ready

Write-Host "`n=== Railway Help Desk - Setup Verification ===" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check 1: Python
Write-Host "1. Checking Python..." -NoNewline
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(1[0-9]|[0-9]{2})") {
        Write-Host " ✓ $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host " ✗ Python 3.10+ required" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host " ✗ Python not found" -ForegroundColor Red
    $allGood = $false
}

# Check 2: Virtual Environment
Write-Host "2. Checking virtual environment..." -NoNewline
if (Test-Path ".venv") {
    Write-Host " ✓ .venv exists" -ForegroundColor Green
} else {
    Write-Host " ✗ .venv not created" -ForegroundColor Yellow
    Write-Host "   Run: python -m venv .venv" -ForegroundColor Yellow
}

# Check 3: .env file
Write-Host "3. Checking .env file..." -NoNewline
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "GEMINI_API_KEY=AIza") {
        Write-Host " ✓ API key configured" -ForegroundColor Green
    } elseif ($envContent -match "your_key_here") {
        Write-Host " ✗ API key not set" -ForegroundColor Yellow
        $allGood = $false
    } else {
        Write-Host " ✓ .env exists" -ForegroundColor Green
    }
} else {
    Write-Host " ✗ .env file missing" -ForegroundColor Red
    $allGood = $false
}

# Check 4: Data directory
Write-Host "4. Checking data directory..." -NoNewline
if (Test-Path "data") {
    $docCount = (Get-ChildItem "data\documents" -File -ErrorAction SilentlyContinue | Measure-Object).Count
    $dbExists = Test-Path "data\database\rail_timetable.db"
    
    if ($docCount -ge 7 -and $dbExists) {
        Write-Host " ✓ $docCount documents, database found" -ForegroundColor Green
    } else {
        Write-Host " ✗ Incomplete ($docCount docs, db: $dbExists)" -ForegroundColor Red
        $allGood = $false
    }
} else {
    Write-Host " ✗ data directory not found" -ForegroundColor Red
    $allGood = $false
}

# Check 5: Source files
Write-Host "5. Checking source files..." -NoNewline
$helpdeskFiles = @(
    "helpdesk\config.py",
    "helpdesk\llm.py",
    "helpdesk\ingest.py",
    "helpdesk\search.py",
    "helpdesk\sql.py",
    "helpdesk\sql_guard.py",
    "helpdesk\stations.py",
    "helpdesk\answer.py",
    "helpdesk\router.py",
    "helpdesk\pipeline.py",
    "helpdesk\doc_meta.py",
    "helpdesk\entities.py"
)

$missingFiles = $helpdeskFiles | Where-Object { -not (Test-Path $_) }
if ($missingFiles.Count -eq 0) {
    Write-Host " ✓ All 12 modules present" -ForegroundColor Green
} else {
    Write-Host " ✗ Missing $($missingFiles.Count) modules" -ForegroundColor Red
    $allGood = $false
}

# Check 6: Test files
Write-Host "6. Checking test files..." -NoNewline
$testFiles = @(
    "tests\test_contract.py",
    "tests\test_entity_extraction.py",
    "tests\test_sql_guard.py",
    "tests\test_chunking.py",
    "tests\test_sources.py",
    "tests\test_station_resolution.py"
)

$missingTests = $testFiles | Where-Object { -not (Test-Path $_) }
if ($missingTests.Count -eq 0) {
    Write-Host " ✓ All 6 test files present" -ForegroundColor Green
} else {
    Write-Host " ✗ Missing $($missingTests.Count) test files" -ForegroundColor Red
    $allGood = $false
}

# Check 7: Scripts
Write-Host "7. Checking scripts..." -NoNewline
$scripts = @("build_index.py", "ask.py", "run_questions.py")
$missingScripts = $scripts | Where-Object { -not (Test-Path $_) }
if ($missingScripts.Count -eq 0) {
    Write-Host " ✓ All scripts present" -ForegroundColor Green
} else {
    Write-Host " ✗ Missing scripts" -ForegroundColor Red
    $allGood = $false
}

# Check 8: Eval files
Write-Host "8. Checking eval files..." -NoNewline
if ((Test-Path "eval\test_set.json") -and (Test-Path "eval\evaluate.py") -and (Test-Path "eval\experiments.md")) {
    $questionCount = (Get-Content "eval\test_set.json" | ConvertFrom-Json).Count
    Write-Host " ✓ Eval suite ready ($questionCount questions)" -ForegroundColor Green
} else {
    Write-Host " ✗ Eval files incomplete" -ForegroundColor Red
    $allGood = $false
}

# Check 9: Index built
Write-Host "9. Checking index..." -NoNewline
if (Test-Path "index") {
    $indexFiles = Get-ChildItem "index" -File | Measure-Object
    if ($indexFiles.Count -ge 3) {
        Write-Host " ✓ Index built ($($indexFiles.Count) files)" -ForegroundColor Green
    } else {
        Write-Host " ✗ Index not built" -ForegroundColor Yellow
        Write-Host "   Run: python build_index.py" -ForegroundColor Yellow
    }
} else {
    Write-Host " ✗ Index directory missing" -ForegroundColor Yellow
}

# Check 10: Git status
Write-Host "10. Checking git status..." -NoNewline
if (Test-Path ".git") {
    $gitStatus = git status --porcelain 2>&1
    if ($gitStatus -match ".env") {
        Write-Host " ✗ .env file tracked in git!" -ForegroundColor Red
        $allGood = $false
    } else {
        Write-Host " ✓ Git repo clean" -ForegroundColor Green
    }
} else {
    Write-Host " ✗ Not a git repo" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan

if ($allGood) {
    Write-Host "✓ Setup is READY! You can proceed with testing." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Activate venv: .venv\Scripts\activate"
    Write-Host "  2. Build index: python build_index.py"
    Write-Host "  3. Test: python ask.py 'What is the Tatkal charge?'"
} else {
    Write-Host "✗ Setup is INCOMPLETE. Fix the issues above." -ForegroundColor Red
    Write-Host ""
    Write-Host "See SETUP_GUIDE.md for detailed instructions." -ForegroundColor Yellow
}

Write-Host ""
