@echo off
REM ============================================================================
REM Fase 3 — Verifica bootstrap frontend (Windows CMD)
REM ============================================================================
REM Esegui questo file dalla radice del progetto Heat-pedal-to-the-roguelike/
REM dopo aver creato frontend/ con npx sv create
REM ============================================================================

echo.
echo ============================================================================
echo Fase 3 — Verifica bootstrap frontend
echo ============================================================================
echo.

REM Verifica che frontend/ esista
if not exist frontend (
    echo ERRORE: frontend/ non trovata. Esegui prima phase3_bootstrap.bat o npx sv create frontend
    pause
    exit /b 1
)

REM 1. Entra in frontend/
echo [1/8] Entro in frontend/...
cd frontend
if %errorlevel% neq 0 (
    echo ERRORE: Impossibile entrare in frontend/
    pause
    exit /b 1
)
echo.

REM 2. Verifica package.json e package-lock.json
echo [2/8] Verifica package.json e package-lock.json...
if exist package.json (
    echo package.json: presente
) else (
    echo ERRORE: package.json non trovato!
    pause
    exit /b 1
)
if exist package-lock.json (
    echo package-lock.json: presente
) else (
    echo ERRORE: package-lock.json non trovato!
    pause
    exit /b 1
)
echo.

REM 3. Elenca script npm disponibili
echo [3/8] Elenco script npm disponibili...
npm run
echo.

REM 4. Type-check
echo [4/8] Type-check...
call npm run check
if %errorlevel% neq 0 (
    echo.
    echo ERRORE: Type-check fallito.
    pause
    exit /b 1
)
echo Type-check: OK
echo.

REM 5. Lint
echo [5/8] Lint...
call npm run lint
if %errorlevel% neq 0 (
    echo.
    echo ERRORE: Lint fallito.
    pause
    exit /b 1
)
echo Lint: OK
echo.

REM 6. Test Vitest
echo [6/8] Test Vitest...
call npm run test
if %errorlevel% neq 0 (
    echo.
    echo ERRORE: Test fallito.
    pause
    exit /b 1
)
echo Test: OK
echo.

REM 7. Build di produzione
echo [7/8] Build di produzione...
call npm run build
if %errorlevel% neq 0 (
    echo.
    echo ERRORE: Build fallita.
    pause
    exit /b 1
)
echo Build: OK
echo.

REM 8. Torna alla radice e verifica struttura
echo [8/8] Torno alla radice e verifico struttura...
cd ..
echo.
echo Contenuto frontend/:
dir frontend
echo.
echo Contenuto frontend\src:
dir frontend\src
echo.
echo Contenuto frontend\src\routes:
dir frontend\src\routes
echo.

echo ============================================================================
echo Fase 3 — Verifica completata con successo!
echo ============================================================================
echo.
echo Prossimo passo: incolla questo output al tuo assistente per procedere con la Fase 4.
echo.
pause