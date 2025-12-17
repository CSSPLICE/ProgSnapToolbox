from abc import ABC, abstractmethod
from typing import Any, Dict, Final, List, Optional, Set, Tuple
from pandas import DataFrame, Series
import pandas as pd
import numpy as np
import re
import os
import subprocess
import json
import tempfile
from pathlib import Path


class CodeMetricsProcessor(ABC):
    """
    Abstract class for code metrics.
    """
    @abstractmethod
    def calculate(self, rows: DataFrame) -> DataFrame:
        ...

    @abstractmethod
    def parallel_calculate(self, rows: DataFrame) -> DataFrame:
        ...

    @abstractmethod
    def code_metrics_columns(self) -> list[str]:
        ...


class PythonCodeMetricsProcessor(CodeMetricsProcessor):
    RAW_COLUMNS = [
        "loc",
        "lloc",
        "sloc",
        "comments",
    ]

    HAL_COLUMNS = [
        "h1",
        "h2",
        "N1",
        "N2",
        "vocabulary",
        "length",
        "calculated_length",
        "volume",
        "difficulty",
        "effort",
        "time",
        "bugs",
    ]


    # Output/error columns
    ERROR = "error"
    RAW_ERROR = "raw_error"
    CC_ERROR = "cc_error"
    HAL_ERROR = "hal_error"

    CC_OUTPUT = "cc_output"
    AVG_CC = "avg_cc"


    def code_metrics_columns(self) -> list[str]:
        return self.RAW_COLUMNS + self.HAL_COLUMNS + [self.AVG_CC]

    def __init__(self, code_col):
        self.code_col = code_col

    def _process_code(self, code: str) -> dict[str, Any]:
        return self._analyze_code(code)

    def calculate(self, rows: DataFrame) -> DataFrame:
        metrics = rows[self.code_col].apply(self._process_code)
        return pd.json_normalize(metrics)

    def parallel_calculate(self, rows: DataFrame) -> DataFrame:
        try:
            from pandarallel import pandarallel

            pandarallel.initialize(progress_bar=True)

            metrics = rows[self.code_col].parallel_apply(self._process_code)
            return pd.json_normalize(metrics)

        except ImportError:
            return self.calculate(rows)

    def _analyze_code(
        self,
        code: str,
        timeout: int = 15,
    ) -> dict[str, Any]:

        if not code or not code.strip():
            return {
                self.ERROR: "empty_code"
            }

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(code)
            path = f.name

        try:
            result = {}

            result.update(self._run_raw(path, timeout))
            result.update(self._run_cc(path, timeout))
            result.update(self._run_halstead(path, timeout))

            return result

        finally:
            try:
                os.unlink(path)
            except OSError:
                pass

    def _run_raw(
        self,
        path: str,
        timeout: int,
    ) -> dict[str, Any]:

        try:
            proc = subprocess.run(
                [
                    "radon",
                    "raw",
                    "-j",
                    path,
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if proc.returncode != 0:
                return {
                    self.RAW_ERROR: proc.stderr.strip()
                }

            metrics = json.loads(proc.stdout).get(path, {})

            return {
                key: metrics[key]
                for key in self.RAW_COLUMNS
                if key in metrics
            }

        except subprocess.TimeoutExpired:
            return {
                self.RAW_ERROR: "timeout"
            }

        except Exception as e:
            return {
                self.RAW_ERROR: str(e)
            }

    def _run_cc(
        self,
        path: str,
        timeout: int,
    ) -> dict[str, Any]:

        try:
            proc = subprocess.run(
                [
                    "radon",
                    "cc",
                    "-s",
                    "--total-average",
                    path,
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if proc.returncode != 0:
                return {
                    self.CC_ERROR: proc.stderr.strip()
                }

            return {
                self.CC_OUTPUT: proc.stdout,
                self.AVG_CC: self._extract_cc_average(proc.stdout) or 0,
            }

        except subprocess.TimeoutExpired:
            return {
                self.CC_ERROR: "timeout"
            }

        except Exception as e:
            return {
                self.CC_ERROR: str(e)
            }

    def _run_halstead(
        self,
        path: str,
        timeout: int,
    ) -> dict[str, Any]:

        try:
            proc = subprocess.run(
                [
                    "radon",
                    "hal",
                    "-j",
                    path,
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if proc.returncode != 0:
                return {
                    self.HAL_ERROR: proc.stderr.strip()
                }

            total = (
                json.loads(proc.stdout)
                .get(path, {})
                .get("total", {})
            )

            return {
                key: total.get(key, 0)
                for key in self.HAL_COLUMNS
            }

        except subprocess.TimeoutExpired:
            return {
                self.HAL_ERROR: "timeout"
            }

        except Exception as e:
            return {
                self.HAL_ERROR: str(e)
            }

    @staticmethod
    def _extract_cc_average(cc_output: str) -> Optional[float]:
        match = re.search(
            r"Average complexity: ([A-Z]) \((\d+\.\d+)\)",
            cc_output,
        )

        if match:
            return float(match.group(2))

        return None


class JavaCodeMetricsProcessor(CodeMetricsProcessor):
    SCC_COLUMNS = ["Lines", "Code", "Comments", "Blanks", "Complexity"]
    HAL_COLUMNS = [
        "Vocabulary",
        "n1",
        "N1",
        "n2",
        "N2",
        "Difficulty",
        "Effort",
        "Programming time",
        "Estimated program length",
        "Length",
        "Volume",
        "Purity ratio",
    ]

    ERROR = "error"


    def code_metrics_columns(self) -> list[str]:
        return self.SCC_COLUMNS + self.HAL_COLUMNS

    # https://github.com/SoftengPoliTo/Halstead-Metrics-Tool
    def __init__(self, code_col, code_id_col, base_dir=None, jar_file="Halstead-Metrics.jar"):
        self.code_col = code_col
        self.code_id_col = code_id_col
        self.base_dir = Path(base_dir) if base_dir else None
        self.jar_file = jar_file

    def _process_row(self, row):
        return self._analyze_code(
            row[self.code_col],
            row[self.code_id_col],
        )

    def calculate(self, rows: DataFrame):
        return pd.concat(rows.apply(self._process_row, axis=1).tolist(), ignore_index=True)

    def parallel_calculate(self, rows: DataFrame):
        try:
            from pandarallel import pandarallel

            pandarallel.initialize(progress_bar=True)
            return pd.concat(
                rows.parallel_apply(self._process_row, axis=1).tolist(),
                ignore_index=True,
            )

        except ImportError:
            return self.calculate(rows)
    
    def _error_df(self, error: str, tool: str | None = None, details: str | None = None) -> DataFrame:
            row = {self.ERROR: error}
            if tool is not None:
                row["tool"] = tool
            if details:
                row["details"] = details
            return pd.DataFrame([row])

    def _analyze_code(
        self,
        code: str,
        code_id: str,
        timeout: int = 15,
    ) -> DataFrame | dict[str, Any]:

        
        if not code or not code.strip():
            return pd.DataFrame([{self.ERROR: "empty_code"}])
        
        with tempfile.TemporaryDirectory(dir=self.base_dir) as tmp_dir:
            work_dir = Path(tmp_dir)

            java_file = work_dir / f"{code_id}.java"
            
            try:
                with java_file.open("w", encoding="utf-8") as f:
                    f.write(code)

                scc = self._run_scc_tool(java_file, timeout)
                if self.ERROR in scc.columns:
                    return scc

                hal = self._run_halstead(java_file, timeout)
                if self.ERROR in hal.columns:
                    return hal

                return pd.concat(
                    [
                        scc.reset_index(drop=True),
                        hal.reset_index(drop=True),
                    ],
                    axis=1,
                )

            except subprocess.TimeoutExpired:
                return self._error_df("timeout")

            except Exception as e:
                return self._error_df("exception", details=str(e))

            finally:
                for suffix in (".java", ".csv", ".json"):
                    java_file.with_suffix(suffix).unlink(missing_ok=True)

    def _run_scc_tool(self, path: Path, timeout: int = 15) -> DataFrame:
        output_file = path.with_suffix(".csv")

        try:
            result = subprocess.run(
                [
                    "scc",
                    "--format-multi",
                    f"csv:{output_file}",
                    str(path),
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode != 0:
                return self._error_df(
                    "scc_error",
                    tool="scc",
                    details=result.stderr.strip(),
                )

            return (
                pd.read_csv(output_file)[self.SCC_COLUMNS]
                .reset_index(drop=True)
            )

        except subprocess.TimeoutExpired:
            return self._error_df("timeout", tool="scc")

        except Exception as e:
            return self._error_df(
                "scc_error",
                tool="scc",
                details=str(e),
            )

    def _run_halstead(self, path: Path, timeout: int = 15) -> DataFrame:
        output_file = path.with_suffix(".json")

        try:
            result = subprocess.run(
                ["java", "-jar", self.jar_file, str(path)],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode != 0:
                return self._error_df(
                    "halstead_error",
                    tool="halstead",
                    details=result.stderr.strip(),
                )

            raw_metrics = json.loads(result.stdout)

            with output_file.open("w", encoding="utf-8") as f:
                json.dump(raw_metrics, f, indent=4)

            halstead = {
                k: raw_metrics["Halstead"][k]
                for k in self.HAL_COLUMNS
                if k in raw_metrics["Halstead"]
            }

            return pd.json_normalize(halstead)

        except subprocess.TimeoutExpired:
            return self._error_df("timeout", tool="halstead")

        except Exception as e:
            return self._error_df(
                "halstead_error",
                tool="halstead",
                details=str(e),
            )
