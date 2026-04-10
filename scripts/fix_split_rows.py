import logging
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd
import json

DB_PATH = "./data_copy.db"
CONFIG_PATH = "all_configs.json"


def load_configurations() -> List[List[str]]:
    with open(CONFIG_PATH, "r") as cfg_file:
        config_dict = json.load(cfg_file)
    return [
        [b["provider"], b["test"], b["language"], b["cpu"], b["memory"]]
        for b in config_dict.get("benchmarks", [])
    ]


def normalize_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    # Treat empty strings as missing
    if isinstance(value, str):
        s = value.strip()
        if s == "":
            return None
        return s
    return value


def merge_rows(row_a: pd.Series, row_b: pd.Series, columns: List[str]) -> Optional[Dict[str, object]]:
    merged: Dict[str, object] = {}
    for column in columns:
        if column == "id":
            continue

        value_a = row_a[column]
        value_b = row_b[column]

        if column == "timestamp":
            merged[column] = int(min(value_a, value_b))
            continue

        # Consider empty strings as missing as well
        def is_present(v):
            if pd.isna(v):
                return False
            if isinstance(v, str) and v.strip() == "":
                return False
            return True

        a_present = is_present(value_a)
        b_present = is_present(value_b)

        if a_present and b_present:
            na = normalize_value(value_a)
            nb = normalize_value(value_b)
            # If both are numbers, compare numerically. Otherwise compare string forms trimmed.
            try:
                import numbers

                if isinstance(na, numbers.Number) and isinstance(nb, numbers.Number):
                    if float(na) != float(nb):
                        return None
                    merged[column] = na
                else:
                    # Compare as strings (trimmed)
                    if str(na).strip() != str(nb).strip():
                        return None
                    merged[column] = na
            except Exception:
                if str(na).strip() != str(nb).strip():
                    return None
                merged[column] = na
        elif a_present:
            merged[column] = normalize_value(value_a)
        elif b_present:
            merged[column] = normalize_value(value_b)
        else:
            merged[column] = None

    return merged


def generate_cpu_variants(cpu: Optional[str]) -> List[Optional[str]]:
    variants: List[Optional[str]] = []
    if cpu is None:
        return [None]

    trimmed = cpu.strip()
    if trimmed:
        variants.append(trimmed)
        if trimmed.endswith("vCPU"):
            without_suffix = trimmed[:-4].strip()
            if without_suffix:
                variants.append(without_suffix)
        else:
            variants.append(f"{trimmed}vCPU")
    else:
        variants.append(None)

    # Deduplicate while preserving order
    seen = set()
    ordered: List[Optional[str]] = []
    for variant in variants:
        if variant not in seen:
            ordered.append(variant)
            seen.add(variant)

    # Final fallback: no CPU filter at all
    ordered.append(None)
    return ordered


def fetch_dataframe(config: List[str]) -> pd.DataFrame:
    provider, experiment, language, cpu, memory = config

    def run_query(conn: sqlite3.Connection, cpu_value: Optional[str]) -> pd.DataFrame:
        base_query = (
            "SELECT * FROM data WHERE provider = ? AND experiment = ? AND language = ? "
            "AND memory = ?"
        )
        params: List[object] = [provider, experiment, language, memory]
        if cpu_value is not None:
            base_query += " AND cpu = ?"
            params.append(cpu_value)
        base_query += " ORDER BY timestamp ASC"
        return pd.read_sql_query(base_query, conn, params=params)

    conn = sqlite3.connect(DB_PATH)
    try:
        cpu_variants = generate_cpu_variants(cpu)
        for cpu_value in cpu_variants:
            df = run_query(conn, cpu_value)
            if not df.empty:
                return df
        return pd.DataFrame()
    finally:
        conn.close()


def find_pairs_for_config(config: List[str]) -> List[Dict[str, object]]:
    df = fetch_dataframe(config)
    if df.empty:
        return []

    columns = df.columns.tolist()
    pairs: List[Dict[str, object]] = []
    i = 0
    max_index = len(df) - 1

    while i < max_index:
        row = df.iloc[i]
        row_after = df.iloc[i + 1]

        timestamp_current = int(row["timestamp"])
        timestamp_next = int(row_after["timestamp"])

        if timestamp_current + 1 != timestamp_next:
            i += 1
            continue

        merged_row = merge_rows(row, row_after, columns)
        if not merged_row:
            i += 1
            continue

        pairs.append(
            {
                "delete_ids": (int(row["id"]), int(row_after["id"])),
                "insert_row": merged_row,
                "config": config,
            }
        )

        i += 2

    return pairs


def run_parallel_detection(configs: List[List[str]]) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=min(8, len(configs) or 1)) as executor:
        future_map = {executor.submit(find_pairs_for_config, cfg): cfg for cfg in configs}
        for future in as_completed(future_map):
            config = future_map[future]
            try:
                pairs = future.result()
                if pairs:
                    results.extend(pairs)
            except Exception:
                logging.exception(
                    "Failed to process config %s", config
                )
    return results


def chunked(sequence: List[int], size: int) -> Iterable[List[int]]:
    for idx in range(0, len(sequence), size):
        yield sequence[idx : idx + size]


def delete_rows(conn: sqlite3.Connection, row_ids: List[int]) -> int:
    if not row_ids:
        return 0
    total_deleted = 0
    for chunk in chunked(row_ids, 900):
        placeholders = ",".join(["?"] * len(chunk))
        query = f"DELETE FROM data WHERE id IN ({placeholders})"
        cursor = conn.execute(query, chunk)
        total_deleted += cursor.rowcount
    return total_deleted


def insert_rows(conn: sqlite3.Connection, rows: List[Dict[str, object]]) -> int:
    if not rows:
        return 0
    df = pd.DataFrame(rows)
    df.to_sql("data", conn, if_exists="append", index=False)
    return len(rows)


def apply_changes(pairs: List[Dict[str, object]]) -> Tuple[int, int, int]:
    if not pairs:
        return 0, 0, 0

    unique_delete_ids: List[int] = []
    new_rows: List[Dict[str, object]] = []

    for pair in pairs:
        unique_delete_ids.extend(pair["delete_ids"])
        new_rows.append(pair["insert_row"])

    unique_delete_ids = sorted(set(unique_delete_ids))

    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            deleted = delete_rows(conn, unique_delete_ids)
            inserted = insert_rows(conn, new_rows)
    finally:
        conn.close()

    return len(pairs), deleted, inserted


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    configs = load_configurations()
    if not configs:
        logging.info("No benchmark configurations found in %s", CONFIG_PATH)
        return

    logging.info("Scanning %d configuration sets in parallel", len(configs))

    pairs = run_parallel_detection(configs)
    if not pairs:
        logging.info("No split rows detected. No changes applied.")
        return

    pair_count, deleted_rows, inserted_rows = apply_changes(pairs)
    logging.info(
        "Merged %d split pairs. Deleted %d rows and inserted %d merged rows.",
        pair_count,
        deleted_rows,
        inserted_rows,
    )

    print(
        f"Rows affected: {deleted_rows + inserted_rows} "
        f"(deleted: {deleted_rows}, inserted: {inserted_rows}, pairs merged: {pair_count})."
    )


if __name__ == "__main__":
    main()