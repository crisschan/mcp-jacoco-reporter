# MCP-JaCoCo
MCP-JaCoCo is a MCP server that reads JaCoCo code coverage reports and returns them in LLM-friendly formats.

# Motivation
As AI and Large Language Models (LLMs) become increasingly integral to software development, there is a growing need to bridge the gap between traditional code coverage reporting and AI-assisted analysis. Traditional JaCoCo coverage report formats, while human-readable, aren't optimized for LLM consumption and processing.

MCP-JaCoCo addresses this challenge by transforming JaCoCo coverage reports into LLM-friendly formats. This transformation enables AI models to better understand, analyze, and provide insights about code coverage results, making it easier to:

- Generate meaningful coverage summaries and insights
- Identify areas with insufficient test coverage
- Suggest potential test cases for uncovered code
- Enable more effective AI-assisted test planning
- Facilitate automated coverage documentation generation

By optimizing coverage reports for LLM consumption, MCP-JaCoCo helps development teams leverage the full potential of AI tools in their testing workflow, leading to more efficient and intelligent code coverage analysis and test planning.

# Problems Solved
- **Format Complexity**: Traditional JaCoCo XML reports are complex and not optimized for AI consumption
- **Data Accessibility**: Coverage data is scattered across different metrics and requires parsing
- **Analysis Efficiency**: Manual coverage analysis is time-consuming and prone to oversight
- **Integration Challenges**: Raw coverage data is difficult to integrate with AI-powered tools

# Key Features
- **Smart Conversion**: Transforms JaCoCo XML reports into LLM-friendly JSON format
- **Flexible Coverage Types**: Supports multiple coverage metrics (instruction, branch, line, etc.)
- **Efficient Processing**: Fast and lightweight report processing
- **Structured Output**: Well-organized JSON format for easy AI consumption
- **Customizable Analysis**: Filter coverage data by specific metrics of interest

# Installation
To install mcp-jacoco-reporter using uv:
```
{
  "mcpServers": {
     "mcp-jacoco-reporter-server": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "/Users/crisschan/workspace/pyspace/mcp-jacoco-reporter/mcp-jacoco-reporter-server.py"
      ],
      "env": {
        "COVERED_TYPES": "nocovered, partiallycovered, fullcovered"
      },
      "alwaysAllow": [
        "jacoco_reporter_server"
      ]
    }
  }
}
```

# Tool
## jacoco_reporter_server

- Reads JaCoCo XML report and returns coverage data in JSON format
- Input:
  - jacoco_report_path: Path to JaCoCo report path
  - covered_types: List of coverage types to include (optional)
- Return:
  - String, formatted JSON data containing coverage metrics

Example output format:
```json
[
    {
        "sourcefile": "PasswordUtil.java",
        "package": "com/cicc/ut/util",
        "lines": {
            "nocovered": [],
            "partiallycovered": []
        },
        "branch": {
            "nocovered": [],
            "partiallycovered": []
        }
    },
    {
        "sourcefile": "UserServiceImpl.java",
        "package": "com/cicc/ut/service/impl",
        "lines": {
            "nocovered": [
                33,
                67,
                69,
                71,
                72
            ],
            "partiallycovered": []
        },
        "branch": {
            "nocovered": [
                67
            ],
            "partiallycovered": [
                32
            ]
        }
    },
    {
        "sourcefile": "Constants.java",
        "package": "com/cicc/ut/constants",
        "lines": {
            "nocovered": [],
            "partiallycovered": []
        },
        "branch": {
            "nocovered": [],
            "partiallycovered": []
        }
    },
    {
        "sourcefile": "AuthException.java",
        "package": "com/cicc/ut/exceptions",
        "lines": {
            "nocovered": [],
            "partiallycovered": []
        },
        "branch": {
            "nocovered": [],
            "partiallycovered": []
        }
    },
    {
        "sourcefile": "UserService.java",
        "package": "com/cicc/ut/service",
        "lines": {
            "nocovered": [],
            "partiallycovered": []
        },
        "branch": {
            "nocovered": [],
            "partiallycovered": []
        }
    }
]
```