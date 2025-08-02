"""Custom exceptions for the BNI Palms Analysis domain."""


class BNIAnalysisException(Exception):
    """Base exception for BNI Analysis domain errors."""
    pass


class MemberValidationError(BNIAnalysisException):
    """Raised when member data validation fails."""
    pass


class ReferralValidationError(BNIAnalysisException):
    """Raised when referral data validation fails."""
    pass


class OneToOneValidationError(BNIAnalysisException):
    """Raised when one-to-one data validation fails."""
    pass


class MatrixGenerationError(BNIAnalysisException):
    """Raised when matrix generation fails."""
    pass


class DataProcessingError(BNIAnalysisException):
    """Raised when data processing fails."""
    pass


class FileProcessingError(BNIAnalysisException):
    """Raised when file processing fails."""
    pass


class ConfigurationError(BNIAnalysisException):
    """Raised when configuration is invalid."""
    pass


class ExportError(BNIAnalysisException):
    """Raised when exporting data fails."""
    pass