"""
PMhelper Edu — Shared application state and configuration.
All tabs read/write through this single object.
"""

import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Callable, Optional, Any


def _config_dir() -> Path:
    """Platform-appropriate config directory."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home()
    return base / ".pmhelper_edu"


@dataclass
class AppConfig:
    """Persisted app configuration. Survives restarts."""
    mode: str = "UG"                        # "UG" or "PG"
    last_project_path: str = ""
    currency_symbol: str = "$"
    rag_thresholds: dict = field(default_factory=lambda: {
        "cpi_amber_lower": 0.95,
        "spi_amber_lower": 0.95,
        "cr_amber_lower": 0.80,
        "tcpi_amber_upper": 1.10,
        "cv_amber_pct": 0.05,
        "sv_amber_pct": 0.05,
        "eac_amber_pct": 0.10,
    })

    CONFIG_PATH: Path = field(
        default_factory=lambda: _config_dir() / "config.json",
        repr=False
    )

    def save(self) -> None:
        self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "mode": self.mode,
            "last_project_path": self.last_project_path,
            "currency_symbol": self.currency_symbol,
            "rag_thresholds": self.rag_thresholds,
        }
        self.CONFIG_PATH.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls) -> "AppConfig":
        config = cls()
        if config.CONFIG_PATH.exists():
            try:
                data = json.loads(config.CONFIG_PATH.read_text())
                config.mode = data.get("mode", "UG")
                config.last_project_path = data.get("last_project_path", "")
                config.currency_symbol = data.get("currency_symbol", "$")
                config.rag_thresholds = {
                    **config.rag_thresholds,
                    **data.get("rag_thresholds", {})
                }
            except (json.JSONDecodeError, KeyError):
                pass  # corrupted config -> use defaults
        return config


class EduProjectState:
    """
    Central shared state for the Edu app.
    All tabs receive a reference to the same instance.
    Tabs call mark_dirty() after mutations.
    Tabs call subscribe() to be notified of changes.
    """

    def __init__(self):
        self.evm_project: Any = None        # Set in Phase 1 (EVMProject)
        self.risk_register: Any = None      # Set in Phase 3 (RiskRegister)
        self.mc_results: Any = None         # Set in Phase 4 (MCResults)
        self.swot_analysis: Any = None      # Set in Phase 9A (SWOTAnalysis)
        self.pestel_analysis: Any = None    # Set in Phase 9B (PESTELAnalysis)
        self.wbs_tree: Any = None           # Set in Phase 9C (WBSTree)
        self.charter_data: Optional[dict] = None  # Charter tab data for SWOT extraction
        self.current_file_path: Optional[str] = None
        self._dirty: bool = False
        self._callbacks: List[Callable] = []

    def mark_dirty(self) -> None:
        self._dirty = True
        # Sync BAC between EVM project and Risk Register
        if self.evm_project and self.risk_register:
            self.risk_register.bac = self.evm_project.bac
        for cb in self._callbacks:
            cb()

    def mark_clean(self) -> None:
        self._dirty = False

    def is_dirty(self) -> bool:
        return self._dirty

    def subscribe(self, callback: Callable) -> None:
        self._callbacks.append(callback)

    def reset(self) -> None:
        """Reset to empty state (New Project)."""
        self.evm_project = None
        self.risk_register = None
        self.mc_results = None
        self.swot_analysis = None
        self.pestel_analysis = None
        self.wbs_tree = None
        self.charter_data = None
        self.current_file_path = None
        self._dirty = False
