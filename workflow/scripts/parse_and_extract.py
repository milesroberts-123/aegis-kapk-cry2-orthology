#!/usr/bin/env python3
"""Parse orthology files, deduplicate by latest assembly, extract orthologous
protein sequences from proteomes, and write a combined FASTA file."""

import argparse
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


ATHALIANA_ORTHO_PREFIX = "Athalianacolumbia"
ATHALIANA_SPECIES = "Athaliana"
ATHALIANA_PHYTOZOME = "447"
ATHALIANA_ASSEMBLY = "Araport11"
ATHALIANA_PROTEIN = "AT1G04400.1"

PROTEOME_SUFFIX = ".protein_primaryTranscriptOnly.fa.gz"
ORTHO_FILE_PATTERN = re.compile(r"^inParanoid_")
ORTHO_ATHALIANA_MARKER = "Athaliana_447_Araport11"

FILENAME_PARSE = re.compile(r"^(.+?)_(\d+(?:_\d+)?)_(.+)$")


def parse_proteome_filename(filename: str) -> tuple[str, str, str] | None:
    """Extract (species, phytozome_id, assembly) from a proteome filename.

    Expects: {Species}_{PhytozomeID}_{Assembly}.protein_primaryTranscriptOnly.fa.gz
    """
    if not filename.endswith(PROTEOME_SUFFIX):
        return None
    stem = filename[: -len(PROTEOME_SUFFIX)]
    m = FILENAME_PARSE.match(stem)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def index_proteomes(proteome_dir: str) -> dict[tuple[str, str], tuple[str, str]]:
    """Walk proteome_dir and build index: (species, phytozome_id) -> (path, assembly)."""
    index: dict[tuple[str, str], tuple[str, str]] = {}
    for root, _dirs, files in os.walk(proteome_dir):
        for fname in files:
            if not fname.endswith(".fa.gz"):
                continue
            parsed = parse_proteome_filename(fname)
            if parsed is None:
                continue
            species, phytozome_id, assembly = parsed
            key = (species, phytozome_id)
            full_path = os.path.join(root, fname)
            if key in index:
                print(f"Warning: duplicate proteome for {species}_{phytozome_id}, "
                      f"using {index[key][0]}", file=sys.stderr)
            else:
                index[key] = (full_path, assembly)
    return index


def parse_orthology_entry(line: str) -> tuple[str, list[str]]:
    """Parse a tab-separated orthology line.

    Returns (species_prefix, [protein_ids]) for the non-Athaliana column.
    The line has two tab-separated columns (OrtoA and OrtoB).
    Each column contains space-separated entries alternating between:
        SpeciesPrefix:ProteinID ConfidenceScore
    Only entries containing ':' are protein IDs; bare numbers are scores.
    """
    parts = line.strip().split("\t")
    if len(parts) != 2:
        return "", []

    for col_idx in (0, 1):
        entries = parts[col_idx].split()
        for entry in entries:
            if entry.startswith(ATHALIANA_ORTHO_PREFIX + ":"):
                other_col = parts[1 - col_idx]
                other_entries = other_col.split()
                if not other_entries:
                    return "", []
                first = other_entries[0]
                if ":" not in first:
                    return "", []
                species_prefix = first.split(":")[0]
                protein_ids = [e.split(":")[1] for e in other_entries
                               if ":" in e and not e[0].isdigit()]
                return species_prefix, protein_ids

    return "", []


def parse_orthology_filename(filename: str) -> tuple[str, str, str] | None:
    """Extract (species, phytozome_id, assembly) from an orthology filename.

    Filename format:
        inParanoid_{Species}_{PhytozomeID}_{Assembly}_Athaliana_447_Araport11
    or:
        inParanoid_Athaliana_447_Araport11_{Species}_{PhytozomeID}_{Assembly}
    """
    name = filename
    if name.startswith("inParanoid_"):
        name = name[len("inParanoid_"):]

    if name.startswith(ORTHO_ATHALIANA_MARKER + "_"):
        rest = name[len(ORTHO_ATHALIANA_MARKER) + 1:]
    elif name.endswith("_" + ORTHO_ATHALIANA_MARKER):
        rest = name[: -(len(ORTHO_ATHALIANA_MARKER) + 1)]
    else:
        return None

    m = FILENAME_PARSE.match(rest)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def parse_orthology_files(
    ortho_dir: str, query_gene: str
) -> list[tuple[str, str, str, list[str]]]:
    """Scan orthology files for query_gene.

    Returns: [(species, phytozome_id, assembly, [protein_ids]), ...]
    """
    results: list[tuple[str, str, str, list[str]]] = []
    for fname in sorted(os.listdir(ortho_dir)):
        fpath = os.path.join(ortho_dir, fname)
        if not os.path.isfile(fpath):
            continue
        if not fname.startswith("inParanoid_"):
            continue

        with open(fpath) as f:
            content = f.read()

        if query_gene not in content:
            continue

        parsed = parse_orthology_filename(fname)
        if parsed is None:
            print(f"Warning: could not parse orthology filename: {fname}", file=sys.stderr)
            continue
        species, phytozome_id, assembly = parsed

        for line in content.splitlines():
            if query_gene in line:
                ortho_species, protein_ids = parse_orthology_entry(line)
                if ortho_species and protein_ids:
                    results.append((species, phytozome_id, assembly, protein_ids))
                break

    return results


