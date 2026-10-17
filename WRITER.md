# rvt-write: build Revit models from a JSON spec (no Revit needed)

```
./rvt-write example > my.json          # example spec
./rvt-write check my.json              # validate only
./rvt-write scene my.json out.rte      # build out.rte + out.rte.json (manifest) + out.rte.report.json, then offline invariants (--no-verify to skip)
```

Our own writer: every added element is a clone of a record that Revit itself wrote in a small
"rosetta" file (one object, base + one-change variant), with ids, references, positions and
checksums rewritten by our code (fitted from Revit samples). No Revit, no ODA, no third-party code.

The output always contains the **seed**: a tiny Revit-made house (`rosetta/<year>_house_base.rte`,
5 walls, 2 doors, 3 windows, 2 columns, floor, room, text) at x 0..47, y 0..30 on level `L1`
(elevation 0). Place your model elsewhere (e.g. x >= 60) to keep it clear.

Years: **2024** and **2026** (`"year"`). Units: feet.

## Spec

| key | items | supported / limits |
|---|---|---|
| `levels` | `{name, elevation}` | any number; `L1` = seed ground level |
| `params` | `{name, kind, guid?}` kind = text, int, number, length, yesno | shared parameters bound to walls; GUID = `guid` or a deterministic uuid5 of kind+name (builds are reproducible: same spec, same bytes) |
| `walls` | `{id?, from:[x,y], to:[x,y], level, height, mark?, comments?, values?:{param: value}}` | straight, any direction, any level; type = template wall type |
| `floors` | `{x, y, width, depth, level}` | rectangles with width >= depth |
| `columns` | `{x, y, base, top}` | structural columns between two levels |
| `windows`, `doors` | `{wall: <wall id>, offset}` | host wall must run along +x; first window type / door type of the template. Host wall is NOT cut (see limits) |
| `views` | `{name, level}` | floor plans |
| `sheets` | `{number, name, viewports?:[{view, centre:[x,y]}]}` | sheets with the template title block; viewports 2024 and 2026 (the plan must contain something, Revit refuses empty plans), each plan on at most one sheet |
| `text` | `{x, y, text}` | model-level text notes (level 1 plan) |
| `detail_lines` | `{view, from, to}` | view-owned detail lines (2024, 2026) |
| `view_text` | `{view, x, y, text}` | text notes in a given plan (2024, 2026) |
| `grids` | `{name, from, to}` | straight grids, any direction (2024 and 2026; the old 2026 refusal was the short-last-page bug, fixed 2026-10-15) |
| `stairs` | `{offset:[dx,dy]}` | translated copy of a Revit-made straight stair L1->L2 (run (60,40)-(75,40), its railings included) |
| `railings` | `{offset:[dx,dy]}` | translated copy of a Revit-made railing (60,50)-(80,50)-(80,58) on L1 |
| `roofs` | `{offset:[dx,dy]}` | translated copy of a Revit-made flat footprint roof 30x20 ft + ceiling (types imported once, reused) |
| `rooms` | `{id?, level, x, y, width, depth, name, number}` | a room enclosed by 4 writer-made JOINED walls (9 ft, Revit's join records fitted from rosetta rooms_lv); Revit computes the area itself (measured: exactly the interior to the wall faces). One room per level, not on L1; walls are addressable as `<id>.south/east/north/west` |
| `topography` | `{offset:[dx,dy]}` | translated copy of a Revit-made 5-point toposurface (40x40 ft hill, z 0..5) |
| `curtain_walls` | `{offset:[dx,dy]}` | translated copy of a Revit-made curtain wall (60,62)-(84,62), 12 ft, 4x3 panels, 17 mullions |

Stairs, railings and curtain walls are *shift* objects: the writer clones every record of the Revit-made
object (learnt from a base/variant pair where Revit moved it by (+100,+50)) and moves all position fields.
Shape is fixed; position is free. Revit's geometry export of the copies equals the original solids moved
by the offset (checked solid by solid).

Viewport centre: the writer stores the viewport's offset; Revit derives the box from the view's
model outline. The writer estimates that outline from the spec (walls/floors on the level + seed);
expect the box centre within a few hundredths of a foot of the requested centre (measured per
scene in LOG.md).

## Verification protocol (every deliverable)
1. offline invariants (`vcheck.py`: ECC, gzip, record chain, Adler, ids, seed records preserved)
2. Revit (offline VM) API open with audit off and on, SaveAs + reopen equal element list
3. Revit UI command-line open, no dialogs
4. Revit geometry export compared to the manifest (`stageb_check.py`: class, position, volume, params)
5. views/sheets: Revit viewdump compared to the manifest (`check_views.py`: viewports, detail lines, view text)

6. 3D pick + phase (`tools/pickwalls.py` then `tools/pickcheck.py`, PICKCHECK PASS): a Phase 1 / Show Complete 3D view (what the GUI creates) is shot with ReferenceIntersector rays at every Wall, Structural Column and Floor (all must be hit = hover/select works) and no element may be in a later phase than the view (else it is invisible). Needs the spatial pick key (`genlib.spatial_key`) and Phase 1 on every cloned record (`setphase`; `Scene._rephase_seed` for the seed).
   Whole chain for rebuilt scenes: `pipeline/rebuild_scenes.sh YEAR scene...` (builds, vcheck, queues the protocol + pick check for jobq); `pipeline/deliver.py` only delivers scenes with PICKCHECK PASS.
7. Infra: the guest add-in signing cert is throwaway (2 days). After an idle period `guest.fresh()` re-signs it (C:/ci/trust-and-sign.ps1 -Years 2024,2026) when Revit gives no port.

Run: `pipeline/stageb_job.sh TAG YEAR OUT.rte rosetta/<year>_house_base.rte` (needs the VM).

## Revit finishing pass (optional; needs the offline Revit VM; output is Revit-saved and flagged)
`rvt-write finish YEAR IN.rte OUT.rte FINISH.json [IN.rte.json]` runs ONE Revit session over a writer file and adds what Revit does better than the writer. Example: `specs/finish_example.json`.

| key | what Revit does | notes |
|---|---|---|
| `openings: true` | re-creates every hosted door/window through the API at the same point and host wall, so every wall opening is cut | any wall geometry; verified max position error 0.000 ft, wall volume 2927.66 -> 2738.36 ft3 on the fit-out scene |
| `rooms: [{level,x,y,name,number}]` | walls are touched first (Revit then joins the writer's unjoined walls and rebuilds the level's room topology), then `NewRoom` | fails with a clear error if the point is not enclosed |
| `grids: [{name,from,to}]` | `Grid.Create` | the way to get grids in 2026 |
| `dimensions: [{view,walls:[a,b],offset} / {view,grids:[a,b],offset}]` | linear dimensions between two parallel walls (side faces) or two grids | |
| `tags: [{view,element,at}]` | `IndependentTag` for the element's category; the tag family is copied from the default template when the project has none | |
| `text`, `detail_lines`, `filled_regions: [{view,x,y,w,d}]`, `viewports: [{sheet,view,centre}]` | text notes, detail lines, rectangular filled regions, viewports | |

Names of walls/levels/views/sheets resolve through the manifest `IN.rte.json` written by `scene` (walls need an `"id"` in the spec); numbers are raw element ids. Instance ids of re-created doors/windows change. Tested 2024 and 2026: 7 openings, 2 grids, 1 room, 2 dimensions, 2 tags, text, detail line, filled region all created; Revit's viewdump lists them in the plan view.

## Known limits (honest)
- windows/doors do not cut the host wall in pure writer output except the fitted case (60 ft wall along +x on level 1, k<=3 windows); use the finishing pass (`openings`) for any other geometry
- rooms: writer-built only as `rooms` boxes (4 joined 9 ft walls, one room per level, not on L1); rooms bounded by other walls, rooms on L1, several rooms per level: Revit finishing pass (`rooms`). Tags: finishing pass only; rectangular FILLED REGIONS are pure writer (`filled_regions` in the scene spec, `S.filled_region`; scene regions1 PASS 2024+2026); PURE-WRITER linear dimensions (scene spec key `dimensions: [{view, walls:["office.west","office.east"], at}]` or `S.dimension(plan, wallA, wallB, c)`; specs/dims_example_<year>.json) work on the walls of `room_box` (4 JOINED walls with Revit-made join records), full protocol PASS 2024+2026; walls from plain `S.wall` (unjoined) crash Revit on open, see below; linear dimensions between two wall faces can be written by `tools/add_dimensions.py` on a file whose walls Revit already regenerated (e.g. the output of `rvt_write.py finish` with openings/rooms/touch_walls): Revit rejects a pure-writer dimension that references an UNREGENERATED writer wall (InternalException on open), regenerated walls accept it (2024+2026, API audit off/on, UI, reopen)
- not yet writer-built: roofs/ceilings of free size (fixed 30x20 shape only), stairs/railings/curtain walls of free shape, MEP, groups, worksets, design options, tags, filled regions, schedules on sheets
- 2024: Revit refuses to place an EMPTY plan view on a sheet (Viewport.Create returns null); the writer's viewports are tested on plans with content

## Revit-validity notes (2026-10-15)
- Picking: every wall and floor the writer makes carries Revit's per-element spatial key (genlib.spatial_key, derived from the element outline), so 3D hover/selection works in Revit 2024 and 2026. The protocol checks it with a ReferenceIntersector ray at every wall, column and floor (tools/pickwalls.py, tools/pickcheck.py).
- Phases: the seed house is moved to Phase 1 (the phase of the template views and of Revit's default 3D view), like every writer element; otherwise the seed is invisible in those views.
