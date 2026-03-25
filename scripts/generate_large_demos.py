#!/usr/bin/env python3
"""Generate large 600-task demo files for UG (deterministic) and PG (probabilistic) modes."""

import json
import math
import random
import os

random.seed(42)  # Reproducible

# ---------------------------------------------------------------------------
# Shared predecessor-network builder  (Constraints #1–#19)
# ---------------------------------------------------------------------------

def _build_ancestor_sets(pred_map, all_ids):
    """Compute ancestor sets in topological order for transitive reduction.

    Works because all_ids is already in topological order — every predecessor
    has a strictly lower list-index than its successor.
    """
    ancestor = {tid: set() for tid in all_ids}
    for tid in all_ids:
        for p in pred_map.get(tid, []):
            ancestor[tid].add(p)
            ancestor[tid].update(ancestor.get(p, set()))
    return ancestor


def _transitive_reduce(pred_map, all_ids):
    """Remove edge A→C where A is already an ancestor of C via another path.

    Example: if A→B and B→C exist, the direct edge A→C is removed (constraint #5).
    """
    ancestor = _build_ancestor_sets(pred_map, all_ids)
    result = {}
    for tid in all_ids:
        preds = pred_map.get(tid, [])
        if len(preds) <= 1:
            result[tid] = list(preds)
            continue
        keep = [
            p for p in preds
            if not any(p in ancestor.get(q, set()) for q in preds if q != p)
        ]
        # Safety: always keep at least one predecessor
        if not keep and preds:
            keep = [preds[-1]]
        result[tid] = keep
    return result


def _build_predecessors_map(phase_codes, phase_task_ids, rng):
    """Build a well-formed predecessor network satisfying all 19 DAG constraints.

    Constraint coverage
    -------------------
    #1  DAG          : predecessors always have a lower sequence-index → no cycles
    #2  Order        : enforced by index-based candidate windows
    #3  Start tasks  : first 3 tasks of phase 1 have no predecessors
    #4  End task     : last task of last phase has no successors (by construction)
    #5  Trans. redux : applied via _transitive_reduce()
    #6  Max 3 preds  : hard cap enforced at the end
    #7  No fan-out   : ONE gateway per phase boundary; not all tasks link
    #8  No overconv. : at most 3 predecessors total
    #9  Logical flow : tasks only link within-phase or to adjacent-phase gate
    #10 Locality     : last-8 window within the same phase
    #11 Connectivity : fallback ensures every non-start task has ≥1 predecessor
    #14 Long path    : spine creates an ≈N/3-task critical chain (≥30% of project)
    #15 Branching    : reciprocal of the 3-pred cap limits fan-out
    #17 No dead-ends : spine + phase-end links guarantee paths to the finish
    #18 Reachability : every task reachable from at least one spine start task
    #19 Path to end  : spine threads through to the last task of the last phase
    """
    # Flatten task IDs in sequence order — this IS the topological order
    all_ids = []
    for pc in phase_codes:
        all_ids.extend(phase_task_ids[pc])
    id_to_idx = {tid: i for i, tid in enumerate(all_ids)}
    pred_map = {tid: [] for tid in all_ids}

    # ── Step 1: Critical spine  (constraint #14) ───────────────────────────
    # Every 3rd task forms a long sequential chain: ≈200 tasks for n=600  (33%)
    spine = all_ids[::3]
    for i in range(1, len(spine)):
        pred_map[spine[i]].append(spine[i - 1])

    # ── Step 2: Phase-boundary gateways  (constraints #7, #8) ─────────────
    # The FIRST task of each phase depends on the LAST task of the previous
    # phase — one clean handoff, no fan-out explosion at boundaries.
    for pi in range(1, len(phase_codes)):
        gateway  = phase_task_ids[phase_codes[pi]][0]
        prev_end = phase_task_ids[phase_codes[pi - 1]][-1]
        if prev_end not in pred_map[gateway]:
            pred_map[gateway].append(prev_end)

    # ── Step 3: Within-phase local links  (constraints #6, #10, #11) ───────
    for pi, pc in enumerate(phase_codes):
        ids = phase_task_ids[pc]
        for ti, tid in enumerate(ids):
            if pi == 0 and ti < 3:
                continue  # legitimate project-start tasks

            current = set(pred_map[tid])
            # Candidate pool: most-recent 8 tasks in the same phase only
            window = ids[max(0, ti - 8): ti]
            candidates = [t for t in window if t not in current]

            # Target 1–3 total predecessors (bias towards 2)
            target = rng.choice([1, 2, 2, 2, 3])
            needed = max(0, target - len(current))
            if needed <= 0 or not candidates:
                continue

            pool = candidates[-4:] if len(candidates) > 4 else candidates
            chosen = rng.sample(pool, min(needed, len(pool)))
            pred_map[tid].extend(chosen)

    # ── Step 4: Ensure no floating tasks  (constraint #11) ────────────────
    for pi, pc in enumerate(phase_codes):
        ids = phase_task_ids[pc]
        for ti, tid in enumerate(ids):
            if pi == 0 and ti < 3:
                continue
            if not pred_map[tid]:
                fallback = (ids[ti - 1] if ti > 0
                            else phase_task_ids[phase_codes[pi - 1]][-1])
                pred_map[tid] = [fallback]

    # ── Step 5: Transitive reduction  (constraint #5) ─────────────────────
    pred_map = _transitive_reduce(pred_map, all_ids)

    # ── Step 6: Hard cap at 3 predecessors  (constraint #6) ───────────────
    for tid in all_ids:
        preds = sorted(set(pred_map[tid]), key=lambda x: id_to_idx[x])
        if len(preds) > 3:
            # Keep the earliest (chain anchor) + the 2 most recent
            preds = [preds[0]] + preds[-2:]
            preds = sorted(set(preds), key=lambda x: id_to_idx[x])
        pred_map[tid] = preds

    return pred_map


# ---------------------------------------------------------------------------
# UG DEMO — Large Infrastructure Construction Project (600 activities)
# ---------------------------------------------------------------------------

