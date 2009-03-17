@ECHO OFF
CLS
COLOR 1B
TITLE Scripts Choice!

:Begin
:: Set script name based on keyword
ECHO ----------------------------------------------------------------------
DIR /AD /O /B
ECHO ----------------------------------------------------------------------
ECHO.
SET /P SCRIPT_NAME_ANSWER=Enter name for building script:
    SET ScriptName=%SCRIPT_NAME_ANSWER%
    IF NOT EXIST %ScriptName% (
        GOTO END
    )

:: Set window title
TITLE %ScriptName% Build Script!

:MakeBuildFolder
:: Create Build folder
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Creating \BUILD\%ScriptName%\ folder . . .
IF EXIST BUILD (
    RD BUILD /S /Q
)
MD BUILD
ECHO.

:MakeExcludeFile
:: Create exclude file
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Creating exclude.txt file . . .
ECHO.
ECHO .svn>"BUILD\exclude.txt"
ECHO Thumbs.db>>"BUILD\exclude.txt"
ECHO Desktop.ini>>"BUILD\exclude.txt"

ECHO .pyo>>"BUILD\exclude.txt"
ECHO .pyc>>"BUILD\exclude.txt"

:MakeReleaseBuild
:: Create release build
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Copying required files to \Build\%ScriptName%\ folder . . .
XCOPY %ScriptName% "BUILD\%ScriptName%" /E /Q /I /Y /EXCLUDE:BUILD\exclude.txt

ECHO.

:Cleanup
:: Delete exclude.txt file
ECHO ----------------------------------------------------------------------
ECHO.
ECHO Cleaning up . . .
DEL "BUILD\exclude.txt"
ECHO.
ECHO.

:: XBMC is installed
SET XBMC_EXE=%ProgramFiles%\XBMC
IF EXIST "%XBMC_EXE%" (
    GOTO XBMC_EXIST
) ELSE (
    GOTO Finish
)

:XBMC_EXIST
    ECHO ----------------------------------------------------------------------
    ECHO.
    ECHO XBMC is installed on your PC!
    ECHO [1] Yes, copy a new "\Build\%ScriptName%\ to %XBMC_EXE%\scripts\%ScriptName%\"
    ECHO [2] Yes, copy a new build and run XBMC in fullscreen
    ECHO [3] No, i prefer copied manually
    ECHO [4] Create ZIP "BUILD\%ScriptName%.zip"
    ECHO.
    ECHO ----------------------------------------------------------------------
    SET /P COPY_BUILD_ANSWER=Copy a new BUILD? [1/2/3/4]:
    IF /I %COPY_BUILD_ANSWER% EQU 1 GOTO COPY_BUILD
    IF /I %COPY_BUILD_ANSWER% EQU 2 GOTO COPY_BUILD
    IF /I %COPY_BUILD_ANSWER% EQU 3 GOTO Finish
    IF /I %COPY_BUILD_ANSWER% EQU 4 GOTO ZIP_BUILD

:COPY_BUILD
    :: Copy release build
    ECHO ----------------------------------------------------------------------
    ECHO.
    ECHO Copying "\Build\%ScriptName%\ to \XBMC\scripts\%ScriptName%\" folder . . .
    rem ren "%XBMC_EXE%\scripts\%ScriptName%\" %ScriptName%_old
    XCOPY "BUILD\%ScriptName%" "%XBMC_EXE%\scripts\%ScriptName%\" /E /Q /I /Y
    ECHO.

    :: Notify user of completion of copy
    ECHO ======================================================================
    ECHO.
    ECHO Build Complete and Copied.
    ECHO.
    ECHO ======================================================================
    ECHO.

    IF /I %COPY_BUILD_ANSWER% EQU 2 (
        ECHO Starting XBMC in fullscreen.
        ECHO.
        ECHO ======================================================================
        start /D"%XBMC_EXE%" XBMC.exe -fs -p
        )

    GOTO END

:ZIP_BUILD
    set ZIP="%ProgramFiles%\7-Zip\7z.exe"
    set ZIP_ROOT=7z.exe
    set ZIPOPS_EXE=a -tzip "%ScriptName%.zip" "%ScriptName%"
    ECHO IF EXIST %ZIP% ( %ZIP% %ZIPOPS_EXE%>>"BUILD\zip_build.bat"
    ECHO   ) ELSE (>>"BUILD\zip_build.bat"
    ECHO   IF EXIST %ZIP_ROOT% ( %ZIP_ROOT% %ZIPOPS_EXE%>>"BUILD\zip_build.bat"
    ECHO     ) ELSE (>>"BUILD\zip_build.bat"
    ECHO     ECHO  not installed!  Skipping .zip compression...>>"BUILD\zip_build.bat"
    ECHO     )>>"BUILD\zip_build.bat"
    ECHO   )>>"BUILD\zip_build.bat"
    cd BUILD
    ECHO Compressing "BUILD\%ScriptName%.zip"...
    CALL zip_build.bat
    ::cd ..
    ::DEL "BUILD\zip_build.bat"
    DEL zip_build.bat
    GOTO Finish

:Finish
    :: Notify user of completion
    ECHO ======================================================================
    ECHO.
    ECHO Build Complete.
    ECHO.
    ECHO Final build is located in the \BUILD\ folder.
    ECHO.
    ECHO copy: \%ScriptName%\ folder from the \BUILD\ folder.
    ECHO to: /XBMC/scripts/ folder.
    ECHO.
    ECHO ======================================================================
    ECHO.
    GOTO END

:END
    ECHO Scroll up to check for errors.
    PAUSE