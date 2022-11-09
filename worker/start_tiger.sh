#!/bin/bash 
# Bash script for creating the session
# TODO: Daemonize the entire thing already

_term() { 
  echo "Caught SIGTERM signal!" 
  kill -TERM "$CHILD_X" 2>/dev/null
  kill -TERM "$CHILD_W" 2>/dev/null
  kill -TERM "$CHILD_C" 2>/dev/null
}
# Catch SIGTERM since the processes run forever
trap _term SIGTERM

# Find an available display by incrementing the largest display number locked by X server
DISPLAY_NUM=$(($(ls /tmp/.X11-unix/ | sort -nr | head -n1 | cut -c 2-)+1))

# Session ID: creation time and VNC port encoded in base64
# TODO: Make Python handle this to avoid recalculations
ID=$(echo "$5:$2" | base64)

# Environment variable for display
# The need for this is because of Chromium: Passing DISPLAY as an argument is not stable
export DISPLAY=:$DISPLAY_NUM

# Start Xvnc display server, websockify proxy for VNC-to-WS proxying, and Chromium
# TODO: websockify comes with a process wrapper, check if usable for daemonizing
Xvnc :$DISPLAY_NUM -geometry $1 -rfbport $2 -rfbauth ./.vnc/passwd -SecurityTypes None &
CHILD_X=$!
websockify $3 localhost:$2 &
CHILD_W=$!
/snap/chromium/current/usr/lib/chromium-browser/chrome --no-sandbox --disable-gpu --disable-fre --no-default-browser-check --no-first-run --window-size=1920,1080 --window-position=0,0 --start-maximized --kiosk --app=$4 --user-data-dir=/tmp/worker/$ID --enable-features=OverlayScrollbar &
CHILD_C=$! 

wait "$CHILD_C"
wait "$CHILD_X"
wait "$CHILD_W"


