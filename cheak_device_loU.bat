@echo off
adb shell dumpsys window | findstr "mDreamingLockscreen" > temp.txt
findstr "mDreamingLockscreen=true" temp.txt > nul
if %errorlevel%==0 (
    echo LOCKED
) else (
    findstr "mDreamingLockscreen=false" temp.txt > nul
    if %errorlevel%==1 (
        echo UNLOCKED
    ) else (
        echo Unable to determine lock status
    )
)
del temp.txt
