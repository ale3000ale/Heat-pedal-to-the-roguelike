@echo off
REM ============================================================================
REM Fase 4 — Bootstrap completo del repository (Windows CMD)
REM ============================================================================
REM Esegui questo file dalla radice del progetto Heat-pedal-to-the-roguelike/
REM ============================================================================

echo.
echo ============================================================================
echo Fase 4 — Bootstrap completo del repository
echo ============================================================================
echo.



echo [1/10] Creo struttura cartelle backend...
mkdir backend 2>nul
mkdir backend\app 2>nul
mkdir backend\app\models 2>nul
mkdir backend\app\schemas 2>nul
mkdir backend\app\repositories 2>nul
mkdir backend\app\services 2>nul
mkdir backend\app\api 2>nul
mkdir backend\app\api\routers 2>nul
mkdir backend\app\auth 2>nul
mkdir backend\app\tests 2>nul
mkdir backend\alembic 2>nul
mkdir backend\alembic\versions 2>nul
echo.

echo [2/10] Creo struttura cartelle script...
mkdir scripts 2>nul
mkdir scripts\windows 2>nul
mkdir scripts\unix 2>nul
echo.

echo [3/10] Creo struttura cartelle database e resources...
mkdir database 2>nul
mkdir resources 2>nul
mkdir resources\images 2>nul
mkdir resources\images\cards 2>nul
echo.

echo [4/10] Creo struttura cartelle tests e docs...
mkdir tests 2>nul
mkdir docs 2>nul
echo.

echo [5/10] Creo file Python base backend...
type nul > backend\app\__init__.py
type nul > backend\app\main.py
type nul > backend\app\config.py
type nul > backend\app\database.py
type nul > backend\app\models\__init__.py
type nul > backend\app\models\user.py
type nul > backend\app\models\team.py
type nul > backend\app\models\pilot.py
type nul > backend\app\models\deck.py
type nul > backend\app\models\championship.py
type nul > backend\app\models\championship_pilot.py
type nul > backend\app\models\race.py
type nul > backend\app\models\race_result.py
type nul > backend\app\models\deck_prototype.py
type nul > backend\app\schemas\__init__.py
type nul > backend\app\repositories\__init__.py
type nul > backend\app\services\__init__.py
type nul > backend\app\api\__init__.py
type nul > backend\app\api\routers\__init__.py
type nul > backend\app\auth\__init__.py
type nul > backend\app\tests\__init__.py
echo.

echo [6/10] Creo file configurazione backend...
type nul > backend\pyproject.toml
type nul > backend\.env.example
type nul > backend\README.md
type nul > backend\alembic.ini
echo.

echo [7/10] Creo file script principali...
type nul > run-once.py
type nul > run-once.bat
type nul > run-once.sh
type nul > setup.py
type nul > setup.bat
type nul > setup.sh
echo.

echo [8/10] Creo file script interni...
type nul > scripts\windows\check-prereqs.bat
type nul > scripts\windows\install-frontend.bat
type nul > scripts\windows\install-backend.bat
type nul > scripts\windows\migrate-db.bat
type nul > scripts\windows\backup-db.bat
type nul > scripts\unix\check-prereqs.sh
type nul > scripts\unix\install-frontend.sh
type nul > scripts\unix\install-backend.sh
type nul > scripts\unix\migrate-db.sh
type nul > scripts\unix\backup-db.sh
echo.

echo [9/10] Creo file documentazione NUOVA (non sovrascrivo .md esistenti)...
type nul > PROJECT_STATUS.md
type nul > DATABASE.md
type nul > ARCHITECTURE.md
type nul > CHANGELOG.md
echo.

echo [10/10] Creo struttura frontend applicativa minima...
mkdir frontend\src\lib\api 2>nul
mkdir frontend\src\lib\components 2>nul
mkdir frontend\src\lib\stores 2>nul
mkdir frontend\src\lib\types 2>nul
echo.

echo ============================================================================
echo Fase 4 — Bootstrap repository completata!
echo ============================================================================
echo.
echo Struttura creata:
echo   - backend/ con app/, models/, schemas/, repositories/, services/, api/, auth/, tests/, alembic/
echo   - scripts/windows/ e scripts/unix/
echo   - database/, resources/images/cards/, tests/, docs/
echo   - run-once.py, run-once.bat, run-once.sh, setup.py, setup.bat, setup.sh
echo   - Documentazione NUOVA: PROJECT_STATUS.md, DATABASE.md, ARCHITECTURE.md, CHANGELOG.md
echo   - frontend/src/lib/api/, components/, stores/, types/
echo.
echo I file .md esistenti (PROJECT_SPEC.md, README.md, SETUP.md, SCRIPTS.md, ecc.) NON sono stati sovrascritti.
echo.
echo Prossimo passo: popolare i file con contenuto reale.
echo.
pause