<p align="center"><img src="assets/logo.png" alt="rvt-writer logo" width="140"></p>

<h1 align="center">rvt-writer</h1>
<p align="center">Experimental generator of Revit <code>.rte</code> / <code>.rvt</code> scenes from a JSON spec.</p>

<p align="center"><a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-0f766e"></a> <img alt="Status: experimental" src="https://img.shields.io/badge/status-experimental-1e293b"></p>

## What it does

Builds Revit files by cloning records that Revit itself wrote into small reference ("rosetta") files, then rewriting ids, references, positions and checksums with this code. Supports levels, shared parameters, walls, columns, floors, doors, windows and more; builds are deterministic (same spec, same bytes). Output is validated against the Revit API.

```bash
python rvt_write.py example > my.json         # example spec
python rvt_write.py check my.json              # validate only
python rvt_write.py scene my.json out.rte      # build out.rte plus manifest and report
```

See [`WRITER.md`](WRITER.md) for the spec format, supported classes and the verification protocol.

## Important limitations

- **Reference files are not included.** The seed `.rte` files are made with Revit and are Autodesk-derived, so they are kept out of this repository. You must generate your own with a licensed Revit using the scripts in [`tools/`](tools). Without them the writer cannot run.
- Experimental: supported Revit years are limited (currently 2024 and 2026), and files should always be opened in Revit and validated before real use.
- The scripts in [`tools/`](tools) and [`pipeline/`](pipeline) are research tooling run against a Revit installation.

## Coverage

Supported spec keys (each verified through the protocol in `WRITER.md`): levels, shared parameters, walls, floors, columns, windows and doors, floor-plan views, sheets and viewports, text, detail lines, grids, rooms, free-size flat roofs with ceilings, and position-free copies of Revit-made stairs, railings, roofs, toposurfaces, curtain walls, beams, wall foundations, MEP (duct and pipe) and groups. Files are produced for Revit **2024 and 2026**.

Every deliverable is checked offline (ECC, gzip, record chain, ids), reopened in Revit through the API and UI with no dialogs, compared with Revit's geometry export (class, position, volume, parameters) and picked in 3D.

## Pending

- Other Revit years, and free-shape (not translated-copy) stairs, railings, curtain walls and MEP.
- Doors and windows only on walls running along +x; host walls are not cut without the optional Revit finishing pass.
- Further element classes (families, rebar, mass).

## The rvt toolkit

| Repo | Role |
|---|---|
| [rvt-reader](https://github.com/baleti/rvt-reader) | Pure-Python reader: file container, schema, elements, parameters, geometry |
| [rvt-core](https://github.com/baleti/rvt-core) | Optional Rust acceleration for the reader (PyO3) |
| [rvt-viewer](https://github.com/baleti/rvt-viewer) | Browser 3D viewer built on the reader |
| [rvt-sheets](https://github.com/baleti/rvt-sheets) | Sheet and view renderer (2D drawings) built on the reader |
| [rvt-qa](https://github.com/baleti/rvt-qa) | Visual-diff QA tooling for rvt-sheets output |
| [rvt-writer](https://github.com/baleti/rvt-writer) | Experimental generator of `.rvt` / `.rte` scenes |

## Status and scope

Research-grade software developed by reverse-engineering the file format through black-box analysis of sample files and comparison with the output of the official Revit API. It is accurate on the files it has been tested against but makes no guarantees for arbitrary files. Test models (Autodesk sample files) and Revit-derived ground-truth data are **not** included in this repository.

## License

MIT, see [LICENSE](LICENSE). Autodesk and Revit are trademarks of Autodesk, Inc. This project is independent and is not affiliated with, endorsed by or sponsored by Autodesk.
