import pytest

from .query_helpers import parse_hp, parse_rarity, parse_type


# test parse_hp function with valid inputs
def test_parse_hp_with_valid_inputs():
    # test valid input for hp
    assert parse_hp("50") == "50"
    assert parse_hp("50 to 100") == "[50 TO 100]"
    assert parse_hp("* to 100") == "[* TO 100]"
    assert parse_hp("50 to *") == "[50 TO *]"


# test parse_hp function with invalid inputs
def test_parse_hp_with_invalid_inputs():
    # test invalid input for hp
    with pytest.raises(ValueError):
        parse_hp("50 - 100")
    with pytest.raises(ValueError):
        parse_hp("abc")


# test parse_rarity function with single rarity input
def test_parse_rarity_with_single_rarity():
    assert parse_rarity("Rare Holo") == ["rare holo"]


# test parse_rarity function with OR condition input
def test_parse_rarity_with_or_condition():
    assert set(parse_rarity("Rare Holo or Uncommon")) == {"rare holo", "uncommon"}
    assert set(parse_rarity("Rare Holo or Rare Ultra or Common or Uncommon")) == {"rare holo", "rare ultra", "common",
                                                                                  "uncommon"}
    assert set(parse_rarity("Rare Holo or Rare Ultra or Common or Uncommon or Rare Shiny GX")) == {"rare holo",
                                                                                                   "rare ultra",
                                                                                                   "common", "uncommon",
                                                                                                   "rare shiny gx"}


# test parse_rarity function with NOT condition input
def test_parse_rarity_with_not_condition():
    expected = ["rare secret", "rare rainbow", "rare shiny gx", "rare shining",
                "rare shiny", "amazing rare", "rare prime", "rare ace", "rare break",
                "rare prism star", "legend", "promo", "rare ultra", "common", "uncommon"]
    actual = parse_rarity("Not Rare Holo")

    assert len(actual) == len(expected)

    for i in range(len(expected)):
        assert actual[i] in expected


# test parse_rarity function with invalid input
def test_parse_rarity_with_invalid_inputs():
    with pytest.raises(ValueError):
        parse_rarity("Rare Holo and Ultra Rare")



# test parse_type function with single type input
def test_parse_type_with_single_type():
    assert parse_type("Fire") == ["fire"]
    assert parse_type("Fairy") == ["fairy"]
    with pytest.raises(ValueError):
        parse_type("abc")


# test parse_type function with OR condition input
def test_parse_type_with_or_condition():
    assert sorted(parse_type("Fire or Water")) == sorted(["fire", "water"])
    assert sorted(parse_type("Fire or Water or Grass")) == sorted(["fire", "water", "grass"])
    assert sorted(parse_type("Not Fire or Water")) == sorted(["normal", "water", "electric", "grass", "ice", "fighting", "poison",
                                               "ground", "flying", "psychic", "bug", "rock", "ghost", "dragon", "dark",
                                               "steel", "fairy"])


# test parse_type function with NOT condition input
def test_parse_type_with_not_condition():
    assert sorted(parse_type("Not Fire")) == sorted(["normal", "water", "electric", "grass", "ice", "fighting", "poison", "ground", "flying", "psychic", "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy"])


# test parse_type function with invalid input
def test_parse_type_with_invalid_inputs():
    with pytest.raises(ValueError):
        parse_type("Fire and Water")
    with pytest.raises(ValueError):
        parse_type("Fire xor Water")
    with pytest.raises(ValueError):
        parse_type("Fire or")
    with pytest.raises(ValueError):
        parse_type("Fire or ")


if __name__ == "__main__":
    pytest.main()