"""
Performance-Instrumented Fabric User Data Function Template

This template provides a reusable pattern for creating User Data Functions
with built-in performance monitoring, structured logging, and timeout awareness.

Usage:
    Copy this template as your function_app.py starting point. Customize the
    function implementations while keeping the performance instrumentation.

Service Limits Reference:
    - Execution timeout: 240 seconds
    - Response size limit: 30 MB
    - Request payload: 4 MB
    - Daily log ingestion: 250 MB
"""

import datetime
import json
import logging
import sys
import time
from functools import wraps

import fabric.functions as fn

udf = fn.UserDataFunctions()

# ---------------------------------------------------------------------------
# Performance Constants
# ---------------------------------------------------------------------------
EXECUTION_TIMEOUT_SECONDS = 240
TIMEOUT_WARN_THRESHOLD = 0.75  # Warn at 75% of timeout
RESPONSE_SIZE_WARN_BYTES = 25 * 1024 * 1024  # 25 MB warning threshold
RESPONSE_SIZE_LIMIT_BYTES = 30 * 1024 * 1024  # 30 MB hard limit


# ---------------------------------------------------------------------------
# Performance Instrumentation Decorator
# ---------------------------------------------------------------------------
def perf_monitor(func):
    """
    Decorator that adds performance monitoring to a UDF function.

    Logs:
        - Function start and end with total duration
        - Warning if approaching timeout threshold
        - Response size estimate
        - Error details with duration context
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        start_time = time.perf_counter()

        logging.info(f"PERF|{func_name}|start|{datetime.datetime.utcnow().isoformat()}Z")

        try:
            result = func(*args, **kwargs)

            duration_ms = (time.perf_counter() - start_time) * 1000
            duration_s = duration_ms / 1000

            # Log duration
            logging.info(f"PERF|{func_name}|complete|{duration_ms:.0f}ms")

            # Warn if approaching timeout
            if duration_s > EXECUTION_TIMEOUT_SECONDS * TIMEOUT_WARN_THRESHOLD:
                logging.warning(
                    f"PERF|{func_name}|timeout_risk|"
                    f"{duration_s:.1f}s of {EXECUTION_TIMEOUT_SECONDS}s limit"
                )

            # Estimate and log response size
            try:
                if result is not None:
                    size_estimate = sys.getsizeof(
                        json.dumps(result) if not isinstance(result, str) else result
                    )
                    logging.info(
                        f"PERF|{func_name}|response_size|"
                        f"{size_estimate / (1024 * 1024):.2f}MB"
                    )
                    if size_estimate > RESPONSE_SIZE_WARN_BYTES:
                        logging.warning(
                            f"PERF|{func_name}|response_size_risk|"
                            f"{size_estimate / (1024 * 1024):.2f}MB "
                            f"approaching {RESPONSE_SIZE_LIMIT_BYTES / (1024 * 1024):.0f}MB limit"
                        )
            except (TypeError, OverflowError):
                pass  # Skip size estimation for non-serializable results

            return result

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logging.error(
                f"PERF|{func_name}|error|{duration_ms:.0f}ms|{type(exc).__name__}: {exc}"
            )
            raise

    return wrapper


# ---------------------------------------------------------------------------
# Phase Timer Context Manager
# ---------------------------------------------------------------------------
class PhaseTimer:
    """
    Context manager for timing individual phases within a function.

    Usage:
        with PhaseTimer("data_retrieval", "get_products"):
            data = fetch_products()

        with PhaseTimer("processing", "transform_data"):
            result = transform(data)
    """

    def __init__(self, phase: str, function_name: str = ""):
        self.phase = phase
        self.function_name = function_name
        self.start_time = 0.0
        self.duration_ms = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration_ms = (time.perf_counter() - self.start_time) * 1000
        prefix = f"{self.function_name}|" if self.function_name else ""

        if exc_type is not None:
            logging.error(
                f"PERF|{prefix}{self.phase}|error|{self.duration_ms:.0f}ms|"
                f"{exc_type.__name__}: {exc_val}"
            )
        else:
            logging.info(f"PERF|{prefix}{self.phase}|{self.duration_ms:.0f}ms")

        return False  # Do not suppress exceptions


# ---------------------------------------------------------------------------
# Example Functions
# ---------------------------------------------------------------------------

@udf.function()
@perf_monitor
def health_check() -> str:
    """
    Lightweight health check function for warm-up scheduling.
    Call this from a Pipeline on a schedule to prevent cold starts.
    """
    return json.dumps({
        "status": "OK",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "python_version": sys.version
    })


@udf.function()
@perf_monitor
def example_simple_function(name: str) -> str:
    """
    Example simple function with performance monitoring.
    The @perf_monitor decorator handles all instrumentation automatically.
    """
    return f"Hello, {name}! Timestamp: {datetime.datetime.utcnow().isoformat()}Z"


# Uncomment and customize the following for data source functions:
#
# @udf.connection(argName="myWarehouse", alias="<Your-Warehouse-Alias>")
# @udf.function()
# @perf_monitor
# def example_warehouse_query(
#     myWarehouse: fn.FabricSqlConnection,
#     category: str,
#     max_rows: int
# ) -> str:
#     """
#     Example warehouse query function with phase-level timing.
#     """
#     max_rows = min(max_rows, 1000)  # Cap to prevent oversized responses
#     conn = None
#
#     try:
#         with PhaseTimer("connect", "example_warehouse_query"):
#             conn = myWarehouse.connect()
#             cursor = conn.cursor()
#
#         with PhaseTimer("query", "example_warehouse_query"):
#             cursor.execute(
#                 "SELECT Id, Name, Price "
#                 "FROM Products "
#                 "WHERE Category = ? "
#                 "ORDER BY Id "
#                 "OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY",
#                 (category, max_rows)
#             )
#             columns = [c[0] for c in cursor.description]
#             rows = cursor.fetchall()
#
#         with PhaseTimer("serialize", "example_warehouse_query"):
#             results = []
#             for row in rows:
#                 item = {}
#                 for col, val in zip(columns, row):
#                     if isinstance(val, (datetime.date, datetime.datetime)):
#                         val = val.isoformat()
#                     item[col] = val
#                 results.append(item)
#
#         logging.info(f"PERF|example_warehouse_query|rows_returned|{len(results)}")
#         return json.dumps(results)
#
#     finally:
#         if conn:
#             conn.close()
#
#
# @udf.connection(argName="myLakehouse", alias="<Your-Lakehouse-Alias>")
# @udf.function()
# @perf_monitor
# def example_lakehouse_read(
#     myLakehouse: fn.FabricLakehouseClient,
#     filename: str
# ) -> str:
#     """
#     Example lakehouse CSV reader with phase-level timing.
#     Uses lazy import for pandas to minimize cold start impact.
#     """
#     connection = None
#
#     try:
#         with PhaseTimer("connect", "example_lakehouse_read"):
#             connection = myLakehouse.connectToFiles()
#             file_client = connection.get_file_client(filename)
#
#         with PhaseTimer("download", "example_lakehouse_read"):
#             download = file_client.download_file()
#             raw_data = download.readall()
#             logging.info(
#                 f"PERF|example_lakehouse_read|file_size|"
#                 f"{len(raw_data) / (1024 * 1024):.2f}MB"
#             )
#
#         with PhaseTimer("parse", "example_lakehouse_read"):
#             import pandas as pd  # Lazy import
#             from io import StringIO
#             df = pd.read_csv(
#                 StringIO(raw_data.decode('utf-8')),
#                 nrows=10000  # Safety limit
#             )
#
#         with PhaseTimer("serialize", "example_lakehouse_read"):
#             result = df.to_json(orient='records')
#
#         logging.info(f"PERF|example_lakehouse_read|rows_parsed|{len(df)}")
#         return result
#
#     finally:
#         if connection:
#             connection.close()
