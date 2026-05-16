"""
Unit tests for core/gemini_client.py

Tests cover:
- _extract_code_block() with various response formats
  (with code block, without code block, multiple blocks)
- generate_code() with mock successful response
- Error handling for InvalidArgument and ResourceExhausted

All tests that call the Gemini API use mocks to avoid real API calls.

Requirements: 5.2, 5.4
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import google.api_core.exceptions


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_client(api_key: str = "test-api-key") -> "GeminiClient":
    """Create a GeminiClient with mocked google.generativeai to avoid real API calls."""
    with (
        patch("google.generativeai.configure"),
        patch("google.generativeai.GenerativeModel") as mock_model_cls,
    ):
        mock_model_cls.return_value = MagicMock()
        from core.gemini_client import GeminiClient
        client = GeminiClient(api_key=api_key)
    return client


# ---------------------------------------------------------------------------
# _extract_code_block — code block extraction
# ---------------------------------------------------------------------------


class TestExtractCodeBlock:
    """Tests for GeminiClient._extract_code_block()."""

    def setup_method(self):
        """Create a client instance for each test (no real API calls)."""
        self.client = _make_client()

    def test_extracts_simple_code_block(self):
        """A single ```python ... ``` block should be extracted correctly."""
        response = "Here is the code:\n```python\nprint('hello')\n```"
        result = self.client._extract_code_block(response)
        assert result == "print('hello')"

    def test_extracts_multiline_code_block(self):
        """Multi-line code inside a block should be extracted fully."""
        response = (
            "```python\n"
            "import pandas as pd\n"
            "df = df.assign(new_col=1)\n"
            "print(df.head())\n"
            "```"
        )
        result = self.client._extract_code_block(response)
        assert "import pandas as pd" in result
        assert "df = df.assign(new_col=1)" in result
        assert "print(df.head())" in result

    def test_returns_empty_string_when_no_code_block(self):
        """Response without a code block should return an empty string."""
        response = "I cannot generate code for this request."
        result = self.client._extract_code_block(response)
        assert result == ""

    def test_returns_empty_string_for_empty_response(self):
        """Empty response string should return an empty string."""
        result = self.client._extract_code_block("")
        assert result == ""

    def test_strips_leading_trailing_whitespace(self):
        """Extracted code should be stripped of leading/trailing whitespace."""
        response = "```python\n\n  x = 1\n\n```"
        result = self.client._extract_code_block(response)
        assert result == "x = 1"

    def test_extracts_first_block_when_multiple_present(self):
        """When multiple code blocks exist, the first one should be extracted."""
        response = (
            "First block:\n"
            "```python\n"
            "x = 1\n"
            "```\n"
            "Second block:\n"
            "```python\n"
            "y = 2\n"
            "```"
        )
        result = self.client._extract_code_block(response)
        assert "x = 1" in result
        # Should not contain the second block's content
        assert "y = 2" not in result

    def test_returns_empty_string_for_non_python_code_block(self):
        """A code block without 'python' language tag should not be extracted."""
        response = "```\nsome code\n```"
        result = self.client._extract_code_block(response)
        assert result == ""

    def test_extracts_code_with_comments(self):
        """Code block containing comments should be extracted correctly."""
        response = (
            "```python\n"
            "# This is a comment\n"
            "df = df.assign(x=1)  # inline comment\n"
            "```"
        )
        result = self.client._extract_code_block(response)
        assert "# This is a comment" in result
        assert "df = df.assign(x=1)" in result

    def test_extracts_code_with_imports(self):
        """Code block with import statements should be extracted correctly."""
        response = (
            "```python\n"
            "import matplotlib.pyplot as plt\n"
            "fig, ax = plt.subplots()\n"
            "ax.plot([1, 2, 3])\n"
            "```"
        )
        result = self.client._extract_code_block(response)
        assert "import matplotlib.pyplot as plt" in result
        assert "fig, ax = plt.subplots()" in result

    def test_does_not_include_markdown_fences(self):
        """The extracted code must not contain the ``` markers."""
        response = "```python\nprint('hello')\n```"
        result = self.client._extract_code_block(response)
        assert "```" not in result
        assert "python" not in result.split("\n")[0]


# ---------------------------------------------------------------------------
# generate_code — successful response
# ---------------------------------------------------------------------------


