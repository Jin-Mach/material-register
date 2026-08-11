import pytest

from material_register.providers.language_provider import LanguageProvider


@pytest.mark.parametrize(
    "locale_return, expected",
    [("cs_CZ", "cs_CZ"), ("zu_ZA", "en_GB"), ("", "en_GB")],
    ids=["OS based language", "default language", "no locale"],
)
def test_set_language_code(locale_return, expected) -> None:
    result = LanguageProvider._set_language_code(locale_return)
    assert result == expected
