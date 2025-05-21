# MCP-JaCoCo
MCP-JaCoCo is a server tool that converts JaCoCo code coverage reports into formats optimized for Large Language Models (LLMs), making AI-driven analysis easier and more effective.

For details on generating the `jacoco.xml` report, please refer to the [official JaCoCo documentation](https://www.jacoco.org/jacoco/trunk/doc/).

# Why It Matters
As AI and LLMs play a bigger role in software development, traditional code coverage reports—like those from JaCoCo—need a makeover. While great for humans, their XML format isn’t ideal for AI tools to process or analyze. MCP-JaCoCo bridges this gap by transforming these reports into LLM-friendly formats, unlocking powerful benefits for development teams:

- Quick, meaningful summaries of code coverage
- Easy identification of untested or poorly tested code
- Smart suggestions for new test cases
- Streamlined AI-assisted test planning
- Automated documentation of coverage results
With MCP-JaCoCo, teams can tap into AI’s full potential, boosting efficiency and insight in testing workflows.

# What It Solves
- **Complex Formats**: Simplifies JaCoCo’s dense XML reports for AI use
- **Scattered Data**: Pulls coverage metrics into one accessible place
- **Slow Analysis**: Cuts down on time-consuming manual reviews
- **Integration Hurdles**: Makes raw data play nicely with AI tools

# Key Features
- **Smart Conversion**: Transforms JaCoCo XML reports into LLM-friendly JSON format
- **Flexible Coverage Types**: Supports multiple coverage metrics (instruction, branch, line, etc.)
- **Efficient Processing**: Fast and lightweight report processing
- **Structured Output**: Well-organized JSON format for easy AI consumption
- **Customizable Analysis**: Filter coverage data by specific metrics of interest

# Installation
Install MCP-JaCoCo using uv with this configuration:
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
        "./mcp-jacoco-reporter-server.py"
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
  - jacoco_xmlreport_path: Path to JaCoCo xml report path(jacoco.xml)
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

# CLI Usage
The `main.py` script provides a command-line interface to generate the JSON report directly.

**Usage:**
```bash
python main.py <path_to_jacoco.xml> [--covered-types <types>]
```

**Arguments:**
-   `path_to_jacoco.xml`: (Required) The path to your JaCoCo XML report file.
-   `--covered-types`: (Optional) A comma-separated string of coverage types to include in the report. Valid types are `nocovered`, `partiallycovered`, and `fullcovered`. 
    If omitted, the default is `"nocovered,partiallycovered,fullcovered"`.

**Example:**
To process a JaCoCo report and include only 'not covered' and 'partially covered' lines/branches:
```bash
python main.py /path/to/your/project/target/site/jacoco/jacoco.xml --covered-types "nocovered,partiallycovered"
```

To process with default covered types:
```bash
python main.py /path/to/your/project/target/site/jacoco/jacoco.xml
```