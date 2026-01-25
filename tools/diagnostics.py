"""
Diagnostics Tools
Error log parsing, config validation, and troubleshooting
"""
import json
import re
from typing import Optional
import config
from moonraker import get_client


def register_diagnostics_tools(mcp):
    """Register diagnostics tools."""
    
    @mcp.tool()
    async def parse_klippy_log(lines: int = 200) -> str:
        """
        Parse klippy.log for errors, warnings, and important messages.
        
        Args:
            lines: Number of recent lines to analyze (default: 200)
        """
        client = get_client()
        session = await client._get_session()
        
        url = f"{client.base_url}/server/files/logs/klippy.log"
        
        try:
            async with session.get(url) as response:
                if response.status == 404:
                    return json.dumps({"error": "klippy.log not found"})
                response.raise_for_status()
                content = await response.text()
                
                # Get last N lines
                all_lines = content.split('\n')
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                errors = []
                warnings = []
                shutdowns = []
                tmc_errors = []
                mcu_issues = []
                
                for i, line in enumerate(recent_lines):
                    line_lower = line.lower()
                    
                    # Errors
                    if 'error' in line_lower or 'exception' in line_lower:
                        errors.append({"line": len(all_lines) - lines + i + 1, "text": line.strip()})
                    
                    # Warnings
                    elif 'warning' in line_lower or 'warn' in line_lower:
                        warnings.append({"line": len(all_lines) - lines + i + 1, "text": line.strip()})
                    
                    # Shutdown events
                    elif 'shutdown' in line_lower:
                        shutdowns.append({"line": len(all_lines) - lines + i + 1, "text": line.strip()})
                    
                    # TMC driver issues
                    elif 'tmc' in line_lower and ('fault' in line_lower or 'error' in line_lower or 'overtemp' in line_lower):
                        tmc_errors.append({"line": len(all_lines) - lines + i + 1, "text": line.strip()})
                    
                    # MCU issues
                    elif 'mcu' in line_lower and ('timeout' in line_lower or 'disconnect' in line_lower or 'lost' in line_lower):
                        mcu_issues.append({"line": len(all_lines) - lines + i + 1, "text": line.strip()})
                
                return json.dumps({
                    "analyzed_lines": len(recent_lines),
                    "summary": {
                        "errors": len(errors),
                        "warnings": len(warnings),
                        "shutdowns": len(shutdowns),
                        "tmc_errors": len(tmc_errors),
                        "mcu_issues": len(mcu_issues),
                    },
                    "errors": errors[-10:] if errors else [],  # Last 10
                    "warnings": warnings[-5:] if warnings else [],  # Last 5
                    "shutdowns": shutdowns[-3:] if shutdowns else [],  # Last 3
                    "tmc_errors": tmc_errors[-5:] if tmc_errors else [],
                    "mcu_issues": mcu_issues[-5:] if mcu_issues else [],
                }, indent=2)
                
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    @mcp.tool()
    async def get_recent_errors(count: int = 10) -> str:
        """
        Get the most recent errors from klippy.log with context.
        
        Args:
            count: Number of errors to return (default: 10)
        """
        client = get_client()
        session = await client._get_session()
        
        url = f"{client.base_url}/server/files/logs/klippy.log"
        
        try:
            async with session.get(url) as response:
                if response.status == 404:
                    return json.dumps({"error": "klippy.log not found"})
                response.raise_for_status()
                content = await response.text()
                
                lines = content.split('\n')
                
                errors_with_context = []
                
                for i, line in enumerate(lines):
                    if 'error' in line.lower() or 'exception' in line.lower():
                        # Get context: 2 lines before and 2 after
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        context = lines[start:end]
                        
                        errors_with_context.append({
                            "line_number": i + 1,
                            "error": line.strip(),
                            "context": [l.strip() for l in context]
                        })
                
                # Return last N errors
                recent_errors = errors_with_context[-count:] if errors_with_context else []
                
                return json.dumps({
                    "total_errors_found": len(errors_with_context),
                    "showing": len(recent_errors),
                    "errors": recent_errors
                }, indent=2)
                
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    @mcp.tool()
    async def check_common_issues() -> str:
        """
        Check for common configuration issues and problems.
        Analyzes printer state and recent logs for known issues.
        """
        client = get_client()
        issues = []
        warnings = []
        
        # Check printer status
        status_result = await client.get_printer_status()
        if "error" in status_result:
            issues.append({
                "category": "connection",
                "severity": "critical",
                "message": "Cannot connect to Klipper",
                "suggestion": "Check if Klipper service is running"
            })
            return json.dumps({"issues": issues, "warnings": warnings})
        
        status = status_result.get("result", {}).get("status", {})
        
        # Check print state
        print_stats = status.get("print_stats", {})
        if print_stats.get("state") == "error":
            issues.append({
                "category": "print",
                "severity": "high",
                "message": f"Printer in error state: {print_stats.get('message', 'unknown')}",
                "suggestion": "Check klippy.log for details and restart Klipper"
            })
        
        # Check temperatures
        extruder = status.get("extruder", {})
        if extruder.get("temperature", 0) > 50 and extruder.get("target", 0) == 0:
            warnings.append({
                "category": "temperature",
                "message": "Extruder is hot but target is 0",
                "suggestion": "Extruder may still be cooling down from previous print"
            })
        
        bed = status.get("heater_bed", {})
        if bed.get("temperature", 0) > 50 and bed.get("target", 0) == 0:
            warnings.append({
                "category": "temperature",
                "message": "Bed is hot but target is 0",
                "suggestion": "Bed may still be cooling down"
            })
        
        # Check homing
        toolhead = status.get("toolhead", {})
        homed = toolhead.get("homed_axes", "")
        if homed != "xyz":
            warnings.append({
                "category": "homing",
                "message": f"Not all axes homed (current: {homed or 'none'})",
                "suggestion": "Run G28 to home all axes before printing"
            })
        
        # Check for idle timeout
        idle = status.get("idle_timeout", {})
        if idle.get("state") == "Printing" and print_stats.get("state") != "printing":
            warnings.append({
                "category": "state",
                "message": "Idle timeout thinks printer is printing but print_stats disagrees",
                "suggestion": "State may be out of sync - consider FIRMWARE_RESTART"
            })
        
        return json.dumps({
            "issues_found": len(issues),
            "warnings_found": len(warnings),
            "issues": issues,
            "warnings": warnings,
            "status": "healthy" if not issues else "needs_attention"
        }, indent=2)
    
    @mcp.tool()
    async def get_mcu_status() -> str:
        """
        Get MCU (microcontroller) status including timing and connection info.
        """
        client = get_client()
        
        result = await client.query_printer_objects({
            "mcu": ["mcu_version", "mcu_build_versions", "mcu_constants", "last_stats"],
            "toolhead": ["max_velocity", "max_accel", "square_corner_velocity"]
        })
        
        if "error" in result:
            return json.dumps({"error": result["error"]})
        
        status = result.get("result", {}).get("status", {})
        
        mcu = status.get("mcu", {})
        toolhead = status.get("toolhead", {})
        
        return json.dumps({
            "mcu": {
                "version": mcu.get("mcu_version"),
                "build_versions": mcu.get("mcu_build_versions"),
                "last_stats": mcu.get("last_stats"),
            },
            "motion": {
                "max_velocity": toolhead.get("max_velocity"),
                "max_accel": toolhead.get("max_accel"),
                "square_corner_velocity": toolhead.get("square_corner_velocity"),
            }
        }, indent=2)
    
    @mcp.tool()
    async def get_gcode_history(count: int = 50) -> str:
        """
        Get recent G-code commands and responses.
        
        Args:
            count: Number of recent commands to return (default: 50)
        """
        client = get_client()
        result = await client.get_gcode_store(count=count)
        
        if "error" in result:
            return json.dumps({"error": result["error"]})
        
        gcode_store = result.get("result", {}).get("gcode_store", [])
        
        commands = []
        for entry in gcode_store[-count:]:
            commands.append({
                "message": entry.get("message"),
                "time": entry.get("time"),
                "type": entry.get("type"),
            })
        
        return json.dumps({
            "count": len(commands),
            "commands": commands
        }, indent=2)
    
    @mcp.tool()
    async def diagnose_problem(symptom: str) -> str:
        """
        Get troubleshooting suggestions based on a symptom description.
        
        Args:
            symptom: Description of the problem (e.g., 'layer shifts', 'nozzle clog', 'bed adhesion')
        """
        symptom_lower = symptom.lower()
        
        troubleshooting = {
            "layer shift": {
                "possible_causes": [
                    "Belts too loose",
                    "Stepper motor overheating (TMC overtemp)",
                    "Acceleration too high",
                    "Nozzle hitting print",
                    "Grub screws loose on pulleys"
                ],
                "suggestions": [
                    "Check belt tension",
                    "Check TMC driver temps (run parse_klippy_log)",
                    "Reduce max_accel in printer.cfg",
                    "Check for Z-hop in slicer",
                    "Tighten grub screws on motor pulleys"
                ],
                "gcode_commands": ["M569 (check TMC)", "SET_VELOCITY_LIMIT ACCEL=3000"]
            },
            "adhesion": {
                "possible_causes": [
                    "Bed not level",
                    "Z offset too high",
                    "Bed not clean",
                    "Bed temp too low",
                    "First layer speed too fast"
                ],
                "suggestions": [
                    "Run bed mesh calibration",
                    "Adjust Z offset (negative = closer)",
                    "Clean bed with IPA",
                    "Increase bed temp by 5-10°C",
                    "Reduce first layer speed to 20mm/s"
                ]
            },
            "clog": {
                "possible_causes": [
                    "Heat creep",
                    "Partial clog from debris",
                    "Wet filament",
                    "Gap between nozzle and heatbreak",
                    "Retraction too high"
                ],
                "suggestions": [
                    "Check hotend fan is working",
                    "Do cold pull to clear partial clog",
                    "Dry filament (4h at 50-60°C)",
                    "Re-seat nozzle hot-tightened",
                    "Reduce retraction distance"
                ]
            },
            "stringing": {
                "possible_causes": [
                    "Retraction too low",
                    "Temperature too high",
                    "Wet filament",
                    "Travel speed too slow"
                ],
                "suggestions": [
                    "Increase retraction distance/speed",
                    "Lower hotend temp by 5-10°C",
                    "Dry filament",
                    "Increase travel speed"
                ]
            },
            "underextrusion": {
                "possible_causes": [
                    "Partial clog",
                    "Extruder tension too low",
                    "Incorrect e-steps",
                    "Filament grinding",
                    "PTFE tube gap"
                ],
                "suggestions": [
                    "Check for clog (cold pull)",
                    "Increase extruder gear tension",
                    "Calibrate e-steps",
                    "Check extruder gear for worn teeth",
                    "Check PTFE tube seating"
                ]
            }
        }
        
        # Find matching symptom
        matched = None
        for key in troubleshooting:
            if key in symptom_lower:
                matched = troubleshooting[key]
                matched["symptom"] = key
                break
        
        if matched:
            return json.dumps(matched, indent=2)
        else:
            return json.dumps({
                "message": f"No specific troubleshooting found for '{symptom}'",
                "available_topics": list(troubleshooting.keys()),
                "suggestion": "Try describing the symptom differently or check klippy.log for errors"
            }, indent=2)
