@echo off
REM ファイル実行フォルダへ移動
cd /d "%~dp0"

REM データ取得日の生成
FOR /F "usebackq" %%a IN (`powershell "("Get-Date -Day 1")".AddMonths"("-1")".ToString"("'yyyy/MM/dd'")"`) DO SET targetdate1=%%a
FOR /F "usebackq" %%a IN (`powershell "("Get-Date -Day 1")".AddDays"("-1")".ToString"("'yyyy/MM/dd'")"`) DO SET targetdate2=%%a

REM データ取得
echo python main.py --start_date %targetdate1% --end_date %targetdate2% --proxy
python main.py --start_date %targetdate1% --end_date %targetdate2% --proxy
