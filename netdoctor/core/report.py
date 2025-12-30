"""
Reporting module for exporting session data.
"""

import json
import csv
import io
from typing import Dict, Any, List

def export_csv(session: Dict[str, Any]) -> str:
    """
    Export session data to CSV format.
    
    Args:
        session: Session dictionary from history storage
        
    Returns:
        CSV string
    """
    results = session.get("results", [])
    if not results:
        return ""
        
    output = io.StringIO()
    # Assume results is a list of dicts, get keys from first item
    if isinstance(results[0], dict):
        writer = csv.DictWriter(output, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    else:
        # Fallback for non-dict results
        writer = csv.writer(output)
        writer.writerow(["Result"])
        for r in results:
            writer.writerow([str(r)])
            
    return output.getvalue()

def export_json(session: Dict[str, Any]) -> str:
    """
    Export session data to JSON format.
    
    Args:
        session: Session dictionary from history storage
        
    Returns:
        JSON string
    """
    return json.dumps(session, indent=4)
