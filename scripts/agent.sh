#!/bin/bash

# Stash Agent Management Script

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="$SCRIPT_DIR/src/main.py"
PID_FILE="$SCRIPT_DIR/logs/agent.pid"
LOG_FILE="$SCRIPT_DIR/logs/agent.log"

# Create logs directory if not exists
mkdir -p "$SCRIPT_DIR/logs"

start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Agent is already running with PID $PID"
            return 1
        fi
    fi
    
    echo "Starting Stash Agent..."
    nohup python3 "$PYTHON_SCRIPT" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Agent started with PID $(cat $PID_FILE)"
    echo "Check logs: tail -f $LOG_FILE"
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Agent is not running (no PID file found)"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "Agent is not running (PID $PID not found)"
        rm "$PID_FILE"
        return 1
    fi
    
    echo "Stopping Stash Agent (PID $PID)..."
    kill $PID
    
    # Wait for process to stop
    for i in {1..10}; do
        if ! ps -p $PID > /dev/null 2>&1; then
            echo "Agent stopped successfully"
            rm "$PID_FILE"
            return 0
        fi
        sleep 1
    done
    
    echo "Agent did not stop gracefully, forcing..."
    kill -9 $PID
    rm "$PID_FILE"
    echo "Agent force stopped"
}

status() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Agent is not running (no PID file)"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    
    if ps -p $PID > /dev/null 2>&1; then
        echo "Agent is running with PID $PID"
        echo "Log file: $LOG_FILE"
        return 0
    else
        echo "Agent is not running (PID $PID not found)"
        rm "$PID_FILE"
        return 1
    fi
}

restart() {
    echo "Restarting Stash Agent..."
    stop
    sleep 2
    start
}

logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "No log file found at $LOG_FILE"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac

exit 0
