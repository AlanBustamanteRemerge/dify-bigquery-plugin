#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import threading
import select

# Add the parent directory to the Python path to allow for absolute imports.
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(APP_ROOT, ".."))

# Import provider and tool modules to allow them to be discovered.
import minimal_provider
import minimal_tool

# Global flag to control heartbeat thread
heartbeat_active = True

def send_json_message(message):
    """Send JSON message to daemon via STDOUT"""
    try:
        json_str = json.dumps(message)
        print(json_str, flush=True)
    except Exception as e:
        # Fallback error message
        error_msg = json.dumps({"type": "error", "message": str(e)})
        print(error_msg, flush=True)

def heartbeat_worker():
    """Background thread to send periodic heartbeat messages"""
    global heartbeat_active
    while heartbeat_active:
        try:
            time.sleep(30)  # Send heartbeat every 30 seconds
            if heartbeat_active:
                send_json_message({
                    "type": "heartbeat",
                    "timestamp": time.time(),
                    "status": "alive"
                })
        except Exception as e:
            # Don't let heartbeat errors crash the thread
            pass

def handle_stdin_message(line):
    """Handle incoming JSON message from daemon"""
    try:
        if not line.strip():
            return
        
        message = json.loads(line.strip())
        msg_type = message.get("type", "")
        
        if msg_type == "ping":
            send_json_message({"type": "pong"})
        elif msg_type == "health_check":
            send_json_message({
                "type": "health_response", 
                "status": "healthy",
                "timestamp": time.time()
            })
        elif msg_type == "tool_invoke":
            # Handle tool invocation
            tool_name = message.get("tool_name", "minimal_tool")
            parameters = message.get("parameters", {})
            request_id = message.get("request_id")
            
            try:
                # Simple tool execution
                result = f"Tool {tool_name} executed with parameters: {parameters}"
                send_json_message({
                    "type": "tool_response",
                    "request_id": request_id,
                    "result": result,
                    "status": "success"
                })
            except Exception as e:
                send_json_message({
                    "type": "tool_response", 
                    "request_id": request_id,
                    "error": str(e),
                    "status": "error"
                })
        else:
            # Unknown message type - just acknowledge it
            send_json_message({
                "type": "ack", 
                "original_type": msg_type,
                "timestamp": time.time()
            })
            
    except json.JSONDecodeError as e:
        send_json_message({
            "type": "error", 
            "message": f"Invalid JSON: {str(e)}"
        })
    except Exception as e:
        send_json_message({
            "type": "error", 
            "message": f"Error processing message: {str(e)}"
        })

def main():
    """Entry point for the plugin - pure STDIN/STDOUT communication with heartbeat"""
    global heartbeat_active
    
    try:
        # Send ready signal
        send_json_message({
            "type": "ready",
            "plugin_info": {
                "name": "testplugin",
                "version": "1.0.56",
                "status": "initialized"
            }
        })
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=heartbeat_worker, daemon=True)
        heartbeat_thread.start()
        
        # Main communication loop
        while True:
            try:
                # Use select to check if input is available (Unix-like systems)
                if hasattr(select, 'select'):
                    ready, _, _ = select.select([sys.stdin], [], [], 1.0)  # 1 second timeout
                    if ready:
                        line = sys.stdin.readline()
                        if not line:
                            # EOF - daemon closed connection
                            break
                        handle_stdin_message(line)
                else:
                    # Fallback for systems without select
                    line = sys.stdin.readline()
                    if not line:
                        break
                    handle_stdin_message(line)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                send_json_message({
                    "type": "error", 
                    "message": f"Main loop error: {str(e)}"
                })
                
    except Exception as e:
        send_json_message({
            "type": "fatal_error", 
            "message": f"Plugin startup failed: {str(e)}"
        })
        sys.exit(1)
    finally:
        # Stop heartbeat thread
        heartbeat_active = False

if __name__ == "__main__":
    main() 