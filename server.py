"""
Klipper MCP Server - Main Entry Point
Compatible with Python 3.9+ (CB1/Raspberry Pi)
Run with: python server.py
"""
import asyncio
import json
import os
import sys
import traceback
from datetime import datetime
from aiohttp import web
from typing import Any, Callable, Dict

import config
from moonraker import init_client, close_client, get_client

# Tool registry
TOOLS: Dict[str, Dict[str, Any]] = {}


def audit_log(action: str, details: dict = None):
    """Write to audit log for security tracking."""
    log_path = getattr(config, 'AUDIT_LOG_FILE', '/home/biqu/klipper-mcp/data/audit.log')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details or {}
    }
    
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    except Exception as e:
        print(f"Failed to write audit log: {e}", file=sys.stderr)


# ============================================================
# Import and register all tools from tool modules
# ============================================================

def register_all_tools():
    """Import and register all tool modules."""
    from tools import register_all_tools as _register
    
    # Create a mock MCP object that captures tool registrations
    class MockMCP:
        def tool(self):
            def decorator(func):
                tool_name = func.__name__
                TOOLS[tool_name] = {
                    "function": func,
                    "description": func.__doc__ or "",
                    "name": tool_name
                }
                return func
            return decorator
    
    mock_mcp = MockMCP()
    _register(mock_mcp)
    
    print(f"✓ Registered {len(TOOLS)} tools", file=sys.stderr)


# ============================================================
# HTTP API Handlers
# ============================================================

async def handle_list_tools(request: web.Request) -> web.Response:
    """List all available tools."""
    tools_list = []
    for name, tool_info in TOOLS.items():
        tools_list.append({
            "name": name,
            "description": tool_info["description"].split('\n')[0] if tool_info["description"] else ""
        })
    
    return web.json_response({
        "tools": tools_list,
        "count": len(tools_list)
    })


async def handle_call_tool(request: web.Request) -> web.Response:
    """Call a specific tool."""
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({"error": "Invalid JSON"}, status=400)
    
    tool_name = data.get("tool") or data.get("name")
    arguments = data.get("arguments", {}) or data.get("params", {})
    
    if not tool_name:
        return web.json_response({"error": "Missing 'tool' field"}, status=400)
    
    if tool_name not in TOOLS:
        return web.json_response({
            "error": f"Unknown tool: {tool_name}",
            "available_tools": list(TOOLS.keys())
        }, status=404)
    
    tool_info = TOOLS[tool_name]
    func = tool_info["function"]
    
    # Log the call
    audit_log("tool_call", {"tool": tool_name, "arguments": arguments})
    
    try:
        # Call the tool function
        if asyncio.iscoroutinefunction(func):
            result = await func(**arguments)
        else:
            result = func(**arguments)
        
        return web.json_response({
            "tool": tool_name,
            "result": json.loads(result) if isinstance(result, str) else result
        })
    
    except TypeError as e:
        return web.json_response({
            "error": f"Invalid arguments: {str(e)}",
            "tool": tool_name
        }, status=400)
    
    except Exception as e:
        traceback.print_exc()
        return web.json_response({
            "error": str(e),
            "tool": tool_name
        }, status=500)


async def handle_server_info(request: web.Request) -> web.Response:
    """Get server information."""
    return web.json_response({
        "name": "klipper-mcp",
        "version": "1.0.0",
        "printer": config.PRINTER_NAME,
        "moonraker_url": config.MOONRAKER_URL,
        "armed": config.ARMED,
        "tools_count": len(TOOLS),
        "features": {
            "stealthchanger": True,
            "led_effects": True,
            "spoolman": config.SPOOLMAN_ENABLED,
            "tts": config.TTS_ENABLED,
        }
    })


