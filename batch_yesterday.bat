@echo off
REM ファイル実行フォルダへ移動
cd /d "%~dp0"

REM データ取得日の生成
FOR /F "usebackq" %%a IN (`powershell "("Get-Date")".AddDays"("-1")".ToString"("'yyyy/MM/dd'")"`) DO SET targetdate=%%a

REM データ取得
echo python main.py --start_date %targetdate% --end_date %targetdate% --proxy
python main.py --start_date %targetdate% --end_date %targetdate% --proxy
