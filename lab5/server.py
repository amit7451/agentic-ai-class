"""
Model Context Protocol (MCP) Server: College Server
Exposes student records, marks, and attendance tools over HTTP (streamable-http).
"""

import os
import sys
from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

# Load environment variables
load_dotenv()

SERVER_HOST = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))

# Initialize MCP Server
mcp = MCPServer("College Server")

# In-memory student records database
students = {
    "ravi": {
        "name": "Ravi",
        "marks": {
            "python": 85,
            "ai": 90,
            "dbms": 78
        },
        "attendance": 87
    },
    "praveen": {
        "name": "Praveen",
        "marks": {
            "python": 92,
            "ai": 88,
            "dbms": 95
        },
        "attendance": 91
    },
    "ananya": {
        "name": "Ananya",
        "marks": {
            "python": 95,
            "ai": 94,
            "dbms": 90
        },
        "attendance": 96
    }
}


@mcp.tool()
def get_student(name: str) -> dict:
    """Get complete profile, marks, and attendance information about a student."""
    return students.get(
        name.lower(),
        {"error": f"Student '{name}' not found."}
    )


@mcp.tool()
def get_marks(name: str) -> dict:
    """Get subject marks of a student."""
    student = students.get(name.lower())
    if not student:
        return {"error": f"Student '{name}' not found."}
    return student["marks"]


@mcp.tool()
def get_attendance(name: str) -> str:
    """Get attendance percentage of a student."""
    student = students.get(name.lower())
    if not student:
        return f"Student '{name}' not found."
    return f"{student['name']}'s attendance is {student['attendance']}%"


@mcp.tool()
def calculate_average(name: str) -> float:
    """Calculate average marks across all subjects for a student."""
    student = students.get(name.lower())
    if not student:
        return 0.0
    marks = student["marks"].values()
    return round(sum(marks) / len(marks), 2)


def main():
    print("=" * 60)
    print(" College MCP Server (Model Context Protocol)")
    print("=" * 60)
    print(f"Server Name: College Server")
    print(f"Transport  : streamable-http")
    print(f"Endpoint   : http://{SERVER_HOST}:{SERVER_PORT}/mcp")
    print("Registered Tools:")
    print(" - get_student(name: str)")
    print(" - get_marks(name: str)")
    print(" - get_attendance(name: str)")
    print(" - calculate_average(name: str)")
    print("=" * 60)
    print("Starting server... (Press Ctrl+C to stop)")

    mcp.run(
        transport="streamable-http",
        host=SERVER_HOST,
        port=SERVER_PORT
    )


if __name__ == "__main__":
    main()
