import subprocess
import urllib.parse

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("A server for running python and bash commands")

def _format_response(result) -> str:

    stdout_decoded = result.stdout.decode('utf-8', errors='replace')
    stderr_decoded = result.stderr.decode('utf-8', errors='replace')

    output = f"""
    Lynx return code: {result.returncode}

    Stdout:
    {stdout_decoded}

    Stderr:
    {stderr_decoded}
    """
    return output


def _duckduckgo_search(query: str) -> str:
    query_string = urllib.parse.quote_plus(query, safe='')
    url = f"https://duckduckgo.com/?&q={query_string}"
    result = subprocess.run(["lynx", "-dump", url], capture_output=True, check=False)
    return _format_response(result)

def _view_webpage(url: str) -> str:
    result = subprocess.run(["lynx", "-dump", url], capture_output=True, check=True)
    return _format_response(result)


@mcp.tool()
def view_webpage(url: str) -> str:
    return _view_webpage(url)

@mcp.tool()
def duckduckgo_search(query: str) -> str:
    return _duckduckgo_search(query)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
