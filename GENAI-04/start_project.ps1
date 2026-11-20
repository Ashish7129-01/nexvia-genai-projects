$project = "C:\multimodal-ai-studio"
$apps = @(
    @{File="app.py"; Port=8501},
    @{File="tts.py"; Port=8502},
    @{File="video_ai.py"; Port=8503},
    @{File="governance_v2.py"; Port=8505},
    @{File="dashboard.py"; Port=8506}
)
foreach ($app in $apps) {
    $file = $app.File
    $port = $app.Port
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$project'; python -m streamlit run $file --server.port $port"
    )
}
Start-Sleep -Seconds 5
Start-Process "http://localhost:8506"
