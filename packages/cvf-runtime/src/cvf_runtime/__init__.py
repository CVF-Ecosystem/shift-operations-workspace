"""CVF runtime: turns the static CVF application profile into enforced gates.

This package is self-contained inside the workspace. It reads the YAML policy
files under ``packages/cvf-application-profile/`` and exposes the control chain
(identity, permission, risk, approval, evidence, audit, refusal) as callable
gates the API layer wires into request handlers.

It intentionally does NOT import anything from the CVF framework root repo;
the workspace stays isolated and portable.
"""

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.audit import AuditRecord, AuditLog

__all__ = ["CvfDenied", "Principal", "AuditRecord", "AuditLog"]
