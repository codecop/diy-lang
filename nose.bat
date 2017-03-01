@FOR /F "usebackq delims==" %%i IN (`dir /s /b test_1_*.py`) DO @call python -W ignore::DeprecationWarning -m nose --stop -q -w %%~pi
