"""
Unit tests for core/code_executor.py

Tests cover:
- Execution of code that produces a new DataFrame
- Execution of code that produces a Figure (Matplotlib and Plotly)
- Execution of code with print() produces text output
- Execution of code that errors produces output_type="error" with traceback
- Blocking dangerous module imports

Requirements: 5.5, 5.6, 6.1, 7.2, 7.5
"""

from __future__ import annotations

import pandas as pd
import pytest

from core.code_executor import execute


# ---------------------------------------------------------------------------
# Sample DataFrame used across tests
# ---------------------------------------------------------------------------

SAMPLE_DF = pd.DataFrame(
    {
        "name": ["Alice", "Bob", "Charlie"],
        "value": [10, 20, 30],
        "score": [95.5, 87.0, 92.3],
    }
)


# ---------------------------------------------------------------------------
# DataFrame output tests
# ---------------------------------------------------------------------------


class TestDataFrameOutput:
    """Tests for code that produces a modified DataFrame."""

    def test_assign_new_column_produces_dataframe_output(self):
        """Code that adds a column via assign() should return output_type='dataframe'."""
        code = "df = df.assign(new_col=1)"
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "dataframe"
        assert isinstance(result["data"], pd.DataFrame)

    def test_new_column_is_present_in_result(self):
        """The resulting DataFrame should contain the newly added column."""
        code = "df = df.assign(new_col=1)"
        result = execute(code, SAMPLE_DF.copy())
        assert "new_col" in result["data"].columns

    def test_direct_column_assignment_produces_dataframe_output(self):
        """Direct column assignment (df['col'] = ...) should return output_type='dataframe'."""
        code = "df['extra'] = 99"
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "dataframe"
        assert "extra" in result["data"].columns

    def test_original_dataframe_not_mutated(self):
        """The original DataFrame passed to execute() must not be mutated."""
        original = SAMPLE_DF.copy()
        code = "df = df.assign(new_col=1)"
        execute(code, original)
        assert "new_col" not in original.columns

    def test_dataframe_output_error_is_none(self):
        """Successful DataFrame execution should have error=None."""
        code = "df = df.assign(new_col=1)"
        result = execute(code, SAMPLE_DF.copy())
        assert result["error"] is None

    def test_execution_time_is_positive(self):
        """execution_time_ms should be a positive float."""
        code = "df = df.assign(new_col=1)"
        result = execute(code, SAMPLE_DF.copy())
        assert result["execution_time_ms"] >= 0.0


# ---------------------------------------------------------------------------
# Figure output tests — Matplotlib
# ---------------------------------------------------------------------------


class TestMatplotlibFigureOutput:
    """Tests for code that produces a Matplotlib figure."""

    def test_matplotlib_figure_produces_figure_output(self):
        """Code that creates a Matplotlib figure should return output_type='figure'."""
        code = (
            "import matplotlib.pyplot as plt\n"
            "fig, ax = plt.subplots()\n"
            "ax.plot([1, 2, 3])\n"
        )
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "figure"

    def test_matplotlib_figure_data_is_figure_instance(self):
        """The data field should be a matplotlib Figure instance."""
        import matplotlib.figure

        code = (
            "import matplotlib.pyplot as plt\n"
            "fig, ax = plt.subplots()\n"
            "ax.plot([1, 2, 3])\n"
        )
        result = execute(code, SAMPLE_DF.copy())
        assert isinstance(result["data"], matplotlib.figure.Figure)

    def test_matplotlib_figure_error_is_none(self):
        """Successful figure execution should have error=None."""
        code = (
            "import matplotlib.pyplot as plt\n"
            "fig, ax = plt.subplots()\n"
            "ax.bar(['A', 'B', 'C'], [1, 2, 3])\n"
        )
        result = execute(code, SAMPLE_DF.copy())
        assert result["error"] is None


# ---------------------------------------------------------------------------
# Figure output tests — Plotly
# ---------------------------------------------------------------------------


class TestPlotlyFigureOutput:
    """Tests for code that produces a Plotly figure."""

    def test_plotly_figure_produces_figure_output(self):
        """Code that creates a Plotly figure should return output_type='figure'."""
        code = (
            "import plotly.express as px\n"
            "fig = px.bar(df, x='name', y='value')\n"
        )
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "figure"

    def test_plotly_figure_data_is_figure_instance(self):
        """The data field should be a plotly Figure instance."""
        import plotly.graph_objs

        code = (
            "import plotly.express as px\n"
            "fig = px.bar(df, x='name', y='value')\n"
        )
        result = execute(code, SAMPLE_DF.copy())
        assert isinstance(result["data"], plotly.graph_objs.Figure)

    def test_plotly_scatter_produces_figure_output(self):
        """Plotly scatter chart should also return output_type='figure'."""
        code = (
            "import plotly.express as px\n"
            "fig = px.scatter(df, x='value', y='score')\n"
        )
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "figure"


# ---------------------------------------------------------------------------
# Text output tests (print)
# ---------------------------------------------------------------------------


