"""GovernedRetrievalRequestV1 and closed request contracts (SPEC R2).

Pure package module: standard library + Pydantic + ``retrieval_contracts``
imports only. No I/O, clock, id, secret, environment, auth, Ledger, API,
network, provider, or audit access. This module performs strict field/type
validation only; it never resolves a corpus or touches protected state.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Annotated

from pydantic import Field, model_validator
from retrieval_contracts.enums import RecordType, TruthClass

from .enums import CorpusId
from .model_base import StrictModel
from .lexical import normalize_and_tokenize_query

_SAFE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")

_MAX_QUERY_CODEPOINTS = 512
_MAX_QUERY_UTF8_BYTES = 4096
_MAX_QUERY_TOKENS = 64

# R8 server maxima (also re-declared in projection.py for the projection
# path; kept identical by construction and cross-checked by tests).
_MAX_CONTEXT_RECORDS = 4
_MAX_SNIPPET_CODEPOINTS = 1024
_MAX_SNIPPET_UTF8_BYTES = 3072
_MAX_SERIALIZED_UTF8_BYTES = 16384
_MAX_ESTIMATED_INPUT_TOKENS = 4096

_LIFECYCLE_STATUSES = frozenset(
    {
        "CONFIRMED",
        "CORRECTED",
        "FROZEN",
        "ACKNOWLEDGED",
        "MITIGATING",
        "RESOLVED",
        "CLOSED",
        "REVIEWED",
        "APPROVED",
        "CURRENT",
    }
)


class RequestValidationError(ValueError):
    """Carries a closed R2 :class:`RequestFailureCode` value."""

    def __init__(self, code) -> None:
        self.code = code
        super().__init__(str(code))


def normalize_query(raw_query: str):
    """R2 query preprocessing. Returns the normalized query string.

    Raises :class:`RequestValidationError` with the exact R2 code on failure.
    Strict Unicode decode is assumed already satisfied by Python's ``str``
    type (a caller supplying non-decodable bytes has already failed at the
    transport boundary); this function still rejects NUL, unpaired
    surrogates, and any Unicode ``Cc`` control character.
    """
    from .enums import RequestFailureCode

    if not isinstance(raw_query, str):
        raise RequestValidationError(RequestFailureCode.QUERY_INVALID)
    try:
        raw_query.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise RequestValidationError(RequestFailureCode.QUERY_INVALID) from exc
    if "\x00" in raw_query:
        raise RequestValidationError(RequestFailureCode.QUERY_INVALID)
    for ch in raw_query:
        if 0xD800 <= ord(ch) <= 0xDFFF:
            raise RequestValidationError(RequestFailureCode.QUERY_INVALID)
    # CRLF/CR -> LF canonicalization.
    text = raw_query.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse Unicode whitespace runs to a single ASCII space, trim edges.
    collapsed: list[str] = []
    prev_space = False
    for ch in text:
        if ch.isspace():
            if not prev_space:
                collapsed.append(" ")
            prev_space = True
        else:
            collapsed.append(ch)
            prev_space = False
    normalized = "".join(collapsed).strip(" ")

    if not normalized:
        raise RequestValidationError(RequestFailureCode.QUERY_INVALID)
    for ch in normalized:
        if unicodedata.category(ch) == "Cc":
            raise RequestValidationError(RequestFailureCode.QUERY_INVALID)

    codepoints = len(normalized)
    if codepoints < 1 or codepoints > _MAX_QUERY_CODEPOINTS:
        raise RequestValidationError(RequestFailureCode.QUERY_LIMIT_EXCEEDED)
    byte_length = len(normalized.encode("utf-8"))
    if byte_length > _MAX_QUERY_UTF8_BYTES:
        raise RequestValidationError(RequestFailureCode.QUERY_LIMIT_EXCEEDED)
    tokens = normalize_and_tokenize_query(normalized)
    if len(tokens) > _MAX_QUERY_TOKENS:
        raise RequestValidationError(RequestFailureCode.QUERY_LIMIT_EXCEEDED)
    return normalized


def _sorted_unique(values: tuple[str, ...]) -> None:
    from .enums import RequestFailureCode

    if tuple(sorted(values)) != values or len(set(values)) != len(values):
        raise RequestValidationError(RequestFailureCode.FILTER_INVALID)


def _to_tuple_or_invalid(value):
    """JSON-wire-safe coercion: a normal JSON array (Python ``list``) or an
    already-built ``tuple`` becomes a tuple; anything else (a bare string,
    mapping, scalar, or other non-sequence) is rejected as ``FILTER_INVALID``
    instead of falling through to a strict-mode ``tuple_type`` error or an
    unrelated raw exception downstream."""
    from .enums import RequestFailureCode

    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    raise RequestValidationError(RequestFailureCode.FILTER_INVALID)


class RetrievalFiltersV1(StrictModel):
    """R2 - exactly four closed narrowing filters."""

    shift_ids: tuple[str, ...] = Field(default=(), max_length=2)
    record_types: tuple[RecordType, ...] = Field(default=())
    truth_classes: tuple[TruthClass, ...] = Field(default=())
    lifecycle_statuses: tuple[str, ...] = Field(default=())

    @model_validator(mode="before")
    @classmethod
    def _coerce_enum_strings(cls, value):
        # Wire JSON supplies plain strings for enum fields and plain JSON
        # arrays (Python lists) for every tuple field; strict mode accepts
        # neither by default. This validator normalizes both: every malformed
        # shape (wrong element type, unknown enum value, non-array field, an
        # unhashable/unsortable element) raises the exact closed
        # FILTER_INVALID code - never a raw TypeError/ValueError escapes past
        # this boundary.
        from .enums import RequestFailureCode

        if not isinstance(value, dict):
            return value
        coerced = dict(value)
        try:
            if "shift_ids" in coerced and coerced["shift_ids"] is not None:
                shift_ids = _to_tuple_or_invalid(coerced["shift_ids"])
                for shift_id in shift_ids:
                    if not isinstance(shift_id, str) or not _SAFE_ID_PATTERN.match(shift_id):
                        raise RequestValidationError(RequestFailureCode.FILTER_INVALID)
                coerced["shift_ids"] = shift_ids
            if "record_types" in coerced and coerced["record_types"] is not None:
                record_types = _to_tuple_or_invalid(coerced["record_types"])
                coerced["record_types"] = tuple(
                    RecordType(v) if isinstance(v, str) else v for v in record_types
                )
            if "truth_classes" in coerced and coerced["truth_classes"] is not None:
                truth_classes = _to_tuple_or_invalid(coerced["truth_classes"])
                coerced["truth_classes"] = tuple(
                    TruthClass(v) if isinstance(v, str) else v for v in truth_classes
                )
            if "lifecycle_statuses" in coerced and coerced["lifecycle_statuses"] is not None:
                lifecycle_statuses = _to_tuple_or_invalid(coerced["lifecycle_statuses"])
                for status in lifecycle_statuses:
                    if not isinstance(status, str):
                        raise RequestValidationError(RequestFailureCode.FILTER_INVALID)
                coerced["lifecycle_statuses"] = lifecycle_statuses
        except RequestValidationError:
            raise
        except (TypeError, ValueError) as exc:
            raise RequestValidationError(RequestFailureCode.FILTER_INVALID) from exc
        return coerced

    @model_validator(mode="after")
    def _sorted_and_unique(self) -> "RetrievalFiltersV1":
        from .enums import RequestFailureCode

        try:
            _sorted_unique(self.shift_ids)
            _sorted_unique(tuple(str(v) for v in self.record_types))
            _sorted_unique(tuple(str(v) for v in self.truth_classes))
            _sorted_unique(self.lifecycle_statuses)
        except TypeError as exc:
            # sorted()/set() over an unsortable/unhashable mix - closed R2
            # code, never a raw TypeError.
            raise RequestValidationError(RequestFailureCode.FILTER_INVALID) from exc
        for status in self.lifecycle_statuses:
            if status not in _LIFECYCLE_STATUSES:
                raise RequestValidationError(RequestFailureCode.FILTER_INVALID)
        return self


class ContextBudgetV1(StrictModel):
    """R2 - client-requested ceilings, each positive and <= the R8 server
    maximum for that field."""

    max_projection_records: Annotated[int, Field(ge=1, strict=True)]
    max_snippet_codepoints: Annotated[int, Field(ge=1, strict=True)]
    max_snippet_utf8_bytes: Annotated[int, Field(ge=1, strict=True)]
    max_serialized_utf8_bytes: Annotated[int, Field(ge=1, strict=True)]
    max_estimated_input_tokens: Annotated[int, Field(ge=1, strict=True)]

    @model_validator(mode="after")
    def _within_server_maxima(self) -> "ContextBudgetV1":
        from .enums import RequestFailureCode

        checks = (
            (self.max_projection_records, _MAX_CONTEXT_RECORDS),
            (self.max_snippet_codepoints, _MAX_SNIPPET_CODEPOINTS),
            (self.max_snippet_utf8_bytes, _MAX_SNIPPET_UTF8_BYTES),
            (self.max_serialized_utf8_bytes, _MAX_SERIALIZED_UTF8_BYTES),
            (self.max_estimated_input_tokens, _MAX_ESTIMATED_INPUT_TOKENS),
        )
        for requested, maximum in checks:
            if isinstance(requested, bool) or requested > maximum:
                raise RequestValidationError(RequestFailureCode.CONTEXT_BUDGET_INVALID)
        return self


class GovernedRetrievalRequestV1(StrictModel):
    """R2 - the exact external request body. Rejects unknown fields.

    ``correlation_id`` is deliberately absent: the SPEC forbids the client
    from supplying one. The application layer generates the server-side
    ``retrieval_correlation_id``.
    """

    contract_version: str = Field(default="1.0", pattern=r"^1\.0$")
    query: str = Field(min_length=1)
    # Deliberately a plain safe-shaped ``str``, NOT ``CorpusId``: resolving
    # registry membership is an R3 stage-5 concern (only after every R3
    # authorization stage passes). Typing this field as the closed enum
    # would make Pydantic reject/accept based on registry validity during
    # stage-1 structural parsing, disclosing corpus existence before
    # authorization (R2/R3 boundary; see admission.RequestInvalid's
    # post-authorization CORPUS_ID_INVALID/FILTER_WIDENS_SCOPE handling).
    corpus_id: str = Field(min_length=1, max_length=128)
    filters: RetrievalFiltersV1 = Field(default_factory=RetrievalFiltersV1)
    result_limit: Annotated[int, Field(ge=1, le=20, strict=True)] = 10
    context_budget: ContextBudgetV1

    @model_validator(mode="before")
    @classmethod
    def _normalize_query(cls, value):
        if not isinstance(value, dict):
            return value
        coerced = dict(value)
        # R2 query preprocessing runs here, before the strict field
        # validator, so QUERY_INVALID/QUERY_LIMIT_EXCEEDED are raised with
        # their exact codes and the stored ``query`` is always the
        # normalized form, never the raw wire value.
        if isinstance(coerced.get("query"), str):
            coerced["query"] = normalize_query(coerced["query"])
        return coerced

    @model_validator(mode="after")
    def _validate_shape_only_cardinality(self) -> "GovernedRetrievalRequestV1":
        from .enums import RequestFailureCode

        if isinstance(self.result_limit, bool):
            raise RequestValidationError(RequestFailureCode.RESULT_LIMIT_INVALID)
        if not _SAFE_ID_PATTERN.match(self.corpus_id):
            raise RequestValidationError(RequestFailureCode.CORPUS_ID_INVALID)
        # Shape-only cardinality: without knowing which real corpus this is
        # (that resolution happens only after R3 authorization), the widest
        # permitted shape is 1-2 shift ids; the exact per-corpus cardinality
        # (exactly one for Project Knowledge) is re-checked post-authorization
        # by the application layer once the corpus is actually resolved.
        shift_count = len(self.filters.shift_ids)
        if shift_count < 1 or shift_count > 2:
            raise RequestValidationError(RequestFailureCode.FILTER_INVALID)
        return self