async def handle_printer_status(request: web.Request) -> web.Response:
    """Quick printer status endpoint."""
    try:
        client = get_client()
        result = await client.get_printer_status()
        
        if "error" in result:
            return web.json_response({"error": result["error"]}, status=500)
        
        status = result.get("result", {}).get("status", {})
        print_stats = status.get("print_stats", {})
        extruder = status.get("extruder", {})
        bed = status.get("heater_bed", {})
        
        return web.json_response({
            "state": print_stats.get("state"),
            "filename": print_stats.get("filename"),
            "progress": print_stats.get("progress", 0),
            "temperatures": {
                "extruder": {
                    "current": extruder.get("temperature"),
                    "target": extruder.get("target")
                },
                "bed": {
                    "current": bed.get("temperature"),
                    "target": bed.get("target")
                }
            }
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def handle_health(request: web.Request) -> web.Response:
    """Health check endpoint."""
    try:
        client = get_client()
        result = await client.get_printer_status()
        moonraker_ok = "error" not in result
    except:
        moonraker_ok = False
    
    return web.json_response({
        "status": "ok" if moonraker_ok else "degraded",
        "moonraker_connected": moonraker_ok,
        "timestamp": datetime.now().isoformat()
    })


# ============================================================
# MCP Protocol Handler (JSON-RPC style)
# ============================================================

async def handle_mcp(request: web.Request) -> web.Response:
    """
    Handle MCP protocol requests (JSON-RPC style).
    This allows VS Code MCP clients to communicate with the server.
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"},
            "id": None
        }, status=400)
    
    method = data.get("method", "")
    params = data.get("params", {})
    request_id = data.get("id")
    
    result = None
    error = None
    
    try:
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "klipper-mcp",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": {"listChanged": False}
                }
            }
        
        elif method == "tools/list":
            tools_list = []
            for name, tool_info in TOOLS.items():
                tools_list.append({
                    "name": name,
                    "description": tool_info["description"].split('\n')[0] if tool_info["description"] else "",
                    "inputSchema": {"type": "object", "properties": {}}
                })
            result = {"tools": tools_list}
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name not in TOOLS:
                error = {"code": -32601, "message": f"Unknown tool: {tool_name}"}
            else:
                tool_info = TOOLS[tool_name]
                func = tool_info["function"]
                
                audit_log("tool_call", {"tool": tool_name, "arguments": arguments})
                
                if asyncio.iscoroutinefunction(func):
                    tool_result = await func(**arguments)
                else:
                    tool_result = func(**arguments)
                
                # Parse JSON string result if needed
                if isinstance(tool_result, str):
                    try:
                        tool_result = json.loads(tool_result)
                    except:
                        pass
                
                result = {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(tool_result, indent=2) if isinstance(tool_result, (dict, list)) else str(tool_result)
                    }]
                }
        
        elif method == "ping":
            result = {}
        
        else:
            error = {"code": -32601, "message": f"Method not found: {method}"}
    
    except Exception as e:
        traceback.print_exc()
        error = {"code": -32603, "message": str(e)}
    
    response = {"jsonrpc": "2.0", "id": request_id}
    if error:
        response["error"] = error
    else:
        response["result"] = result
    
    return web.json_response(response)


# ============================================================
# Main Application
# ============================================================

async def on_startup(app):
    """Called when the server starts."""
    print("Initializing Moonraker client...", file=sys.stderr)
    init_client()
    
    print("Registering tools...", file=sys.stderr)
    register_all_tools()
    
    audit_log("server_start", {
        "printer": config.PRINTER_NAME,
        "moonraker_url": config.MOONRAKER_URL
    })


async def on_cleanup(app):
    """Called when the server stops."""
    await close_client()
    audit_log("server_stop")
    print("Server stopped.", file=sys.stderr)


def create_app() -> web.Application:
    """Create the aiohttp application."""
    app = web.Application()
    
    # Add routes
    app.router.add_get("/", handle_server_info)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/status", handle_printer_status)
    app.router.add_get("/tools", handle_list_tools)
    app.router.add_post("/tools/call", handle_call_tool)
    app.router.add_post("/mcp", handle_mcp)  # MCP protocol endpoint
    
    # Lifecycle hooks
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    
    return app


def main():
    """Main entry point."""
    print("=" * 50, file=sys.stderr)
    print("Klipper MCP Server v1.0.0", file=sys.stderr)
    print(f"Printer: {config.PRINTER_NAME}", file=sys.stderr)
    print(f"Moonraker: {config.MOONRAKER_URL}", file=sys.stderr)
    print(f"ARMED: {config.ARMED}", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    app = create_app()
    
    print(f"Starting server on {config.MCP_HOST}:{config.MCP_PORT}", file=sys.stderr)
    print(f"API: http://{config.MCP_HOST}:{config.MCP_PORT}/", file=sys.stderr)
    print(f"MCP: http://{config.MCP_HOST}:{config.MCP_PORT}/mcp", file=sys.stderr)
    
    web.run_app(
        app,
        host=config.MCP_HOST,
        port=config.MCP_PORT,
        print=lambda x: print(x, file=sys.stderr)
    )


if __name__ == "__main__":
    main()
