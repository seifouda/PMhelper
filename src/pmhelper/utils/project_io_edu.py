"""
PMhelper Edu — Combined .pmproj Project I/O.
Saves/loads the full project state as a single JSON file.

File format:
{
    "version": 1,
    "evm_project": { ... },        # EVMProject.to_dict()
    "risk_register": { ... },      # RiskRegister.to_dict()
    "mc_results": { ... } | null,  # MCResults.to_serializable()
    "app_config": { "mode": ..., "currency_symbol": ... }
}
"""

import json
from pathlib import Path
from typing import Optional, Tuple, Any

from pmhelper.core.evm_models_edu import EVMProject
from pmhelper.core.risk_register_edu import RiskRegister

# Monte Carlo results are optional — avoid hard import failure
try:
    from pmhelper.core.monte_carlo_edu import MCResults
    HAS_MC = True
except ImportError:
    HAS_MC = False

SCHEMA_VERSION = 1


def save_full_project(state, filepath: str) -> None:
    """
    Serialise the entire EduProjectState to a .pmproj JSON file.

    Args:
        state: EduProjectState instance
        filepath: target file path (will be overwritten)
    """
    data = {
        "version": SCHEMA_VERSION,
        "evm_project": state.evm_project.to_dict() if state.evm_project else None,
        "risk_register": state.risk_register.to_dict() if state.risk_register else None,
        "mc_results": None,
        "app_config": {
            "mode": getattr(state, "_mode", "UG"),
            "currency_symbol": (
                state.evm_project.currency_symbol
                if state.evm_project else "$"
            ),
        },
        # CPM/PERT activity table — restored on load so user doesn't lose input
        "cpm_activities": getattr(state, "_cpm_activities", []),
        "cpm_mode": getattr(state, "_cpm_mode", "deterministic"),
    }

    # MC results
    if state.mc_results is not None:
        if hasattr(state.mc_results, "to_serializable"):
            data["mc_results"] = state.mc_results.to_serializable()

    path = Path(filepath)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_full_project(filepath: str) -> dict:
    """
    Load a .pmproj file and reconstruct all data model objects.

    Args:
        filepath: path to the .pmproj file

    Returns:
        dict with keys:
            "evm_project": EVMProject | None,
            "risk_register": RiskRegister | None,
            "mc_results": MCResults | None,
            "app_config": dict,
            "version": int,

    Raises:
        FileNotFoundError: if filepath doesn't exist
        ValueError: if file is corrupt or wrong format
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Project file not found: {filepath}")

    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Cannot read project file: {exc}") from exc

    version = data.get("version", 1)

    # Reconstruct EVM project
    evm_project = None
    if data.get("evm_project"):
        evm_project = EVMProject.from_dict(data["evm_project"])

    # Reconstruct risk register
    risk_register = None
    if data.get("risk_register"):
        risk_register = RiskRegister.from_dict(data["risk_register"])

    # Reconstruct MC results (optional)
    mc_results = None
    if data.get("mc_results") and HAS_MC:
        try:
            mc_results = MCResults.from_serializable(data["mc_results"])
        except Exception:
            pass  # MC results are non-critical

    # App config section
    app_config = data.get("app_config", {})

    return {
        "version": version,
        "evm_project": evm_project,
        "risk_register": risk_register,
        "mc_results": mc_results,
        "app_config": app_config,
        # CPM/PERT activities table — re-populate Input tab on load
        "cpm_activities": data.get("cpm_activities", []),
        "cpm_mode": data.get("cpm_mode", "deterministic"),
    }


def make_empty_project() -> Tuple[EVMProject, RiskRegister]:
    """Return a fresh empty project and risk register."""
    proj = EVMProject(project_name="New Project", bac=0.0,
                      bac_auto_compute=False)
    reg = RiskRegister(bac=0.0)
    return proj, reg
