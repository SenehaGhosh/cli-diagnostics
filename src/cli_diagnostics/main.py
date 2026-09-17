import sys
import os
import json
import shutil
import platform
import argparse

def inspect_system():
    """Inspects Python version, disk space, environment variables, and developer tools."""
    # Disk space info
    total, used, free = shutil.disk_usage("/")
    
    # Check common developer tools
    tools = ["git", "docker", "gcc", "python3"]
    tool_status = {tool: bool(shutil.which(tool)) for tool in tools}

    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "disk_space_gb": {
            "total": round(total / (1024**3), 2),
            "used": round(used / (1024**3), 2),
            "free": round(free / (1024**3), 2),
        },
        "developer_tools": tool_status,
        "environment_variables": dict(os.environ)
    }

def analyze_events(file_path):
    """Parses event JSON files and computes simple diagnostic summary metrics."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    events = data.get("events", [])
    total_events = len(events)
    error_count = sum(1 for e in events if e.get("level") == "ERROR")
    warn_count = sum(1 for e in events if e.get("level") == "WARN")
    
    return {
        "generated_for": data.get("generated_for", "Unknown"),
        "total_events": total_events,
        "error_count": error_count,
        "warn_count": warn_count,
        "events": events
    }

def print_human_readable(sys_info, log_summary=None):
    """Prints diagnostic output in a formatted human-readable report."""
    print("========================================")
    print("       CLI DIAGNOSTICS REPORT           ")
    print("========================================")
    print(f"Python Version : {sys_info['python_version']}")
    print(f"Platform       : {sys_info['platform']}")
    print("\n[Disk Usage]")
    print(f"  Free Space   : {sys_info['disk_space_gb']['free']} GB / {sys_info['disk_space_gb']['total']} GB")
    
    print("\n[Developer Tools Installed]")
    for tool, installed in sys_info['developer_tools'].items():
        # Changed '✓' / '✗' to ASCII '[OK]' / '[MISSING]' to prevent Windows charmap encoding errors
        status = "[OK] Installed" if installed else "[MISSING] Not Found"
        print(f"  {tool:<12} : {status}")

    if log_summary:
        print("\n[Log File Analysis]")
        print(f"  Target       : {log_summary['generated_for']}")
        print(f"  Total Events : {log_summary['total_events']}")
        print(f"  Warnings     : {log_summary['warn_count']}")
        print(f"  Errors       : {log_summary['error_count']}")
    print("========================================")

def main():
    parser = argparse.ArgumentParser(description="Packaged CLI Diagnostics Tool")
    parser.add_argument("--file", "-f", help="Path to diagnostic JSON log file to analyze")
    parser.add_argument("--json", action="store_true", help="Output results in raw JSON format")
    args = parser.parse_args()

    # Step 1: Perform System Diagnostics
    try:
        sys_info = inspect_system()
    except Exception as e:
        sys.stderr.write(f"Error inspecting system: {e}\n")
        sys.exit(1)

    # Step 2: Read & Parse Log File (if provided)
    log_summary = None
    if args.file:
        if not os.path.exists(args.file):
            sys.stderr.write(f"Error: File '{args.file}' not found.\n")
            sys.exit(2)  # Exit code 2 for bad arguments / missing paths
        
        try:
            log_summary = analyze_events(args.file)
        except json.JSONDecodeError:
            sys.stderr.write(f"Error: File '{args.file}' contains malformed JSON.\n")
            sys.exit(2)
        except Exception as e:
            sys.stderr.write(f"Error reading file: {e}\n")
            sys.exit(1)

    # Step 3: Format Output
    output_data = {
        "system_info": sys_info,
        "log_summary": log_summary
    }

    if args.json:
        print(json.dumps(output_data, indent=2))
    else:
        print_human_readable(sys_info, log_summary)

    # Return Exit Code 0 on Success
    sys.exit(0)

if __name__ == "__main__":
    main()