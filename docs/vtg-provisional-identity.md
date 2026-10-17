# Provisional TD-to-TYP identity links

`td_lst` is still the authoritative source of explicit TD/TYP associations. When
that list stalls, automation can record a reversible association in
`data/cache/kma_apihub/td_typ_links.json`. The raw official lists are never edited.

Automatic inference requires all of the following:

- A named TYP in `typ_lst`, using its official KMA start time as the boundary.
- A regular ATCF identity verified by a name match for that TYP.
- A successful forecast for the candidate TD within six hours before naming,
  using the same regular ATCF identity.
- Official KMA analysis coordinates for both endpoints, from exact-time KMA GTS
  analysis rows or each system's own saved official track history. Model means,
  B-deck coordinates, and broad historical alias lists are not identity evidence.
- An endpoint displacement <=300 km and speed <75 km/h.
- One unambiguous TD/TYP pair, with no conflicting official/manual association.

The link suppresses the old TD production job only at or after the naming time.
Earlier cycles retain their original TD labels. The named job carries the TD alias
so the existing same-cycle source backup can follow the identity transition.
Lightweight prechecks reuse saved links without adding ATCF network calls.

The page groups the two source manifests while retaining both paths for historical
TD images. At duplicate cycles it always prefers the named TYP image, even if a
stale TD image was generated later. No old PNGs or folders are moved or deleted by
a provisional link. Normal canonical migration remains conditional on official
TD-list confirmation.

Archive scans and backup cleanup project the same connection in memory: promotion
is not dissipation. A genuinely later linked weakening TD episode remains active;
only final TYP termination permits cleanup of the connected source backups.
Unconfirmed historical TD folders remain untouched until the official linkage
allows normal migration and archival.

When `td_lst` confirms the connection, its state becomes `confirmed`. An explicit
different TYP number, changed TYP start time, or incompatible TD episode marks a
`conflict` and disables the temporary connection instead of silently moving
historical files. Missing API rows are not evidence of termination or conflict.

The registry is a small identity/evidence table, not a raw forecast archive. New
records are written through the existing changed-path workflow. If evidence is
insufficient or ambiguous, no link is inferred and the normal workflow continues.
