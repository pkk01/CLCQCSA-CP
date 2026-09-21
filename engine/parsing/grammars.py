from tree_sitter import Language
import tree_sitter_java
import tree_sitter_python

SUPPORTED_LANGUAGES = ("python", "java")

_LANGUAGE_CAPSULES = {
    "python": tree_sitter_python.language(),
    "java": tree_sitter_java.language(),
}


def get_language(language: str) -> Language:
    """Return a loaded tree-sitter grammar for a supported language."""
    try:
        return Language(_LANGUAGE_CAPSULES[language])
    except KeyError as error:
        supported = ", ".join(SUPPORTED_LANGUAGES)
        raise ValueError(
            f"{language!r} is not a supported language (supported: {supported})"
        ) from error
