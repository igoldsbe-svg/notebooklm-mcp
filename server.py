import sys
import os
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# On Railway, write auth cookies from env var to the path notebooklm-py expects.
# Set NOTEBOOKLM_AUTH_JSON in Railway Variables with the contents of storage_state.json.
_auth_json = os.environ.get("NOTEBOOKLM_AUTH_JSON", "")
if _auth_json:
    _storage_path = Path("/root/.notebooklm/storage_state.json")
    _storage_path.parent.mkdir(parents=True, exist_ok=True)
    _storage_path.write_text(_auth_json)

NOTEBOOKLM = os.environ.get("NOTEBOOKLM_BIN", "notebooklm")
PORT = int(os.environ.get("PORT", 8484))

mcp = FastMCP("notebooklm", host="0.0.0.0", port=PORT)


def run_cli(*args, timeout=120):
    result = subprocess.run(
        [NOTEBOOKLM, *args],
        capture_output=True, text=True, timeout=timeout
    )
    output = result.stdout.strip()
    if result.returncode != 0 and result.stderr.strip():
        output = (output + "\n" + result.stderr.strip()).strip()
    return output or "(no output)"


@mcp.tool()
def notebooklm_list() -> str:
    """List all NotebookLM notebooks."""
    return run_cli("list")


@mcp.tool()
def notebooklm_create(title: str) -> str:
    """Create a new NotebookLM notebook with the given title."""
    return run_cli("create", title)


@mcp.tool()
def notebooklm_use(notebook_id: str) -> str:
    """Set the active notebook context by notebook ID."""
    return run_cli("use", notebook_id)


@mcp.tool()
def notebooklm_status() -> str:
    """Show the current active notebook context."""
    return run_cli("status")


@mcp.tool()
def notebooklm_ask(question: str) -> str:
    """Ask the current notebook a question (RAG query)."""
    return run_cli("ask", question, timeout=120)


@mcp.tool()
def notebooklm_source_add(url_or_path: str) -> str:
    """Add a URL or YouTube link as a source to the current notebook."""
    return run_cli("source", "add", url_or_path, timeout=180)


@mcp.tool()
def notebooklm_source_list() -> str:
    """List all sources in the current notebook."""
    return run_cli("source", "list")


@mcp.tool()
def notebooklm_artifact_list() -> str:
    """List all generated artifacts (audio, video, quiz, etc.) in the current notebook."""
    return run_cli("artifact", "list")


@mcp.tool()
def notebooklm_generate_audio(instructions: str = "") -> str:
    """Generate a podcast-style audio overview from the current notebook. Optionally provide focus instructions."""
    args = ["generate", "audio"]
    if instructions:
        args.append(instructions)
    return run_cli(*args, timeout=600)


@mcp.tool()
def notebooklm_generate_report(format: str = "briefing-doc") -> str:
    """Generate a written report. Format options: briefing-doc, study-guide, blog-post."""
    return run_cli("generate", "report", "--format", format, timeout=300)


@mcp.tool()
def notebooklm_generate_quiz() -> str:
    """Generate a quiz from the current notebook's sources."""
    return run_cli("generate", "quiz", timeout=300)


@mcp.tool()
def notebooklm_generate_flashcards() -> str:
    """Generate flashcards from the current notebook's sources."""
    return run_cli("generate", "flashcards", timeout=300)


@mcp.tool()
def notebooklm_generate_mind_map() -> str:
    """Generate a mind map from the current notebook's sources."""
    return run_cli("generate", "mind-map", timeout=120)


@mcp.tool()
def notebooklm_download_report(output_path: str) -> str:
    """Download the generated report to the specified file path (e.g. /tmp/report.md)."""
    return run_cli("download", "report", output_path, timeout=60)


@mcp.tool()
def notebooklm_download_audio(output_path: str) -> str:
    """Download the generated audio overview to the specified file path (e.g. /tmp/podcast.mp3)."""
    return run_cli("download", "audio", output_path, timeout=120)


@mcp.tool()
def notebooklm_history() -> str:
    """Show the conversation history for the current notebook."""
    return run_cli("history")


@mcp.tool()
def notebooklm_auth_check() -> str:
    """Check the current authentication status."""
    return run_cli("auth", "check")


if __name__ == "__main__":
    if "--sse" in sys.argv:
        import uvicorn
        app = mcp.sse_app()
        uvicorn.run(app, host="0.0.0.0", port=PORT)
    else:
        mcp.run(transport="stdio")
