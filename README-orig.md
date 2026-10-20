# write-lab: rvt-write, a Revit model writer without Revit

Builds Revit 2024 / 2026 `.rte`/`.rvt` files from a JSON scene spec using our own writer (every element is a clone of a record Revit itself wrote in a small "rosetta" file, ids/positions/checksums rewritten by our code).

    ./rvt-write example > my.json     # example spec
    ./rvt-write check my.json         # validate only
    ./rvt-write scene my.json out.rte # build + offline invariants (vcheck)

- Spec format, per-class support and known limits: **WRITER.md** (spec keys: levels, walls, floors, columns, windows/doors, views, sheets+viewports, text, detail lines, grids, rooms, roofs (free-size, landscape and portrait, any level), stairs/railings/curtain walls/beams/MEP/groups (shift objects), topography, dimensions, filled regions).
- Regression matrix (every scene, year, last protocol result): **scenes/REGRESSION.md** (`tools/regression_matrix.py`).
- Verification protocol (offline invariants, Revit API open audit off/on, UI open, geometry vs manifest, 3D pick check) and the Revit finishing pass: WRITER.md.
- Work log and handoff: LOG.md, HANDOFF.md.
- Memory note: a scene build peaks near 0.7 GB; run it on a host with free RAM (host1 via h1run) when the daily-driver is short on memory.
