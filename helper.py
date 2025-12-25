import subprocess

# Set volume of sink 0 (default sink) to 75%
subprocess.call(["pactl", "set-sink-volume", "0", "75%"])