def deduplicate_by_latest(
    ortho_results: list[tuple[str, str, str, list[str]]],
) -> dict[str, tuple[str, str, list[str]]]:
    """Group by species prefix, keep only the entry with the highest Phytozome ID.

    Phytozome IDs are numeric (or compound like 169_227). Higher = newer.
    For compound IDs, compare the first number.
    """
    groups: dict[str, list[tuple[str, str, str, list[str]]]] = defaultdict(list)
    for species, phytozome_id, assembly, protein_ids in ortho_results:
        groups[species].append((phytozome_id, assembly, protein_ids))

    deduped: dict[str, tuple[str, str, list[str]]] = {}
    for species, entries in groups.items():
        if len(entries) == 1:
            deduped[species] = (entries[0][0], entries[0][1], entries[0][2])
        else:
            def sort_key(entry: tuple[str, str, list[str]]) -> int:
                pid = entry[0]
                try:
                    return int(pid.split("_")[0])
                except ValueError:
                    return 0
            best = max(entries, key=sort_key)
            dropped = [e for e in entries if e != best]
            for d in dropped:
                print(f"Info: dropping {species}_{d[0]}_{d[1]} in favor of "
                      f"{species}_{best[0]}_{best[1]}", file=sys.stderr)
            deduped[species] = (best[0], best[1], best[2])

    return deduped


def extract_sequences(
    proteome_path: str,
    protein_ids: list[str],
    species: str,
    output_handle,
) -> int:
    """Extract protein sequences from a proteome FASTA using seqkit.

    Uses regex mode (-r) with word-boundary anchoring to match protein IDs
    that appear in the transcript= field of FASTA headers.
    Pipes seqkit grep into seqkit replace to rename headers.
    Returns the number of sequences extracted.
    """
    grep_cmd = ["seqkit", "grep", "-n", "-r"]
    for pid in protein_ids:
        grep_cmd.extend(["-p", rf"transcript={pid}\b"])
    grep_cmd.append(proteome_path)

    replace_pattern = r"^(\S+).*"
    replace_repl = f"{species}_$1"
    replace_cmd = ["seqkit", "replace", "-p", replace_pattern, "-r", replace_repl]

    try:
        p1 = subprocess.Popen(
            grep_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        p2 = subprocess.Popen(
            replace_cmd, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if p1.stdout:
            p1.stdout.close()
        stdout, stderr = p2.communicate()
        grep_stderr = p1.stderr.read() if p1.stderr else b""

        if p2.returncode != 0:
            print(f"Warning: seqkit replace failed for {species}: {stderr.decode()}",
                  file=sys.stderr)
            return 0

        output_handle.write(stdout)
        lines = stdout.decode().count("\n")
        seq_count = sum(1 for line in stdout.decode().splitlines() if line.startswith(">"))

        if seq_count < len(protein_ids):
            print(f"Warning: {species}: expected {len(protein_ids)} sequences, "
                  f"got {seq_count}", file=sys.stderr)

        return seq_count

    except FileNotFoundError:
        print("Error: seqkit not found. Is it installed in the conda environment?",
              file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Extract orthologous protein sequences for a query gene"
    )
    parser.add_argument("--ortho-dir", required=True, help="Path to orthology directory")
    parser.add_argument("--proteome-dir", required=True, help="Path to proteomes directory")
    parser.add_argument("--query", required=True, help="Query gene ID (e.g. AT1G04400)")
    parser.add_argument("--output", required=True, help="Output FASTA file path")
    args = parser.parse_args()

    print(f"Indexing proteomes in {args.proteome_dir}...", file=sys.stderr)
    proteome_index = index_proteomes(args.proteome_dir)
    print(f"  Found {len(proteome_index)} proteome files", file=sys.stderr)

    print(f"Parsing orthology files in {args.ortho_dir} for {args.query}...", file=sys.stderr)
    ortho_results = parse_orthology_files(args.ortho_dir, args.query)
    print(f"  Found {len(ortho_results)} orthology entries", file=sys.stderr)

    print("Deduplicating by latest assembly...", file=sys.stderr)
    deduped = deduplicate_by_latest(ortho_results)
    print(f"  {len(deduped)} species after deduplication", file=sys.stderr)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    total_seqs = 0
    matched = 0
    missing_proteome = 0

    with open(args.output, "wb") as out_fh:
        ath_key = (ATHALIANA_SPECIES, ATHALIANA_PHYTOZOME)
        if ath_key in proteome_index:
            ath_path, _ = proteome_index[ath_key]
            n = extract_sequences(ath_path, [ATHALIANA_PROTEIN], ATHALIANA_SPECIES, out_fh)
            total_seqs += n
            print(f"  Extracted {n} Athaliana sequence(s)", file=sys.stderr)
        else:
            print(f"Error: Athaliana proteome not found for key {ath_key}", file=sys.stderr)
            sys.exit(1)

        for species in sorted(deduped.keys()):
            phytozome_id, assembly, protein_ids = deduped[species]
            key = (species, phytozome_id)

            if key not in proteome_index:
                print(f"Warning: no proteome for {species}_{phytozome_id} — skipping",
                      file=sys.stderr)
                missing_proteome += 1
                continue

            proteome_path, proteome_assembly = proteome_index[key]
            if proteome_assembly != assembly:
                print(f"Info: {species}_{phytozome_id}: assembly mismatch "
                      f"(ortho={assembly}, proteome={proteome_assembly}), "
                      f"using proteome", file=sys.stderr)

            n = extract_sequences(proteome_path, protein_ids, species, out_fh)
            total_seqs += n
            matched += 1

    print(f"\nSummary:", file=sys.stderr)
    print(f"  Species with orthologs (after dedup): {len(deduped)}", file=sys.stderr)
    print(f"  Species matched to proteome:          {matched}", file=sys.stderr)
    print(f"  Species missing proteome:              {missing_proteome}", file=sys.stderr)
    print(f"  Total sequences extracted:             {total_seqs}", file=sys.stderr)
    print(f"  Output written to:                     {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
