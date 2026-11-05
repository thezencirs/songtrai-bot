param(
    [string]$Language = "otomatik",
    [string]$Query = "",
    [int]$BatchCount = 1,
    [switch]$SetupBot = $true
)

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
$env:TELEGRAM_BOT_TOKEN = "8824304361:AAFeGn-3yjGbd_YA-80GHo3wS6p2v-b-pRA"
$env:TELEGRAM_CHAT_ID = "995164733"
$env:PYTHONPATH = "C:\Users\zenci\.gemini\antigravity\scratch\songtrai-bot\src;$env:PYTHONPATH"
$env:PATH = "C:\Users\zenci\.gemini\antigravity\scratch\tools\python\tools\Lib\site-packages\imageio_ffmpeg\binaries;$env:PATH"

$PYTHON_EXE = "C:\Users\zenci\.gemini\antigravity\scratch\tools\python\tools\python.exe"
$BOT_DIR = "C:\Users\zenci\.gemini\antigravity\scratch\songtrai-bot"

Set-Location $BOT_DIR

$argsList = @(
    "src/main.py",
    "--language", $Language,
    "--batch-count", "$BatchCount",
    "--output", "output/songtrai_reel_final.mp4"
)
if ($Query -ne "") {
    $argsList += @("--query", $Query)
}
if ($SetupBot) {
    $argsList += "--setup-bot"
}

& $PYTHON_EXE @argsList
