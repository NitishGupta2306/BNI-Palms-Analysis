"""Application-wide constants."""

from enum import Enum


class SlipType(Enum):
    """Types of slips in PALMS data."""
    REFERRAL = "Referral"
    ONE_TO_ONE = "One to One"
    TYFCB = "TYFCB"


class ExcelColumns(Enum):
    """Standard Excel column positions for PALMS data."""
    GIVER_NAME = 0  # Column A
    RECEIVER_NAME = 1  # Column B
    SLIP_TYPE = 2  # Column C
    TYFCB_AMOUNT = 4  # Column E
    DETAIL = 6  # Column G


class MatrixHeaders:
    """Standard headers for matrix exports."""
    GIVER_RECEIVER = "Giver \\ Receiver"
    TOTAL_REFERRALS_GIVEN = "Total Referrals Given:"
    UNIQUE_REFERRALS_GIVEN = "Unique Referrals Given:"
    TOTAL_REFERRALS_RECEIVED = "Total Referrals Received:"
    UNIQUE_REFERRALS_RECEIVED = "Unique Referrals Received:"
    TOTAL_OTO = "Total OTO:"
    UNIQUE_OTO = "Unique OTO:"
    NEITHER = "Neither:"
    OTO_ONLY = "OTO only:"
    REFERRAL_ONLY = "Referral only:"
    OTO_AND_REFERRAL = "OTO and Referral:"
    CURRENT_REFERRAL = "Current Referral:"
    LAST_REFERRAL = "Last Referral:"
    CHANGE_IN_REFERRALS = "Change in Referrals:"
    LAST_NEITHER = "Last Neither:"
    CHANGE_IN_NEITHER = "Change in Neither:"


class CombinationValues:
    """Values used in combination matrix."""
    NEITHER = 0  # No OTO and no referral
    OTO_ONLY = 1  # OTO but no referral
    REFERRAL_ONLY = 2  # Referral but no OTO
    BOTH = 3  # Both OTO and referral


class FileNames:
    """Standard file names for reports."""
    REFERRAL_MATRIX = "referral_matrix.xlsx"
    OTO_MATRIX = "OTO_matrix.xlsx"
    COMBINATION_MATRIX = "combination_matrix.xlsx"
    COMBINATION_COMPARISON = "combination_matrix_comparison.xlsx"


class StreamlitConfig:
    """Streamlit-specific configuration."""
    PAGE_TITLE = "BNI Palms Analysis"
    PAGE_ICON = ":material/partner_exchange:"
    LAYOUT = "wide"
    
    # File uploader settings
    MAX_FILE_SIZE_MB = 200
    ALLOWED_TYPES = ["xls", "xlsx"]


class ValidationMessages:
    """Standard validation and error messages."""
    INVALID_MEMBER_NAME = "Member name cannot be empty"
    SELF_REFERRAL_ERROR = "A member cannot refer to themselves"
    SELF_OTO_ERROR = "A member cannot have a one-to-one with themselves"
    FILE_NOT_FOUND = "File not found: {}"
    INVALID_FILE_FORMAT = "Invalid file format. Expected: {}"
    PROCESSING_ERROR = "Error processing file: {}"
    MATRIX_GENERATION_ERROR = "Error generating matrix: {}"
    EXPORT_ERROR = "Error exporting data: {}"