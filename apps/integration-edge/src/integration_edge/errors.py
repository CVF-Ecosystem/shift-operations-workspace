"""Fail-closed Integration Edge exception taxonomy."""


class IntegrationEdgeError(Exception):
    """Base class safe for coarse internal classification."""


class ContractViolation(IntegrationEdgeError):
    pass


class VerificationRefused(IntegrationEdgeError):
    pass


class ReplayRefused(VerificationRefused):
    pass


class KeyUnavailable(IntegrationEdgeError):
    pass


class EncryptionRefused(IntegrationEdgeError):
    pass


class MatrixDriftError(ContractViolation):
    pass
