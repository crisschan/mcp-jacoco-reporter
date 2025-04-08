from mcp.server.fastmcp import FastMCP
from jacoco_reporter import JaCoCoReport
import json
import asyncio
import os

MCP_SERVER_NAME = "mcp-jacoco-reporter-server"
mcp= FastMCP(MCP_SERVER_NAME)

if "COVERED_TYPES" not in os.environ:
    os.environ["COVERED_TYPES"] = ["nocovered"]

COVERED_TYPES = os.environ["COVERED_TYPES"].split(",")

@mcp.tool()
async def jacoco_reporter_server(jacoco_report_path:str,covered_types=COVERED_TYPES)->json:
    """
    read jacoco report and return the coverage data in COVERED_TYPES.
    :param jacoco_report_path: jacoco report path
    :param covered_types: covered types
    :return: json data
    """
    jac=JaCoCoReport(jacoco_report_path,covered_types)
    data = jac.jacoco_to_json()
    return data