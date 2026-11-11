# Fresh Clone Test Script for Railway Passenger Help Desk
# Tests that the system works from a clean clone

param(
    [string]$TestDir = "$env:TEMP\rail_helpdesk_test_$(Get-Date -Format 'yyyyMMdd_HHmmss')",
    [string]$RepoUrl = ""  # Leave empty to test local directory
)

Write-Host "=" * 60
Write-Host "Fresh Clone Test - Railway Passenger Help Desk"
Write-Host "=" * 60
Write-Host ""

# Step 1: Create test directory
Write-Host "[1/8] Creating test directory: $TestDir"
New-Item -ItemType Directory -Path $TestDir -Force | Out-Null

try {
    Set-Location $TestDir
    
    # Step 2: Clone or copy repository
    if ($RepoUrl) {
        Write-Host "[2/8] Cloning repository from $RepoUrl"
        git clone $RepoUrl repo
        Set-Location repo
    } else {
        Write-Host "[2/8] Copying local repository"
        $SourceDir = Split-Path -Parent $PSScriptRoot
        Copy-Item -Path $SourceDir -Destination "repo" -Recurse -Force
        Set-Location repo
        
        # Remove data directory to simulate fresh clone
        if (Test-Path "data") {
            Remove-Item "data" -Recurse -Force
        }
        
        # Remove .env to simulate fresh clone
        if (Test-Path ".env") {
            Remove-Item ".env" -Force
        }
    }
    
    # Step 3: Check structure
    Write-Host "[3/8] Verifying repository structure"
    $RequiredFiles = @(
        "helpdesk/pipeline.py",
        "helpdesk/config.py",
        "build_index.py",
        "ask.py",
        "run_questions.py",
        "requirements.txt",
        ".env.example",
        ".gitignore"
    )
    
    $MissingFiles = @()
    foreach ($file in $RequiredFiles) {
        if (-not (Test-Path $file)) {
            $MissingFiles += $file
        }
    }
    
    if ($MissingFiles.Count -gt 0) {
        Write-Host "ERROR: Missing required files:" -ForegroundColor Red
        $MissingFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
        exit 1
    }
    Write-Host "  ✓ All required files present" -ForegroundColor Green
    
    # Step 4: Create virtual environment
    Write-Host "[4/8] Creating virtual environment"
    python -m venv .venv
    
    # Activate virtual environment
    .\.venv\Scripts\Activate.ps1
    
    # Step 5: Install dependencies
    Write-Host "[5/8] Installing dependencies"
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
    
    # Step 6: Setup environment
    Write-Host "[6/8] Setting up environment"
    
    # Check for GEMINI_API_KEY environment variable
    $ApiKey = $env:GEMINI_API_KEY
    if (-not $ApiKey) {
        Write-Host "ERROR: GEMINI_API_KEY environment variable not set" -ForegroundColor Red
        Write-Host "Set it with: `$env:GEMINI_API_KEY='your-key-here'" -ForegroundColor Yellow
        exit 1
    }
    
    # Create .env file
    "GEMINI_API_KEY=$ApiKey" | Out-File -FilePath ".env" -Encoding utf8
    "GEMINI_MODEL=gemini-1.5-flash-latest" | Out-File -FilePath ".env" -Encoding utf8 -Append
    Write-Host "  ✓ Created .env file" -ForegroundColor Green
    
    # Check for data pack
    Write-Host "  Checking for data pack..."
    if (-not (Test-Path "data/database/rail_timetable.db") -and -not (Test-Path "data/rail_capstone_pack/database/rail_timetable.db")) {
        Write-Host "  WARNING: Data pack not found" -ForegroundColor Yellow
        Write-Host "  Please unzip rail_capstone_pack.zip into data/ directory" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Assuming data pack will be provided separately..."
    } else {
        Write-Host "  ✓ Data pack found" -ForegroundColor Green
    }
    
    # Step 7: Run sample questions (if index exists)
    Write-Host "[7/8] Testing system"
    
    if (Test-Path "index/chunks.json") {
        Write-Host "  Index found, testing queries..."
        
        # Create test questions file
        $TestQuestions = @(
            @{id="Q1"; question="What is Rule 25?"},
            @{id="Q2"; question="Which trains go from Delhi to Mumbai?"},
            @{id="Q3"; question="What is the Tatkal cancellation charge?"}
        )
        
        $TestQuestions | ConvertTo-Json | Out-File -FilePath "test_questions.json" -Encoding utf8
        
        # Run questions
        python run_questions.py test_questions.json test_results.json
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ System executed successfully" -ForegroundColor Green
            
            # Check results
            if (Test-Path "test_results.json") {
                $Results = Get-Content "test_results.json" | ConvertFrom-Json
                $AnswerCount = ($Results | Where-Object { $_.dont_know -eq $false }).Count
                Write-Host "  ✓ Answered $AnswerCount / $($Results.Count) questions" -ForegroundColor Green
            }
        } else {
            Write-Host "  ✗ System execution failed" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  Index not found (run build_index.py first to build it)"
        Write-Host "  Testing contract compliance only..."
        
        # Test that ask.py works
        $TestOutput = python ask.py "What is Rule 25?" --json 2>&1 | Out-String
        
        if ($TestOutput -match '"answer"' -and $TestOutput -match '"sources"') {
            Write-Host "  ✓ Contract compliance verified" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Contract compliance failed" -ForegroundColor Red
            Write-Host $TestOutput
            exit 1
        }
    }
    
    # Step 8: Summary
    Write-Host ""
    Write-Host "[8/8] Summary"
    Write-Host "=" * 60
    Write-Host "✓ Fresh clone test PASSED" -ForegroundColor Green
    Write-Host ""
    Write-Host "Test directory: $TestDir"
    Write-Host "To clean up: Remove-Item '$TestDir' -Recurse -Force"
    Write-Host "=" * 60
    
} catch {
    Write-Host ""
    Write-Host "ERROR: Test failed with exception" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
} finally {
    # Return to original directory
    Set-Location $PSScriptRoot
}
