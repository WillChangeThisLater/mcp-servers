import logging
from typing import Optional

import libtmux
from fastmcp import FastMCP
from typing import Optional, List, Dict, Literal

logger = logging.getLogger(__name__)

# Create the FastMCP server
mcp = FastMCP("tmux-controller")


class TmuxMCP:
    """
    Minimal tmux controller using libtmux, wrapped for FastMCP tools.
    """

    def __init__(self, session_name: Optional[str] = None):
        """
        Initialize the tmux server. If session_name is provided, bind to it;
        otherwise default to the first available session (with a warning if
        multiple exist).
        """
        self.server = libtmux.Server()

        sessions = self.server.sessions
        if not sessions:
            raise RuntimeError("No tmux sessions found. Start one before using this server.")

        # Pick a specific session if requested
        if session_name:
            session = self.server.find_where({"session_name": session_name})
            if session is None:
                raise ValueError(f"tmux session '{session_name}' not found.")
            self.session = session
        else:
            if len(sessions) > 1:
                logger.warning(
                    "Multiple tmux sessions detected; defaulting to the first one."
                )
            self.session = sessions[0]

    # ---------- tool implementations ----------

    def list_window_ids(self) -> list[str]:
        """List tmux window IDs in the current session."""
        return [w.window_id for w in self.session.windows]

    def list_pane_ids(self, window_id: str) -> list[str]:
        """
        List pane IDs for a given tmux window ID.
        Returns an empty list if the window isn't found.
        """
        window = self.session.windows.get(window_id=window_id)
        if not window:
            return []
        return [p.pane_id for p in window.panes]

    def capture_visible_pane(self, pane_id: str) -> str:
        """Capture only the currently visible contents of a tmux pane."""
        pane: libtmux.Pane | None = self.session.panes.get(pane_id=pane_id)
        if not pane:
            raise ValueError(f"Pane '{pane_id}' not found.")
        return "\n".join(pane.capture_pane())

    def capture_full_pane(self, pane_id: str) -> str:
        """Capture the full scrollback buffer of a tmux pane."""
        pane: libtmux.Pane | None = self.session.panes.get(pane_id=pane_id)
        if not pane:
            raise ValueError(f"Pane '{pane_id}' not found.")
        return "\n".join(pane.capture_pane("-"))

    def send_keys(self, pane_id: str, keys_to_send: str, enter: bool = True) -> str:
        """
        Send keys to a tmux pane. Set enter=False to avoid sending <Enter>.
        Returns the visible contents after sending.
        """
        pane: libtmux.Pane | None = self.session.panes.get(pane_id=pane_id)
        if not pane:
            raise ValueError(f"Pane '{pane_id}' not found.")
        pane.send_keys(keys_to_send, enter=enter)
        return "\n".join(pane.capture_pane())

    def dump_all_panes(
        self,
        mode: Literal["visible", "full"] = "visible",
        max_lines: Optional[int] = None,
    ) -> List[Dict[str, object]]:
        """
        Dump contents for every pane in every window of the current session.
        This can help you look for panes containing specific content

        Args:
            mode: "visible" (default) for on-screen contents, or "full" for full scrollback.
            max_lines: if provided, return only the last N lines of each pane.

        Returns:
            A list of dicts, one per pane, with metadata and contents, e.g.:
            {
              "window_id": "@1",
              "window_name": "editor",
              "window_index": "1",
              "pane_id": "%3",
              "pane_index": "0",
              "pane_active": True,
              "pane_current_command": "nvim",
              "pane_title": "main.go",
              "pane_current_path": "/home/you/project",
              "contents": "...\n..."
            }
        """
        if mode not in ("visible", "full"):
            raise ValueError("mode must be 'visible' or 'full'")

        out: List[Dict[str, object]] = []

        for window in self.session.windows:
            win_id = getattr(window, "window_id", None)
            win_name = window.get("window_name")
            win_index = window.get("window_index")

            for pane in window.panes:
                try:
                    # capture contents
                    lines = pane.capture_pane("-") if mode == "full" else pane.capture_pane()
                    if max_lines is not None and max_lines > 0:
                        lines = lines[-max_lines:]
                    contents = "\n".join(lines)

                    # collect metadata (strings are tmux-format values)
                    pane_id = getattr(pane, "pane_id", None)
                    pane_index = pane.get("pane_index")
                    pane_active = pane.get("pane_active") == "1"
                    pane_cmd = pane.get("pane_current_command")
                    pane_title = pane.get("pane_title")
                    pane_cwd = pane.get("pane_current_path")

                    out.append(
                        {
                            "window_id": win_id,
                            "window_name": win_name,
                            "window_index": win_index,
                            "pane_id": pane_id,
                            "pane_index": pane_index,
                            "pane_active": pane_active,
                            "pane_current_command": pane_cmd,
                            "pane_title": pane_title,
                            "pane_current_path": pane_cwd,
                            "contents": contents,
                        }
                    )
                except Exception as e:
                    # Include an error entry for visibility, but don't break the sweep
                    out.append(
                        {
                            "window_id": win_id,
                            "window_name": win_name,
                            "window_index": win_index,
                            "pane_id": getattr(pane, "pane_id", None),
                            "error": f"{type(e).__name__}: {e}",
                        }
                    )

        return out


# Create the controller and register its bound methods as FastMCP tools
_tmux = TmuxMCP()
mcp.tool(_tmux.list_window_ids)
mcp.tool(_tmux.list_pane_ids)
mcp.tool(_tmux.capture_visible_pane)
mcp.tool(_tmux.capture_full_pane)
mcp.tool(_tmux.send_keys)
mcp.tool(_tmux.dump_all_panes)

if __name__ == "__main__":
    # Default stdio transport (works with Claude Desktop, Cursor, etc.)
    mcp.run(transport="stdio")