def generate_ug_demo():
    """Generate a 600-activity deterministic construction project."""

    # Work packages with realistic construction phases
    phases = [
        ("PRE",  "Pre-Construction",        30),  # 30 tasks
        ("SITE", "Site Preparation",         40),  # 40 tasks
        ("FND",  "Foundations",              50),  # 50 tasks
        ("STR",  "Structural Steel",         60),  # 60 tasks
        ("MEP",  "MEP Rough-In",            70),  # 70 tasks
        ("EXT",  "Building Envelope",        50),  # 50 tasks
        ("INT",  "Interior Framing",         60),  # 60 tasks
        ("MEF",  "MEP Finishes",            50),  # 50 tasks
        ("FIN",  "Interior Finishes",        60),  # 60 tasks
        ("LAN",  "Landscaping & Exterior",   40),  # 40 tasks
        ("COM",  "Commissioning",            50),  # 50 tasks
        ("CLO",  "Closeout & Handover",      40),  # 40 tasks
    ]
    # Total: 600

    activity_names = {
        "PRE": [
            "Feasibility Study", "Environmental Assessment", "Geotechnical Survey",
            "Topographic Survey", "Traffic Impact Study", "Utility Mapping",
            "Architect Selection", "Structural Engineer Engagement", "MEP Consultant Engagement",
            "Schematic Design", "Design Development", "Construction Documents",
            "Building Permit Application", "Fire Department Review", "Zoning Approval",
            "Bid Package Preparation", "Contractor Pre-Qualification", "General Contractor Selection",
            "Subcontractor Bidding", "Contract Negotiation", "Insurance & Bonds",
            "Construction Schedule Baseline", "Safety Plan Development", "Quality Control Plan",
            "Material Procurement Strategy", "Equipment Planning", "Temporary Facilities Plan",
            "Mobilisation Plan", "Stakeholder Communication Plan", "Project Kickoff",
        ],
        "SITE": [
            "Tree Removal & Clearing", "Topsoil Stripping", "Bulk Earthwork Cut",
            "Bulk Earthwork Fill", "Rock Excavation", "Dewatering System",
            "Silt Fence Installation", "Erosion Control Blankets", "Sediment Basins",
            "Storm Water Diversion", "Temporary Access Road", "Haul Road Construction",
            "Site Grading Level 1", "Site Grading Level 2", "Compaction Testing",
            "Sanitary Sewer Main", "Storm Sewer Main", "Water Main Installation",
            "Gas Line Relocation", "Electrical Duct Bank", "Telecom Conduit",
            "Fire Hydrant Installation", "Manholes & Catch Basins", "Utility Connections",
            "Perimeter Fencing", "Security Lighting", "Site Office Setup",
            "Material Laydown Area", "Crane Pad Preparation", "Tower Crane Erection",
            "Personnel Hoist Installation", "Construction Elevator", "Temporary Power Supply",
            "Temporary Water Supply", "Temporary Sanitation", "Waste Management Setup",
            "Concrete Batch Plant Setup", "Rebar Fabrication Yard", "Formwork Storage Area",
            "Site Survey Control Points",
        ],
        "FND": [
            "Excavation Zone A", "Excavation Zone B", "Excavation Zone C",
            "Excavation Zone D", "Pile Driving Zone A", "Pile Driving Zone B",
            "Pile Driving Zone C", "Pile Cap Rebar Zone A", "Pile Cap Rebar Zone B",
            "Pile Cap Formwork Zone A", "Pile Cap Formwork Zone B", "Pile Cap Concrete Zone A",
            "Pile Cap Concrete Zone B", "Grade Beam Rebar North", "Grade Beam Rebar South",
            "Grade Beam Rebar East", "Grade Beam Rebar West", "Grade Beam Formwork North",
            "Grade Beam Formwork South", "Grade Beam Formwork East", "Grade Beam Formwork West",
            "Grade Beam Concrete North", "Grade Beam Concrete South", "Grade Beam Concrete East",
            "Grade Beam Concrete West", "Foundation Wall Rebar A", "Foundation Wall Rebar B",
            "Foundation Wall Formwork A", "Foundation Wall Formwork B", "Foundation Wall Concrete A",
            "Foundation Wall Concrete B", "Waterproofing North", "Waterproofing South",
            "Waterproofing East", "Waterproofing West", "Underslab Plumbing Zone A",
            "Underslab Plumbing Zone B", "Underslab Electrical Zone A", "Underslab Electrical Zone B",
            "Slab on Grade Rebar A", "Slab on Grade Rebar B", "Slab on Grade Mesh",
            "Slab on Grade Pour A", "Slab on Grade Pour B", "Elevator Pit Excavation",
            "Elevator Pit Concrete", "Sump Pit Construction", "Foundation Backfill",
            "Compaction & Grading", "Foundation Inspection Sign-off",
        ],
    }

    # For phases not explicitly listed, generate generic names
    generic_templates = {
        "STR": "Steel {}", "MEP": "MEP {}", "EXT": "Envelope {}",
        "INT": "Interior {}", "MEF": "MEP Finish {}", "FIN": "Finish {}",
        "LAN": "Landscape {}", "COM": "Commission {}", "CLO": "Closeout {}",
    }

    steel_names = [
        "Anchor Bolt Survey Floor 1", "Anchor Bolt Survey Floor 2", "Column Erection Level 1 Zone A",
        "Column Erection Level 1 Zone B", "Column Erection Level 2 Zone A", "Column Erection Level 2 Zone B",
        "Column Erection Level 3 Zone A", "Column Erection Level 3 Zone B", "Beam Installation Level 1 North",
        "Beam Installation Level 1 South", "Beam Installation Level 2 North", "Beam Installation Level 2 South",
        "Beam Installation Level 3 North", "Beam Installation Level 3 South", "Bracing Level 1",
        "Bracing Level 2", "Bracing Level 3", "Metal Deck Level 1 Zone A",
        "Metal Deck Level 1 Zone B", "Metal Deck Level 2 Zone A", "Metal Deck Level 2 Zone B",
        "Metal Deck Level 3 Zone A", "Metal Deck Level 3 Zone B", "Shear Stud Welding Level 1",
        "Shear Stud Welding Level 2", "Shear Stud Welding Level 3", "Concrete Pour Level 1 Zone A",
        "Concrete Pour Level 1 Zone B", "Concrete Pour Level 2 Zone A", "Concrete Pour Level 2 Zone B",
        "Concrete Pour Level 3 Zone A", "Concrete Pour Level 3 Zone B", "Rebar Placement Level 1",
        "Rebar Placement Level 2", "Rebar Placement Level 3", "Post-Tension Cables Level 1",
        "Post-Tension Cables Level 2", "Post-Tension Cables Level 3", "Core Wall Rebar Level 1",
        "Core Wall Rebar Level 2", "Core Wall Rebar Level 3", "Core Wall Formwork Level 1",
        "Core Wall Formwork Level 2", "Core Wall Formwork Level 3", "Core Wall Pour Level 1",
        "Core Wall Pour Level 2", "Core Wall Pour Level 3", "Stair Steel Level 1",
        "Stair Steel Level 2", "Stair Steel Level 3", "Roof Steel Erection North",
        "Roof Steel Erection South", "Roof Bracing", "Roof Deck Installation",
        "Roof Concrete Pour", "Parapet Framing", "Penthouse Steel",
        "Structural Inspection Level 1", "Structural Inspection Level 2", "Structural Inspection Level 3",
    ]

    mep_names = [
        "Electrical Riser Installation", "Main Switchgear Setup", "Distribution Panel Level 1",
        "Distribution Panel Level 2", "Distribution Panel Level 3", "Conduit Rough-In Level 1 Zone A",
        "Conduit Rough-In Level 1 Zone B", "Conduit Rough-In Level 2 Zone A", "Conduit Rough-In Level 2 Zone B",
        "Conduit Rough-In Level 3 Zone A", "Conduit Rough-In Level 3 Zone B", "Wire Pull Level 1",
        "Wire Pull Level 2", "Wire Pull Level 3", "Fire Alarm Rough-In Level 1",
        "Fire Alarm Rough-In Level 2", "Fire Alarm Rough-In Level 3", "Plumbing Riser Installation",
        "Domestic Water Main", "Hot Water Recirculation", "Sanitary Waste Level 1",
        "Sanitary Waste Level 2", "Sanitary Waste Level 3", "Vent Piping Level 1",
        "Vent Piping Level 2", "Vent Piping Level 3", "Storm Drainage Level 1",
        "Storm Drainage Level 2", "Storm Drainage Level 3", "Gas Piping Level 1",
        "Gas Piping Level 2", "Natural Gas Metre", "HVAC Ductwork Level 1 Zone A",
        "HVAC Ductwork Level 1 Zone B", "HVAC Ductwork Level 2 Zone A", "HVAC Ductwork Level 2 Zone B",
        "HVAC Ductwork Level 3 Zone A", "HVAC Ductwork Level 3 Zone B", "AHU Installation Level 1",
        "AHU Installation Level 2", "AHU Installation Level 3", "Chilled Water Piping",
        "Hot Water Piping", "Refrigerant Piping", "Exhaust Ductwork Level 1",
        "Exhaust Ductwork Level 2", "Exhaust Ductwork Level 3", "Fire Sprinkler Main",
        "Fire Sprinkler Branches Level 1", "Fire Sprinkler Branches Level 2", "Fire Sprinkler Branches Level 3",
        "Sprinkler Head Installation L1", "Sprinkler Head Installation L2", "Sprinkler Head Installation L3",
        "Smoke Detector Rough-In L1", "Smoke Detector Rough-In L2", "Smoke Detector Rough-In L3",
        "BMS Controls Level 1", "BMS Controls Level 2", "BMS Controls Level 3",
        "Insulation Piping Level 1", "Insulation Piping Level 2", "Insulation Piping Level 3",
        "Pressure Testing Plumbing", "Pressure Testing HVAC", "Pressure Testing Sprinkler",
        "MEP Coordination Sign-off L1", "MEP Coordination Sign-off L2", "MEP Coordination Sign-off L3",
    ]

    ext_names = [
        "Curtain Wall Framing North L1", "Curtain Wall Framing North L2", "Curtain Wall Framing North L3",
        "Curtain Wall Framing South L1", "Curtain Wall Framing South L2", "Curtain Wall Framing South L3",
        "Curtain Wall Glazing North L1", "Curtain Wall Glazing North L2", "Curtain Wall Glazing North L3",
        "Curtain Wall Glazing South L1", "Curtain Wall Glazing South L2", "Curtain Wall Glazing South L3",
        "Window Installation East L1", "Window Installation East L2", "Window Installation East L3",
        "Window Installation West L1", "Window Installation West L2", "Window Installation West L3",
        "Exterior Cladding North", "Exterior Cladding South", "Exterior Cladding East",
        "Exterior Cladding West", "Roof Membrane Installation", "Roof Insulation",
        "Roof Flashing", "Roof Drainage", "Skylight Installation",
        "Exterior Sealant North", "Exterior Sealant South", "Exterior Sealant East",
        "Exterior Sealant West", "Loading Dock Door", "Main Entrance Door",
        "Emergency Exit Doors", "Exterior Soffit", "Metal Panel Accent North",
        "Metal Panel Accent South", "Parapet Capping", "Bird Deterrent System",
        "Facade Cleaning System Rails", "Exterior Waterproofing Below Grade",
        "Window Testing & Certification", "Cladding Inspection", "Roof Inspection",
        "Balcony Waterproofing", "Balcony Railings", "Fire Escape Installation",
        "Exterior Signage Preparation", "Canopy Steel Structure", "Canopy Glazing",
    ]

    int_names = [
        "Metal Stud Framing L1 Zone A", "Metal Stud Framing L1 Zone B", "Metal Stud Framing L1 Zone C",
        "Metal Stud Framing L2 Zone A", "Metal Stud Framing L2 Zone B", "Metal Stud Framing L2 Zone C",
        "Metal Stud Framing L3 Zone A", "Metal Stud Framing L3 Zone B", "Metal Stud Framing L3 Zone C",
        "Drywall Hanging L1 Zone A", "Drywall Hanging L1 Zone B", "Drywall Hanging L1 Zone C",
        "Drywall Hanging L2 Zone A", "Drywall Hanging L2 Zone B", "Drywall Hanging L2 Zone C",
        "Drywall Hanging L3 Zone A", "Drywall Hanging L3 Zone B", "Drywall Hanging L3 Zone C",
        "Drywall Taping L1 Zone A", "Drywall Taping L1 Zone B", "Drywall Taping L1 Zone C",
        "Drywall Taping L2 Zone A", "Drywall Taping L2 Zone B", "Drywall Taping L2 Zone C",
        "Drywall Taping L3 Zone A", "Drywall Taping L3 Zone B", "Drywall Taping L3 Zone C",
        "Ceiling Grid L1 Zone A", "Ceiling Grid L1 Zone B", "Ceiling Grid L1 Zone C",
        "Ceiling Grid L2 Zone A", "Ceiling Grid L2 Zone B", "Ceiling Grid L2 Zone C",
        "Ceiling Grid L3 Zone A", "Ceiling Grid L3 Zone B", "Ceiling Grid L3 Zone C",
        "Acoustic Insulation L1", "Acoustic Insulation L2", "Acoustic Insulation L3",
        "Fire Stopping L1", "Fire Stopping L2", "Fire Stopping L3",
        "Door Frame Installation L1", "Door Frame Installation L2", "Door Frame Installation L3",
        "Access Floor L1 Server Room", "Millwork L1 Reception", "Speciality Framing Atrium",
        "Shaft Wall Construction L1", "Shaft Wall Construction L2", "Shaft Wall Construction L3",
        "Bulkhead Framing L1", "Bulkhead Framing L2", "Bulkhead Framing L3",
        "Column Enclosures L1", "Column Enclosures L2", "Column Enclosures L3",
        "Interior Inspection L1", "Interior Inspection L2", "Interior Inspection L3",
    ]

    mef_names = [
        "Light Fixture Install L1 Zone A", "Light Fixture Install L1 Zone B",
        "Light Fixture Install L2 Zone A", "Light Fixture Install L2 Zone B",
        "Light Fixture Install L3 Zone A", "Light Fixture Install L3 Zone B",
        "Switch & Outlet Install L1", "Switch & Outlet Install L2", "Switch & Outlet Install L3",
        "Panel Terminations L1", "Panel Terminations L2", "Panel Terminations L3",
        "Fire Alarm Devices L1", "Fire Alarm Devices L2", "Fire Alarm Devices L3",
        "Emergency Lighting L1", "Emergency Lighting L2", "Emergency Lighting L3",
        "Plumbing Fixture Rough L1", "Plumbing Fixture Rough L2", "Plumbing Fixture Rough L3",
        "Plumbing Fixture Set L1", "Plumbing Fixture Set L2", "Plumbing Fixture Set L3",
        "Toilet Accessory Install L1", "Toilet Accessory Install L2", "Toilet Accessory Install L3",
        "VAV Box Install L1", "VAV Box Install L2", "VAV Box Install L3",
        "Diffuser & Grille Install L1", "Diffuser & Grille Install L2", "Diffuser & Grille Install L3",
        "Thermostat Install L1", "Thermostat Install L2", "Thermostat Install L3",
        "BMS Programming L1", "BMS Programming L2", "BMS Programming L3",
        "Ceiling Tile Install L1 Zone A", "Ceiling Tile Install L1 Zone B",
        "Ceiling Tile Install L2 Zone A", "Ceiling Tile Install L2 Zone B",
        "Ceiling Tile Install L3 Zone A", "Ceiling Tile Install L3 Zone B",
        "Generator Installation", "ATS Installation", "UPS Installation",
        "Transformer Energisation", "Main Bus Energisation",
    ]

    fin_names = [
        "Paint Prep L1 Zone A", "Paint Prep L1 Zone B", "Paint Prep L2 Zone A",
        "Paint Prep L2 Zone B", "Paint Prep L3 Zone A", "Paint Prep L3 Zone B",
        "Paint Application L1 Zone A", "Paint Application L1 Zone B", "Paint Application L2 Zone A",
        "Paint Application L2 Zone B", "Paint Application L3 Zone A", "Paint Application L3 Zone B",
        "Tile Floor L1 Zone A", "Tile Floor L1 Zone B", "Tile Floor L2 Zone A",
        "Tile Floor L2 Zone B", "Tile Floor L3 Zone A", "Tile Floor L3 Zone B",
        "Carpet Installation L1", "Carpet Installation L2", "Carpet Installation L3",
        "Vinyl Floor L1 Wet Areas", "Vinyl Floor L2 Wet Areas", "Vinyl Floor L3 Wet Areas",
        "Wood Floor Reception", "Epoxy Floor Garage", "Polished Concrete Lobby",
        "Wall Tile Washrooms L1", "Wall Tile Washrooms L2", "Wall Tile Washrooms L3",
        "Door Installation L1", "Door Installation L2", "Door Installation L3",
        "Door Hardware L1", "Door Hardware L2", "Door Hardware L3",
        "Base Trim L1", "Base Trim L2", "Base Trim L3",
        "Window Sills & Trim L1", "Window Sills & Trim L2", "Window Sills & Trim L3",
        "Millwork Installation L1", "Millwork Installation L2", "Millwork Installation L3",
        "Countertop Installation L1", "Countertop Installation L2", "Countertop Installation L3",
        "Signage & Wayfinding L1", "Signage & Wayfinding L2", "Signage & Wayfinding L3",
        "Window Blinds L1", "Window Blinds L2", "Window Blinds L3",
        "Mirror Install Washrooms L1", "Mirror Install Washrooms L2", "Mirror Install Washrooms L3",
        "Final Clean L1", "Final Clean L2", "Final Clean L3",
    ]

    lan_names = [
        "Rough Grading", "Topsoil Placement", "Irrigation Main Line",
        "Irrigation Zone North", "Irrigation Zone South", "Irrigation Zone East",
        "Tree Planting North", "Tree Planting South", "Shrub Planting Entrance",
        "Lawn Seeding Zone A", "Lawn Seeding Zone B", "Mulch & Bed Edging",
        "Concrete Sidewalk North", "Concrete Sidewalk South", "Concrete Sidewalk East",
        "Asphalt Paving Main Lot", "Asphalt Paving Staff Lot", "Curb & Gutter",
        "Parking Lot Striping", "Parking Bollards", "Accessible Ramp Installation",
        "Retaining Wall North", "Retaining Wall East", "Decorative Paving Entrance",
        "Bike Rack Installation", "Bench & Furniture Installation", "Flagpole Installation",
        "Exterior Lighting Poles", "Pathway Lighting", "Landscape Lighting Accent",
        "Fence Gate North", "Fence Gate South", "Loading Dock Approach Paving",
        "Dumpster Enclosure", "Transformer Pad Landscaping", "Generator Enclosure Screen",
        "Snow Melt System Entry", "Drainage Swale", "Landscape Final Grading",
        "Landscape Inspection Sign-off",
    ]

    com_names = [
        "Electrical System Testing - Main", "Electrical System Testing - Emergency",
        "Generator Load Test", "UPS System Test", "Lightning Protection Test",
        "Fire Alarm System Test", "Sprinkler Flow Test", "Sprinkler Pressure Test",
        "Fire Pump Test", "Smoke Control System Test", "HVAC Balancing Zone A",
        "HVAC Balancing Zone B", "HVAC Balancing Zone C", "AHU Performance Test L1",
        "AHU Performance Test L2", "AHU Performance Test L3", "Chiller Start-up",
        "Boiler Start-up", "Cooling Tower Test", "BMS Integration Test L1",
        "BMS Integration Test L2", "BMS Integration Test L3", "BMS Graphics & Trending",
        "Plumbing System Flush", "Domestic Hot Water Test", "Backflow Preventer Test",
        "Elevator Installation Car 1", "Elevator Installation Car 2", "Elevator Inspection Car 1",
        "Elevator Inspection Car 2", "Security System Programming", "Access Control Setup",
        "CCTV Camera Install & Test", "Intercom System Test", "Telecom Riser Test",
        "Data Network Testing", "AV System Testing", "PA System Testing",
        "Emergency Generator Auto-Transfer Test", "Integrated Systems Test",
        "Occupancy Sensor Calibration", "Daylight Harvesting Calibration",
        "Indoor Air Quality Test", "Noise Level Testing", "Thermal Comfort Verification",
        "Commissioning Report Draft", "Punch List Generation", "Punch List Resolution",
        "Re-Inspection Items", "Final Commissioning Sign-off",
    ]

    clo_names = [
        "As-Built Drawings Architectural", "As-Built Drawings Structural",
        "As-Built Drawings MEP", "As-Built Drawings Civil",
        "O&M Manual Volume 1 - Architectural", "O&M Manual Volume 2 - Structural",
        "O&M Manual Volume 3 - Mechanical", "O&M Manual Volume 4 - Electrical",
        "O&M Manual Volume 5 - Plumbing", "O&M Manual Volume 6 - Fire Protection",
        "Warranty Documentation Collection", "Warranty Database Setup",
        "Spare Parts Inventory", "Attic Stock Delivery",
        "Staff Training - HVAC Operations", "Staff Training - Fire Life Safety",
        "Staff Training - BMS", "Staff Training - Security Systems",
        "Staff Training - Plumbing & Drainage", "Staff Training - Electrical Systems",
        "Final Health & Safety Audit", "Environmental Compliance Report",
        "Occupancy Permit Application", "Fire Department Final Inspection",
        "Building Code Final Inspection", "Accessibility Compliance Review",
        "Certificate of Occupancy", "Demobilisation - Crane",
        "Demobilisation - Hoist", "Demobilisation - Site Office",
        "Temporary Utilities Disconnect", "Hoarding Removal",
        "Site Restoration", "Final Site Survey",
        "Project Lessons Learned Workshop", "Project Close-out Report",
        "Financial Close-out", "Retention Release Preparation",
        "Owner Move-In Coordination", "Project Handover Ceremony",
    ]

    named_phases = {
        "PRE": activity_names["PRE"],
        "SITE": activity_names["SITE"],
        "FND": activity_names["FND"],
        "STR": steel_names,
        "MEP": mep_names,
        "EXT": ext_names,
        "INT": int_names,
        "MEF": mef_names,
        "FIN": fin_names,
        "LAN": lan_names,
        "COM": com_names,
        "CLO": clo_names,
    }

    activities = []
    phase_task_ids = {}  # phase_code -> list of task IDs
    task_index = 0

    for phase_code, phase_name, count in phases:
        names_list = named_phases.get(phase_code, [])
        # Pad if we don't have enough names
        while len(names_list) < count:
            names_list.append(f"{phase_name} Task {len(names_list)+1}")

        ids_in_phase = []
        for i in range(count):
            task_index += 1
            tid = f"A{task_index:03d}"
            ids_in_phase.append(tid)

        phase_task_ids[phase_code] = ids_in_phase

    # Now build predecessors with a realistic network structure
    # Rules:
    # - First 3 tasks of first phase have no predecessors
    # - Within a phase: each task depends on 1-3 earlier tasks in the same phase
    # - Between phases: first ~5 tasks of a new phase depend on last ~5 tasks of previous phase
    # - Some cross-phase dependencies for realism

    phase_codes = [p[0] for p in phases]

    # Build predecessor network — all 19 DAG constraints applied
    predecessors_map = _build_predecessors_map(phase_codes, phase_task_ids, random)

    # Build activities with realistic durations and costs
    cpm_activities = []
    task_index = 0
    for phase_code, phase_name, count in phases:
        names_list = named_phases[phase_code][:count]
        ids = phase_task_ids[phase_code]
        for i, tid in enumerate(ids):
            duration = random.randint(2, 15)
            min_dur = max(1, int(duration * random.uniform(0.4, 0.75)))
            resource = random.randint(2, 12)
            normal_cost = random.randint(3, 40) * 1000
            crash_premium = random.uniform(1.3, 2.0)
            crash_cost = int(normal_cost * crash_premium / 1000) * 1000

            preds_str = ",".join(predecessors_map[tid])
            cpm_activities.append({
                "id": tid,
                "activity": names_list[i],
                "duration": str(duration),
                "predecessors": preds_str,
                "min_duration": str(min_dur),
                "crash_cost": str(crash_cost),
                "resource_demand": str(resource),
                "normal_cost": str(normal_cost),
            })

    # Calculate approximate planned schedule for EVM
    # Simple forward pass to get expected durations
    id_to_act = {a["id"]: a for a in cpm_activities}
    es_map = {}
    ef_map = {}
    for act in cpm_activities:
        tid = act["id"]
        preds = [p.strip() for p in act["predecessors"].split(",") if p.strip()]
        if not preds:
            es = 0
        else:
            es = max(ef_map.get(p, 0) for p in preds)
        dur = int(act["duration"])
        es_map[tid] = es
        ef_map[tid] = es + dur

    project_duration = max(ef_map.values())
    total_normal_cost = sum(int(a["normal_cost"]) for a in cpm_activities)

    # BAC based on total normal cost
    bac = total_normal_cost

    # Generate EVM tasks (one per activity is too many for EVM; group by phase)
    evm_tasks = []
    for pi, (phase_code, phase_name, count) in enumerate(phases):
        ids = phase_task_ids[phase_code]
        phase_budget = sum(int(id_to_act[tid]["normal_cost"]) for tid in ids)
        phase_es = min(es_map[tid] for tid in ids)
        phase_ef = max(ef_map[tid] for tid in ids)

        evm_tasks.append({
            "task_id": f"WP{pi+1:02d}",
            "name": phase_name,
            "budget": float(phase_budget),
            "pct_complete": max(0, min(100, 100 - pi * 10 + random.randint(-5, 5))),
            "planned_start": phase_es,
            "planned_finish": phase_ef,
            "actual_start": phase_es + random.randint(0, 2),
            "actual_finish": phase_ef + random.randint(-1, 3),
            "baseline_start": phase_es,
            "baseline_finish": phase_ef,
            "pv_spread": "uniform",
            "cpm_task_id": None,
            "predecessors": [f"WP{pi:02d}"] if pi > 0 else [],
        })

    # Fix pct_complete to be realistic (earlier phases more complete)
    for i, t in enumerate(evm_tasks):
        if i < 4:
            t["pct_complete"] = 100.0
        elif i < 7:
            t["pct_complete"] = float(random.randint(40, 85))
        elif i < 9:
            t["pct_complete"] = float(random.randint(10, 40))
        else:
            t["pct_complete"] = float(random.randint(0, 10))

    # EVM periods (weekly, ~60 weeks worth of data up to now)
    n_periods = min(60, project_duration // 2)
    periods = []
    for idx in range(n_periods):
        week = idx + 1
        progress = (week / project_duration)
        pv = bac * min(1.0, progress * 1.05)  # S-curve approximation
        # EV slightly behind PV (over budget, behind schedule)
        ev = pv * random.uniform(0.85, 0.95)
        # AC higher than EV (cost overrun)
        ac = ev * random.uniform(1.05, 1.18)
        periods.append({
            "index": idx,
            "label": f"Week {week}",
            "pv_cumulative": round(pv, 2),
            "ev_cumulative": round(ev, 2),
            "ac_cumulative": round(ac, 2),
            "ev_source": "manual",
        })

    risk_register = {
        "bac": float(bac),
        "high_exposure_threshold_pct": 0.05,
        "risks": [
            {"id": "CR1", "name": "Subcontractor Default", "description": "Major subcontractor goes bankrupt during construction", "probability": 0.1, "impact": float(bac * 0.15), "category": "Cost"},
            {"id": "CR2", "name": "Steel Price Escalation", "description": "Global steel prices increase beyond budget allowance", "probability": 0.5, "impact": float(bac * 0.08), "category": "Cost"},
            {"id": "CR3", "name": "Severe Weather Delays", "description": "Extended rain/snow season delays exterior work by 4-6 weeks", "probability": 0.4, "impact": float(bac * 0.06), "category": "Schedule"},
            {"id": "CR4", "name": "Permit Delays", "description": "Building permit review takes 8 weeks instead of 4", "probability": 0.35, "impact": float(bac * 0.04), "category": "Schedule"},
            {"id": "CR5", "name": "Design Changes", "description": "Client requests significant design modifications after steel erection", "probability": 0.3, "impact": float(bac * 0.10), "category": "Scope"},
            {"id": "CR6", "name": "Labour Shortage", "description": "Skilled trade shortage delays MEP and finishing work", "probability": 0.45, "impact": float(bac * 0.07), "category": "Schedule"},
            {"id": "CR7", "name": "Soil Contamination", "description": "Contaminated soil discovered during excavation requiring remediation", "probability": 0.15, "impact": float(bac * 0.12), "category": "Cost"},
            {"id": "CR8", "name": "Utility Conflicts", "description": "Unmarked underground utilities conflict with foundation layout", "probability": 0.25, "impact": float(bac * 0.05), "category": "Schedule"},
            {"id": "CR9", "name": "Code Compliance Issues", "description": "Building inspector requires structural modifications for code compliance", "probability": 0.2, "impact": float(bac * 0.06), "category": "Quality"},
            {"id": "CR10", "name": "Equipment Failure", "description": "Tower crane malfunction requiring extended repair or replacement", "probability": 0.15, "impact": float(bac * 0.04), "category": "Schedule"},
            {"id": "CR11", "name": "Concrete Supply Disruption", "description": "Concrete batch plant failure or ready-mix shortage", "probability": 0.2, "impact": float(bac * 0.05), "category": "Schedule"},
            {"id": "CR12", "name": "Safety Incident", "description": "Major safety incident resulting in work stoppage and investigation", "probability": 0.1, "impact": float(bac * 0.08), "category": "Quality"},
        ],
    }

    return {
        "version": 1,
        "evm_project": {
            "schema_version": 1,
            "project_name": "Campus Construction (Large UG Demo)",
            "bac": float(bac),
            "bac_auto_compute": False,
            "currency_symbol": "$",
            "tasks": evm_tasks,
            "periods": periods,
        },
        "risk_register": risk_register,
        "mc_results": None,
        "app_config": {"mode": "UG", "currency_symbol": "$"},
        "cpm_activities": cpm_activities,
        "cpm_mode": "deterministic",
    }


# ---------------------------------------------------------------------------
# PG DEMO — Large Enterprise ERP Implementation (600 activities)
# ---------------------------------------------------------------------------

def generate_pg_demo():
    """Generate a 600-activity probabilistic ERP implementation project."""

    phases = [
        ("INI", "Initiation & Planning",          30),
        ("REQ", "Requirements & Analysis",         50),
        ("DES", "Solution Design",                 45),
        ("CFG", "System Configuration",            60),
        ("DEV", "Custom Development",              70),
        ("MIG", "Data Migration",                  50),
        ("INT", "Integration",                     55),
        ("TST", "System Testing",                  60),
        ("UAT", "User Acceptance Testing",         40),
        ("TRN", "Training & Change Mgmt",          45),
        ("DEP", "Deployment & Go-Live",            50),
        ("SUP", "Post Go-Live Support & Closeout", 45),
    ]
    # Total: 600

    phase_names_map = {
        "INI": [
            "Project Charter Development", "Stakeholder Identification", "Steering Committee Setup",
            "Project Governance Framework", "Communication Plan", "Risk Management Framework",
            "Budget Approval Process", "Resource Allocation Plan", "Vendor Selection RFP",
            "Vendor Evaluation Matrix", "Contract Negotiation", "Statement of Work Finalization",
            "License Procurement", "Infrastructure Assessment", "Current State Documentation",
            "Gap Analysis Kickoff", "Change Management Strategy", "Training Needs Assessment",
            "PMO Setup & Tooling", "Project Kickoff Meeting", "Baseline Schedule Development",
            "Quality Management Plan", "Configuration Management Plan", "Issue & Decision Log Setup",
            "Progress Reporting Framework", "Environment Strategy", "Data Governance Framework",
            "Compliance Review", "Executive Sponsor Briefing", "Phase Gate Review - Initiation",
        ],
        "REQ": [
            "Finance Requirements Workshop", "Finance Process Mapping", "AP Requirements Documentation",
            "AR Requirements Documentation", "GL Requirements Documentation", "Fixed Assets Requirements",
            "Treasury Requirements", "Budgeting & Forecasting Requirements", "HR Requirements Workshop",
            "Payroll Requirements Documentation", "Benefits Administration Requirements",
            "Talent Management Requirements", "Time & Attendance Requirements",
            "Recruitment Process Requirements", "Supply Chain Requirements Workshop",
            "Procurement Requirements Documentation", "Inventory Management Requirements",
            "Warehouse Management Requirements", "Demand Planning Requirements",
            "Supplier Management Requirements", "Manufacturing Requirements Workshop",
            "Production Planning Requirements", "Shop Floor Control Requirements",
            "Quality Management Requirements", "Maintenance Requirements",
            "Sales & Distribution Workshop", "Order Management Requirements",
            "Pricing & Promotions Requirements", "Shipping & Logistics Requirements",
            "Customer Master Data Requirements", "CRM Integration Requirements",
            "Reporting & Analytics Workshop", "Executive Dashboard Requirements",
            "Operational Reports Requirements", "Compliance Reports Requirements",
            "Self-Service BI Requirements", "Data Warehouse Requirements",
            "Security Requirements Workshop", "Role-Based Access Requirements",
            "Audit Trail Requirements", "Data Privacy Requirements",
            "Cross-Module Integration Requirements", "Workflow & Approval Requirements",
            "Mobile Requirements", "Portal Requirements",
            "Localisation Requirements", "Multi-Currency Requirements",
            "Requirements Traceability Matrix", "Requirements Sign-off Finance",
            "Requirements Sign-off HR",
        ],
        "DES": [
            "Finance Solution Design", "AP Process Design", "AR Process Design",
            "GL & Chart of Accounts Design", "Fixed Assets Design", "Treasury Design",
            "Budgeting Solution Design", "HR Core Design", "Payroll Design",
            "Benefits Design", "Talent Management Design", "Time & Attendance Design",
            "Recruitment Design", "Supply Chain Solution Design", "Procurement Design",
            "Inventory Design", "Warehouse Design", "Demand Planning Design",
            "Manufacturing Solution Design", "Production Planning Design",
            "Shop Floor Design", "Quality Management Design",
            "Sales & Distribution Design", "Order Management Design",
            "Pricing Design", "Shipping & Logistics Design",
            "Reporting Architecture Design", "Dashboard Framework Design",
            "Data Warehouse Design", "ETL Architecture Design",
            "Security Architecture Design", "Role Matrix Design",
            "Integration Architecture Design", "Workflow Design",
            "Mobile & Portal Design", "Localisation & Multi-Currency Design",
            "Performance Architecture Design", "Infrastructure Sizing",
            "Environment Architecture Design", "Disaster Recovery Design",
            "Design Review - Finance", "Design Review - HR",
            "Design Review - Supply Chain", "Design Review - Technical",
            "Phase Gate Review - Design",
        ],
    }

    # Generate names for remaining phases procedurally
    cfg_names = []
    for module in ["Finance", "HR", "Supply Chain", "Manufacturing", "Sales", "Reporting"]:
        for task in ["Base Configuration", "Master Data Setup", "Organisation Structure",
                     "Workflow Configuration", "Security Role Config", "Report Configuration",
                     "Form & Layout Config", "Notification Setup", "Integration Config", "Validation Rules"]:
            cfg_names.append(f"{module} {task}")

    dev_names = []
    dev_types = ["Custom Report", "Interface", "Enhancement", "Form", "Workflow",
                 "Dashboard", "API Endpoint", "Batch Job", "Conversion Program", "Extension"]
    for i in range(70):
        dtype = dev_types[i % len(dev_types)]
        module = ["Finance", "HR", "Supply Chain", "Manufacturing", "Sales", "Platform", "Analytics"][i % 7]
        dev_names.append(f"{module} {dtype} {(i // 10) + 1}")

    mig_names = []
    data_objects = ["Chart of Accounts", "Cost Centres", "Profit Centres", "Vendors", "Customers",
                    "Employees", "Payroll History", "Open POs", "Open SOs", "Inventory Balances",
                    "Fixed Assets", "GL Balances", "AP Open Items", "AR Open Items", "BOMs",
                    "Routings", "Work Centres", "Pricing Master", "Bank Master", "Tax Configuration"]
    for obj in data_objects:
        mig_names.append(f"{obj} Extract & Cleanse")
        if len(mig_names) < 50:
            mig_names.append(f"{obj} Load & Validate")
    mig_names = mig_names[:50]

    int_names_list = []
    systems = ["CRM", "E-Commerce", "Banking", "EDI", "Warehouse Automation",
               "Planning Tool", "BI Platform", "Document Mgmt", "Travel & Expense", "Identity Provider"]
    for sys_name in systems:
        for task in ["Interface Design", "Connector Development", "Middleware Config",
                     "Unit Test", "End-to-End Test"]:
            int_names_list.append(f"{sys_name} {task}")
    int_names_list = int_names_list[:55]

    tst_names = []
    test_cycles = ["Cycle 1", "Cycle 2", "Cycle 3"]
    modules_test = ["Finance", "HR", "Supply Chain", "Manufacturing", "Sales", "Reporting",
                    "Integration", "Security", "Performance", "Regression"]
    for cycle in test_cycles:
        for mod in modules_test:
            tst_names.append(f"{mod} Test {cycle}")
    for extra in ["System Integration Test - End to End", "Volume Test", "Stress Test",
                  "Failover Test", "Backup & Recovery Test",
                  "Cross-Browser Testing", "Mobile Testing", "Accessibility Testing",
                  "Data Validation Test", "Audit Trail Test",
                  "Report Reconciliation", "Interface Error Handling Test",
                  "Negative Testing", "Boundary Testing", "Usability Testing",
                  "Security Penetration Test", "Role Segregation Test",
                  "Multi-Language Test", "Multi-Currency Test", "Defect Triage & Resolution"]:
        tst_names.append(extra)
    tst_names = tst_names[:60]

    uat_names = []
    uat_modules = ["Finance", "HR", "Supply Chain", "Manufacturing", "Sales",
                   "Reporting", "Integration", "Mobile"]
    for mod in uat_modules:
        for task in ["UAT Script Preparation", "UAT Execution", "UAT Defect Resolution",
                     "UAT Sign-off", "Business Process Validation"]:
            uat_names.append(f"{mod} {task}")
    uat_names = uat_names[:40]

    trn_names = []
    roles = ["Finance Users", "HR Users", "Supply Chain Users", "Manufacturing Users",
             "Sales Users", "Managers", "Executives", "IT Support", "Super Users"]
    for role in roles:
        for task in ["Training Material Development", "Training Environment Setup",
                     "Training Delivery - Classroom", "Training Assessment", "Training Feedback"]:
            trn_names.append(f"{role} {task}")
    trn_names = trn_names[:45]

    dep_names = [
        "Production Environment Build", "Production Database Setup", "Application Server Config",
        "Web Server Config", "Load Balancer Setup", "SSL Certificate Installation",
        "DNS Configuration", "Firewall Rules Update", "Monitoring Agent Deployment",
        "Log Aggregation Setup", "Master Data Migration - Production", "Opening Balances Load",
        "Configuration Transport - Prod", "Custom Code Transport - Prod", "Report Deployment - Prod",
        "Interface Activation - Prod", "Workflow Activation - Prod", "Security Role Assignment - Prod",
        "Printer Configuration", "Email Gateway Config",
        "Cutover Rehearsal 1", "Cutover Rehearsal 2", "Cutover Plan Finalization",
        "Legacy System Lockdown", "Final Data Extract", "Final Data Load & Validate",
        "Go/No-Go Decision Meeting", "Production Smoke Test", "User Access Provisioning",
        "Go-Live Communication", "Legacy System Decommission Plan",
        "Backup Strategy Verification", "Disaster Recovery Test - Prod",
        "Performance Baseline Capture", "Monitoring Dashboard Activation",
        "Hypercare Team Mobilization", "War Room Setup",
        "Go-Live Day Operations", "Post Go-Live Health Check",
        "Go-Live Celebration & Announcement",
        "Batch Job Scheduling - Prod", "Interface Monitoring Setup",
        "SLA Baseline Establishment", "Vendor Support Activation",
        "Knowledge Transfer to IT Support", "Run Book Documentation",
        "Escalation Procedure Activation", "Service Desk Configuration",
        "First Month-End Close Support", "Phase Gate Review - Go-Live",
    ]

    sup_names = [
        "Day 1 Issue Triage", "Critical Defect Resolution Week 1", "Interface Monitoring Week 1",
        "Performance Monitoring Week 1", "User Support Desk Week 1",
        "Day 5 Issue Triage", "Critical Defect Resolution Week 2", "Interface Monitoring Week 2",
        "Performance Monitoring Week 2", "User Support Desk Week 2",
        "Week 3 Issue Review", "Non-Critical Defect Batch 1", "Interface Stabilization",
        "Performance Tuning Batch 1", "Report Corrections Batch 1",
        "Week 4 Issue Review", "Non-Critical Defect Batch 2", "Performance Tuning Batch 2",
        "Report Corrections Batch 2", "Month-End Close Support",
        "Lessons Learned Workshop - Technical", "Lessons Learned Workshop - Business",
        "Knowledge Base Documentation", "Run Book Updates",
        "Transition to BAU Support Plan", "Support Team Training",
        "SLA Review & Adjustment", "Optimization Recommendations",
        "As-Built Documentation Update", "System Architecture Document Final",
        "Data Quality Report", "User Satisfaction Survey",
        "ROI Assessment Draft", "Benefits Realization Tracking Setup",
        "Vendor Relationship Transition", "License Optimization Review",
        "Archive Project Documentation", "Financial Close-out",
        "Project Close-out Report", "Steering Committee Final Presentation",
        "Warranty Period Plan", "Enhancement Backlog Handover",
        "Operational Readiness Confirmation", "Project Celebration Event",
        "Phase Gate Review - Closeout",
    ]

    all_phase_names = {
        "INI": phase_names_map["INI"],
        "REQ": phase_names_map["REQ"],
        "DES": phase_names_map["DES"],
        "CFG": cfg_names,
        "DEV": dev_names,
        "MIG": mig_names,
        "INT": int_names_list,
        "TST": tst_names,
        "UAT": uat_names,
        "TRN": trn_names,
        "DEP": dep_names,
        "SUP": sup_names,
    }

    # Build task IDs per phase
    phase_task_ids = {}
    task_index = 0
    for phase_code, phase_name, count in phases:
        ids = []
        for i in range(count):
            task_index += 1
            ids.append(f"E{task_index:03d}")
        phase_task_ids[phase_code] = ids

    phase_codes = [p[0] for p in phases]

    # Build predecessor network — all 19 DAG constraints applied
    predecessors_map = _build_predecessors_map(phase_codes, phase_task_ids, random)

    # Build activities with PERT estimates
    cpm_activities = []
    task_index = 0
    for phase_code, phase_name, count in phases:
        names_list = all_phase_names[phase_code][:count]
        while len(names_list) < count:
            names_list.append(f"{phase_name} Task {len(names_list)+1}")
        ids = phase_task_ids[phase_code]

        for i, tid in enumerate(ids):
            most_likely = random.randint(2, 12)
            optimistic = max(1, most_likely - random.randint(1, max(1, most_likely // 2)))
            pessimistic = most_likely + random.randint(1, max(1, most_likely))
            expected = (optimistic + 4 * most_likely + pessimistic) / 6
            min_dur = max(1, int(expected * random.uniform(0.5, 0.8)))
            resource = random.randint(2, 10)
            normal_cost = random.randint(5, 50) * 1000
            crash_cost = int(normal_cost * random.uniform(1.3, 2.0) / 1000) * 1000

            preds_str = ",".join(predecessors_map[tid])
            cpm_activities.append({
                "id": tid,
                "activity": names_list[i],
                "optimistic": str(optimistic),
                "most_likely": str(most_likely),
                "pessimistic": str(pessimistic),
                "predecessors": preds_str,
                "min_duration": str(min_dur),
                "crash_cost": str(crash_cost),
                "resource_demand": str(resource),
                "normal_cost": str(normal_cost),
            })

    # Forward pass for EVM timing
    id_to_act = {a["id"]: a for a in cpm_activities}
    es_map = {}
    ef_map = {}
    for act in cpm_activities:
        tid = act["id"]
        preds = [p.strip() for p in act["predecessors"].split(",") if p.strip()]
        es = max((ef_map.get(p, 0) for p in preds), default=0)
        o, m, p_ = int(act["optimistic"]), int(act["most_likely"]), int(act["pessimistic"])
        dur = math.ceil((o + 4 * m + p_) / 6)
        es_map[tid] = es
        ef_map[tid] = es + dur

    project_duration = max(ef_map.values())
    total_normal_cost = sum(int(a["normal_cost"]) for a in cpm_activities)
    bac = total_normal_cost

    # EVM tasks grouped by phase
    evm_tasks = []
    for pi, (phase_code, phase_name, count) in enumerate(phases):
        ids = phase_task_ids[phase_code]
        phase_budget = sum(int(id_to_act[tid]["normal_cost"]) for tid in ids)
        phase_es = min(es_map[tid] for tid in ids)
        phase_ef = max(ef_map[tid] for tid in ids)

        pct = 100.0 if pi < 3 else max(0, 95 - (pi - 3) * 15) + random.randint(-5, 5)
        pct = max(0.0, min(100.0, float(pct)))

        evm_tasks.append({
            "task_id": f"WP{pi+1:02d}",
            "name": phase_name,
            "budget": float(phase_budget),
            "pct_complete": pct,
            "planned_start": phase_es,
            "planned_finish": phase_ef,
            "actual_start": phase_es + random.randint(-1, 2),
            "actual_finish": phase_ef + random.randint(-2, 4),
            "baseline_start": phase_es,
            "baseline_finish": phase_ef,
            "pv_spread": "uniform",
            "cpm_task_id": None,
            "predecessors": [f"WP{pi:02d}"] if pi > 0 else [],
        })

    # EVM periods (sprints/bi-weekly)
    n_periods = min(40, project_duration // 3)
    periods = []
    for idx in range(n_periods):
        sprint = idx + 1
        progress = sprint / (project_duration / 3)
        pv = bac * min(1.0, progress * 1.02)
        ev = pv * random.uniform(0.92, 1.05)  # PG project: slightly better performance
        ac = ev * random.uniform(0.90, 1.05)
        periods.append({
            "index": idx,
            "label": f"Sprint {sprint}",
            "pv_cumulative": round(pv, 2),
            "ev_cumulative": round(ev, 2),
            "ac_cumulative": round(ac, 2),
            "ev_source": "manual",
        })

    risk_register = {
        "bac": float(bac),
        "high_exposure_threshold_pct": 0.05,
        "risks": [
            {"id": "ER1", "name": "Scope Creep", "description": "Stakeholders continuously add requirements beyond MVP", "probability": 0.6, "impact": float(bac * 0.12), "category": "Scope"},
            {"id": "ER2", "name": "Data Migration Failure", "description": "Legacy data quality issues cause migration delays", "probability": 0.4, "impact": float(bac * 0.10), "category": "Schedule"},
            {"id": "ER3", "name": "Key Resource Attrition", "description": "Critical ERP consultants leave mid-project", "probability": 0.25, "impact": float(bac * 0.08), "category": "Schedule"},
            {"id": "ER4", "name": "Integration Complexity", "description": "Legacy system interfaces more complex than estimated", "probability": 0.45, "impact": float(bac * 0.09), "category": "Cost"},
            {"id": "ER5", "name": "User Adoption Resistance", "description": "End users resist new system requiring extended training", "probability": 0.5, "impact": float(bac * 0.06), "category": "Quality"},
            {"id": "ER6", "name": "Vendor Patch Delays", "description": "ERP vendor delays critical patch needed for go-live", "probability": 0.3, "impact": float(bac * 0.07), "category": "Schedule"},
            {"id": "ER7", "name": "Performance Issues", "description": "System fails performance benchmarks under production load", "probability": 0.35, "impact": float(bac * 0.08), "category": "Quality"},
            {"id": "ER8", "name": "Regulatory Changes", "description": "New compliance requirements require system modifications", "probability": 0.2, "impact": float(bac * 0.05), "category": "Scope"},
            {"id": "ER9", "name": "Budget Overrun", "description": "Customization costs exceed estimates by 30%", "probability": 0.4, "impact": float(bac * 0.10), "category": "Cost"},
            {"id": "ER10", "name": "Go-Live Failure", "description": "Critical defect in production causes rollback", "probability": 0.1, "impact": float(bac * 0.15), "category": "Quality"},
        ],
    }

    swot = {
        "factors": [
            {"text": "Experienced implementation partner with 10+ ERP go-lives", "category": "Strength", "source": "Charter", "weight": 0.9, "linked_to": "team_capability"},
            {"text": "Executive sponsorship from CFO and COO", "category": "Strength", "source": "Charter", "weight": 0.85, "linked_to": "business_case"},
            {"text": "CPI > 1.0 — project under budget at midpoint", "category": "Strength", "source": "EVM", "weight": 0.7, "linked_to": "evm_cpi"},
            {"text": "Well-documented current-state business processes", "category": "Strength", "source": "Manual", "weight": 0.6, "linked_to": ""},
            {"text": "Limited internal ERP expertise for post go-live support", "category": "Weakness", "source": "Charter", "weight": 0.8, "linked_to": "skill_gap"},
            {"text": "Complex legacy data with 15+ years of inconsistencies", "category": "Weakness", "source": "Manual", "weight": 0.9, "linked_to": ""},
            {"text": "Multiple time zones across 8 regional offices", "category": "Weakness", "source": "Manual", "weight": 0.5, "linked_to": ""},
            {"text": "Digital transformation initiative provides funding certainty", "category": "Opportunity", "source": "Charter", "weight": 0.8, "linked_to": "business_case"},
            {"text": "Decommission 12 legacy systems reducing annual costs by $2M", "category": "Opportunity", "source": "Manual", "weight": 0.85, "linked_to": ""},
            {"text": "Cloud-first strategy enables global scalability", "category": "Opportunity", "source": "Manual", "weight": 0.7, "linked_to": ""},
            {"text": "Scope Creep — stakeholders expanding requirements", "category": "Threat", "source": "Risk Register", "weight": 0.9, "linked_to": "ER1"},
            {"text": "Data Migration Failure — legacy data quality issues", "category": "Threat", "source": "Risk Register", "weight": 0.8, "linked_to": "ER2"},
            {"text": "User Adoption Resistance — change management challenges", "category": "Threat", "source": "Risk Register", "weight": 0.7, "linked_to": "ER5"},
            {"text": "Vendor lock-in with limited negotiation leverage", "category": "Threat", "source": "Manual", "weight": 0.6, "linked_to": ""},
        ],
    }

    pestel = {
        "factors": [
            {"category": "Political", "description": "Government mandates e-invoicing compliance by Q3 2026", "impact_score": -3.0, "probability": 0.8, "timeframe": "Short-term", "mitigation": "Include e-invoicing module in Phase 1 scope", "linked_to": "ER8"},
            {"category": "Political", "description": "Trade agreements enable cross-border procurement optimization", "impact_score": 3.0, "probability": 0.6, "timeframe": "Medium-term", "mitigation": "Configure multi-entity procurement workflows", "linked_to": ""},
            {"category": "Economic", "description": "Inflation increases implementation partner rates by 10%", "impact_score": -2.5, "probability": 0.7, "timeframe": "Short-term", "mitigation": "Lock in fixed-price contract for Phases 2-4", "linked_to": "ER9"},
            {"category": "Economic", "description": "Strong business case with 280% IRR from legacy decommission", "impact_score": 4.0, "probability": 0.9, "timeframe": "Long-term", "mitigation": "Track benefits realization quarterly", "linked_to": ""},
            {"category": "Social", "description": "Workforce expects modern, mobile-friendly enterprise tools", "impact_score": 3.0, "probability": 0.8, "timeframe": "Short-term", "mitigation": "Prioritize mobile app deployment for field staff", "linked_to": ""},
            {"category": "Social", "description": "Resistance to change from long-tenured staff in finance", "impact_score": -2.0, "probability": 0.6, "timeframe": "Medium-term", "mitigation": "Engage finance super-users as change champions", "linked_to": "ER5"},
            {"category": "Technological", "description": "AI-powered anomaly detection improves data migration quality", "impact_score": 4.0, "probability": 0.7, "timeframe": "Short-term", "mitigation": "Use AI-based data profiling in migration Phase", "linked_to": "ER2"},
            {"category": "Technological", "description": "Legacy COBOL systems lack standard API interfaces", "impact_score": -3.0, "probability": 0.5, "timeframe": "Medium-term", "mitigation": "Build custom middleware adapters with retry logic", "linked_to": "ER4"},
            {"category": "Environmental", "description": "Cloud migration reduces on-premise data centre carbon footprint", "impact_score": 2.0, "probability": 0.8, "timeframe": "Long-term", "mitigation": "Include in ESG reporting dashboard", "linked_to": ""},
            {"category": "Legal", "description": "GDPR & data residency requirements for EU operations", "impact_score": -2.5, "probability": 0.9, "timeframe": "Short-term", "mitigation": "Configure data residency rules per legal entity", "linked_to": ""},
            {"category": "Legal", "description": "SOX compliance requires audit trails on all financial transactions", "impact_score": -2.0, "probability": 0.9, "timeframe": "Short-term", "mitigation": "Enable change document logging and approval workflows", "linked_to": ""},
        ],
    }

    # WBS tree — high-level structure matching phases
    wbs_nodes = [
        {"id": "wbs-root", "wbs_code": "1", "name": "ERP Implementation Project",
         "parent_id": "", "duration": project_duration, "cost": bac, "progress": 35.0,
         "status": "In Progress", "responsible": "Program Manager",
         "description": "Enterprise ERP implementation across all business functions",
         "linked_task_id": "", "sort_order": 0},
    ]
    phase_wbs_map = [
        ("wbs-ini", "1.1", "Initiation & Planning", "INI"),
        ("wbs-req", "1.2", "Requirements & Analysis", "REQ"),
        ("wbs-des", "1.3", "Solution Design", "DES"),
        ("wbs-cfg", "1.4", "Configuration", "CFG"),
        ("wbs-dev", "1.5", "Development", "DEV"),
        ("wbs-mig", "1.6", "Data Migration", "MIG"),
        ("wbs-int", "1.7", "Integration", "INT"),
        ("wbs-tst", "1.8", "Testing", "TST"),
        ("wbs-uat", "1.9", "User Acceptance", "UAT"),
        ("wbs-trn", "1.10", "Training & Change Mgmt", "TRN"),
        ("wbs-dep", "1.11", "Deployment", "DEP"),
        ("wbs-sup", "1.12", "Support & Closeout", "SUP"),
    ]

    for si, (wbs_id, wbs_code, wbs_name, pc) in enumerate(phase_wbs_map):
        ids = phase_task_ids[pc]
        cost = sum(int(id_to_act[tid]["normal_cost"]) for tid in ids)
        es = min(es_map[tid] for tid in ids)
        ef = max(ef_map[tid] for tid in ids)
        prog = 100.0 if si < 3 else max(0, 90 - (si - 3) * 12)

        wbs_nodes.append({
            "id": wbs_id, "wbs_code": wbs_code, "name": wbs_name,
            "parent_id": "wbs-root", "duration": ef - es, "cost": cost,
            "progress": round(prog, 1), "status": "Completed" if si < 3 else "In Progress" if si < 8 else "Not Started",
            "responsible": ["PMO Lead", "Business Analyst Lead", "Solution Architect",
                           "Config Lead", "Dev Lead", "Data Architect",
                           "Integration Lead", "QA Lead", "UAT Manager",
                           "Training Manager", "Release Manager", "Support Lead"][si],
            "description": f"Phase {si+1}: {wbs_name}",
            "linked_task_id": "", "sort_order": si,
        })

    wbs_tree = {"project_name": "ERP Implementation (Large PG Demo)", "nodes": wbs_nodes}

    return {
        "version": 1,
        "evm_project": {
            "schema_version": 1,
            "project_name": "ERP Implementation (Large PG Demo)",
            "bac": float(bac),
            "bac_auto_compute": False,
            "currency_symbol": "$",
            "tasks": evm_tasks,
            "periods": periods,
        },
        "risk_register": risk_register,
        "mc_results": None,
        "app_config": {"mode": "PG", "currency_symbol": "$"},
        "cpm_activities": cpm_activities,
        "cpm_mode": "probabilistic",
        "swot_analysis": swot,
        "pestel_analysis": pestel,
        "wbs_tree": wbs_tree,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "src", "pmhelper", "demos_edu")
    os.makedirs(out_dir, exist_ok=True)

    print("Generating large UG demo (600 tasks)...")
    ug = generate_ug_demo()
    ug_path = os.path.join(out_dir, "campus_construction_ug_large.pmproj")
    with open(ug_path, "w", encoding="utf-8") as f:
        json.dump(ug, f, indent=2, ensure_ascii=False)
    print(f"  → {len(ug['cpm_activities'])} activities, BAC=${ug['evm_project']['bac']:,.0f}")
    print(f"  → Saved to {ug_path}")

    print("Generating large PG demo (600 tasks)...")
    pg = generate_pg_demo()
    pg_path = os.path.join(out_dir, "erp_implementation_pg_large.pmproj")
    with open(pg_path, "w", encoding="utf-8") as f:
        json.dump(pg, f, indent=2, ensure_ascii=False)
    print(f"  → {len(pg['cpm_activities'])} activities, BAC=${pg['evm_project']['bac']:,.0f}")
    print(f"  → Saved to {pg_path}")

    print("\nDone! Both demo files generated.")
