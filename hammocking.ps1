# Help
#   Run python script with virtual environment
#   Usage: hammocking <script> [args]
#   Example: hammocking --help
& "$PSScriptRoot\.venv\Scripts\python.exe" "$PSScriptRoot\src\hammocking\_run.py" $args
