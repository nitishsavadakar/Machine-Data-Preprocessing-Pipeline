# Machine Data Preprocessing & Telemetry Pipeline

An automated Python data engineering pipeline designed to ingest raw machine CSV log files, normalize formats, explode high-frequency time-series arrays, generate component part trackers, and compute Remaining Useful Life (RUL) health indexes.

---

## Detailed Explanation of Processing Steps

### 1. Dynamic File Parsing & Ingestion
* **Multi-Encoding Support:** Industrial machines often export logs using different character encodings (`utf-8`, `latin-1`, or `cp1252`). The pipeline automatically cycles through these encodings to read files without crashing.
* **Smart Delimiter Detection:** It scans incoming log rows to dynamically identify whether the data uses tabs, commas, or semicolons as column separators, ensuring robust ingestion across various machine export configurations.

### 2. Automated Part Numbering & Tracking
* **Suffix Extraction:** The script extracts the last few digits of the machine's serial number (e.g., parsing a serial string to isolate a unique identifier like `0174`).
* **Daily Counter Sequencing:** It combines the machine suffix with the compact production date (e.g., `260821` for August 21, 2026) and a daily tracking sequence to automatically generate unique component part numbers (e.g., `PART_0174_260821_00001`). This maintains full traceability of manufactured parts without exposing proprietary plant or database structures.

### 3. Signal Explosion (Time-Series Granularity)
* **Array Unpacking:** In raw machine exports, high-frequency telemetry readings (such as deformation, electrical current, or frequency over time) are often stored as a single comma-separated text string inside one cell.
* **Millisecond-Level Transformation:** The pipeline "explodes" these strings, transforming them into clean, individual rows indexed by millisecond steps. This structures the data perfectly for advanced time-series analysis and machine learning models.

### 4. Consumable Wear & Health Indexing (RUL)
* **Counter vs. Maximum Limits:** The script reads current usage counters against maximum allowable thresholds for critical machine consumables (such as wedges, guides, and cutters).
* **Percentage Health Metrics:** It calculates dynamic percentage-based Remaining Useful Life metrics (`Wedge_RUL_pct`, `Guide_RUL_pct`, `Cutter_RUL_pct`), providing vital predictive maintenance (PdM) insights.

---

## Requirements
* Python 3.8+
* `pandas`
* `pyarrow`