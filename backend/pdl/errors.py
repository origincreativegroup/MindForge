class PDLError(Exception):
    """Base class for PDL related errors."""


class PDLParseError(PDLError):
    """Raised when parsing fails."""


class PDLSemanticError(PDLError):
    """Raised for semantic issues."""