class TestGenerateCodeSuccess:
    """Tests for GeminiClient.generate_code() with mocked successful responses."""

    def _make_client_with_mock_model(self):
        """Create a GeminiClient where self.model is a MagicMock."""
        with (
            patch("google.generativeai.configure"),
            patch("google.generativeai.GenerativeModel") as mock_model_cls,
        ):
            mock_model_instance = MagicMock()
            mock_model_cls.return_value = mock_model_instance
            from core.gemini_client import GeminiClient
            client = GeminiClient(api_key="test-key")
        return client, mock_model_instance

    def test_returns_code_on_success(self):
        """generate_code() should return (code, None) on a successful response."""
        client, mock_model = self._make_client_with_mock_model()

        mock_response = MagicMock()
        mock_response.text = "```python\ndf = df.assign(new_col=1)\n```"
        mock_model.generate_content.return_value = mock_response

        code, error = client.generate_code("add a new column", {"columns": ["a", "b"]})

        assert error is None
        assert code is not None
        assert "df = df.assign(new_col=1)" in code

    def test_returns_none_error_on_success(self):
        """The error field should be None on a successful response."""
        client, mock_model = self._make_client_with_mock_model()

        mock_response = MagicMock()
        mock_response.text = "```python\nprint('hello')\n```"
        mock_model.generate_content.return_value = mock_response

        code, error = client.generate_code("print hello", {})

        assert error is None

    def test_returns_none_code_when_no_code_block(self):
        """When the response has no code block, code should be None and error set."""
        client, mock_model = self._make_client_with_mock_model()

        mock_response = MagicMock()
        mock_response.text = "I cannot help with that."
        mock_model.generate_content.return_value = mock_response

        code, error = client.generate_code("some prompt", {})

        assert code is None
        assert error is not None

    def test_generate_content_called_with_prompt(self):
        """generate_content should be called with a non-empty prompt string."""
        client, mock_model = self._make_client_with_mock_model()

        mock_response = MagicMock()
        mock_response.text = "```python\nprint('hi')\n```"
        mock_model.generate_content.return_value = mock_response

        client.generate_code("test prompt", {"columns": ["x"]})

        mock_model.generate_content.assert_called_once()
        call_args = mock_model.generate_content.call_args[0][0]
        assert isinstance(call_args, str)
        assert len(call_args) > 0

    def test_return_type_is_tuple(self):
        """generate_code() must always return a tuple of two elements."""
        client, mock_model = self._make_client_with_mock_model()

        mock_response = MagicMock()
        mock_response.text = "```python\nprint('hi')\n```"
        mock_model.generate_content.return_value = mock_response

        result = client.generate_code("test", {})

        assert isinstance(result, tuple)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# generate_code — error handling
# ---------------------------------------------------------------------------


class TestGenerateCodeErrorHandling:
    """Tests for GeminiClient.generate_code() error handling."""

    def _make_client_with_mock_model(self):
        """Create a GeminiClient where self.model is a MagicMock."""
        with (
            patch("google.generativeai.configure"),
            patch("google.generativeai.GenerativeModel") as mock_model_cls,
        ):
            mock_model_instance = MagicMock()
            mock_model_cls.return_value = mock_model_instance
            from core.gemini_client import GeminiClient
            client = GeminiClient(api_key="test-key")
        return client, mock_model_instance

    def test_invalid_argument_returns_error_message(self):
        """InvalidArgument exception should return (None, descriptive_error)."""
        client, mock_model = self._make_client_with_mock_model()

        mock_model.generate_content.side_effect = (
            google.api_core.exceptions.InvalidArgument("bad key")
        )

        code, error = client.generate_code("test", {})

        assert code is None
        assert error is not None
        assert isinstance(error, str)
        assert len(error) > 0

    def test_invalid_argument_error_mentions_api_key(self):
        """InvalidArgument error message should mention API key."""
        client, mock_model = self._make_client_with_mock_model()

        mock_model.generate_content.side_effect = (
            google.api_core.exceptions.InvalidArgument("bad key")
        )

        _, error = client.generate_code("test", {})

        # The error message should be informative about the API key
        assert "API" in error or "key" in error.lower() or "Key" in error

    def test_resource_exhausted_returns_error_message(self):
        """ResourceExhausted exception should return (None, descriptive_error)."""
        client, mock_model = self._make_client_with_mock_model()

        mock_model.generate_content.side_effect = (
            google.api_core.exceptions.ResourceExhausted("quota exceeded")
        )

        code, error = client.generate_code("test", {})

        assert code is None
        assert error is not None
        assert isinstance(error, str)
        assert len(error) > 0

    def test_resource_exhausted_error_mentions_quota(self):
        """ResourceExhausted error message should mention quota."""
        client, mock_model = self._make_client_with_mock_model()

        mock_model.generate_content.side_effect = (
            google.api_core.exceptions.ResourceExhausted("quota exceeded")
        )

        _, error = client.generate_code("test", {})

        assert "kuota" in error.lower() or "quota" in error.lower() or "Kuota" in error

    def test_generic_exception_returns_error_message(self):
        """Any unexpected exception should return (None, descriptive_error)."""
        client, mock_model = self._make_client_with_mock_model()

        mock_model.generate_content.side_effect = Exception("unexpected error")

        code, error = client.generate_code("test", {})

        assert code is None
        assert error is not None

    def test_error_handling_never_raises(self):
        """generate_code() must never raise an exception to the caller."""
        client, mock_model = self._make_client_with_mock_model()

        mock_model.generate_content.side_effect = RuntimeError("crash")

        # Should not raise
        result = client.generate_code("test", {})
        assert isinstance(result, tuple)