class TestTextOutput:
    """Tests for code that produces text output via print()."""

    def test_print_produces_text_output(self):
        """Code with print() should return output_type='text'."""
        code = "print('hello world')"
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "text"

    def test_print_content_in_stdout(self):
        """The printed content should appear in the stdout field."""
        code = "print('hello world')"
        result = execute(code, SAMPLE_DF.copy())
        assert "hello world" in result["stdout"]

    def test_print_content_in_data(self):
        """The data field should contain the printed text."""
        code = "print('test output')"
        result = execute(code, SAMPLE_DF.copy())
        assert "test output" in result["data"]

    def test_multiple_prints_captured(self):
        """Multiple print() calls should all be captured in stdout."""
        code = "print('line1')\nprint('line2')\nprint('line3')"
        result = execute(code, SAMPLE_DF.copy())
        assert "line1" in result["stdout"]
        assert "line2" in result["stdout"]
        assert "line3" in result["stdout"]

    def test_print_error_is_none(self):
        """Successful print execution should have error=None."""
        code = "print('hello')"
        result = execute(code, SAMPLE_DF.copy())
        assert result["error"] is None


# ---------------------------------------------------------------------------
# Error output tests
# ---------------------------------------------------------------------------


class TestErrorOutput:
    """Tests for code that raises exceptions."""

    def test_exception_produces_error_output(self):
        """Code that raises an exception should return output_type='error'."""
        code = "raise ValueError('test error')"
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "error"

    def test_error_field_contains_traceback(self):
        """The error field should contain the traceback string."""
        code = "raise ValueError('test error')"
        result = execute(code, SAMPLE_DF.copy())
        assert result["error"] is not None
        assert "ValueError" in result["error"]
        assert "test error" in result["error"]

    def test_data_field_contains_error_message(self):
        """The data field should contain a descriptive error message."""
        code = "raise ValueError('test error')"
        result = execute(code, SAMPLE_DF.copy())
        assert "ValueError" in result["data"]

    def test_name_error_produces_error_output(self):
        """NameError (undefined variable) should produce output_type='error'."""
        code = "result = undefined_variable + 1"
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "error"
        assert "NameError" in result["error"]

    def test_syntax_error_produces_error_output(self):
        """SyntaxError in code should produce output_type='error'."""
        code = "def broken(:\n    pass"
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "error"

    def test_execute_never_raises(self):
        """execute() must never raise an exception to the caller."""
        code = "raise RuntimeError('should not propagate')"
        # This should not raise
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "error"

    def test_zero_division_produces_error_output(self):
        """ZeroDivisionError should produce output_type='error'."""
        code = "x = 1 / 0"
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "error"
        assert "ZeroDivisionError" in result["error"]


# ---------------------------------------------------------------------------
# Blocked import tests
# ---------------------------------------------------------------------------


class TestBlockedImports:
    """Tests for dangerous module import blocking."""

    def test_import_os_is_blocked(self):
        """Importing 'os' should produce output_type='error'."""
        code = "import os"
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "error"

    def test_import_sys_is_blocked(self):
        """Importing 'sys' should produce output_type='error'."""
        code = "import sys"
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "error"

    def test_import_subprocess_is_blocked(self):
        """Importing 'subprocess' should produce output_type='error'."""
        code = "import subprocess"
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "error"

    def test_import_shutil_is_blocked(self):
        """Importing 'shutil' should produce output_type='error'."""
        code = "import shutil"
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "error"

    def test_import_socket_is_blocked(self):
        """Importing 'socket' should produce output_type='error'."""
        code = "import socket"
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "error"

    def test_blocked_import_error_message_is_descriptive(self):
        """The error message for blocked imports should mention the module name."""
        code = "import os"
        result = execute(code, SAMPLE_DF.copy())
        assert result["error"] is not None
        assert "os" in result["error"]

    def test_safe_import_is_allowed(self):
        """Importing safe modules like 'math' should be allowed."""
        code = "import math\nresult = math.sqrt(4)\nprint(result)"
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "text"
        assert "2.0" in result["stdout"]


# ---------------------------------------------------------------------------
# ExecutionResult structure tests
# ---------------------------------------------------------------------------


class TestExecutionResultStructure:
    """Tests verifying the structure of ExecutionResult."""

    def test_result_has_output_type(self):
        """ExecutionResult must always have an output_type field."""
        result = execute("print('hi')", SAMPLE_DF.copy())
        assert "output_type" in result

    def test_result_has_data(self):
        """ExecutionResult must always have a data field."""
        result = execute("print('hi')", SAMPLE_DF.copy())
        assert "data" in result

    def test_result_has_stdout(self):
        """ExecutionResult must always have a stdout field."""
        result = execute("print('hi')", SAMPLE_DF.copy())
        assert "stdout" in result

    def test_result_has_error(self):
        """ExecutionResult must always have an error field."""
        result = execute("print('hi')", SAMPLE_DF.copy())
        assert "error" in result

    def test_result_has_execution_time_ms(self):
        """ExecutionResult must always have an execution_time_ms field."""
        result = execute("print('hi')", SAMPLE_DF.copy())
        assert "execution_time_ms" in result

    def test_output_type_is_valid_literal(self):
        """output_type must be one of the four valid literals."""
        valid_types = {"dataframe", "figure", "text", "error"}
        for code in [
            "print('hi')",
            "raise ValueError('err')",
            "df = df.assign(x=1)",
        ]:
            result = execute(code, SAMPLE_DF.copy())
            assert result["output_type"] in valid_types

    def test_no_output_code_produces_text(self):
        """Code with no output should produce output_type='text' with default message."""
        code = "x = 1 + 1"
        result = execute(code, SAMPLE_DF.copy())
        assert result["output_type"] == "text"
