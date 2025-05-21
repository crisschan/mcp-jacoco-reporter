from mcp.server.fastmcp import FastMCP
from jacoco_reporter import JaCoCoReport
import json
import asyncio
import os

MCP_SERVER_NAME = "mcp-jacoco-reporter-server"
mcp= FastMCP(MCP_SERVER_NAME)

if "COVERED_TYPES" not in os.environ:
    os.environ["COVERED_TYPES"] = "nocovered,partiallycovered,fullcovered"

COVERED_TYPES = os.environ["COVERED_TYPES"].split(",")

@mcp.tool()
async def jacoco_reporter_server(jacoco_xmlreport_path:str,covered_types=COVERED_TYPES)->json:
    """
    read jacoco report and return the coverage data in COVERED_TYPES.
    :param jacoco_xmlreport_path: jacoco.xml report path
    :param covered_types: covered types ['nocovered', 'partiallycovered', 'fullcovered'],nocovered is not covered, partiallycovered is partially covered, fullcovered is fully covered
    :return: json data
    """
    jac=JaCoCoReport(jacoco_xmlreport_path,covered_types)
    data = jac.jacoco_to_json()
    return data