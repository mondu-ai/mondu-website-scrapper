""" Define util functions here"""
import os
import re
import string
from pathlib import Path
from typing import Union


def get_normalized_words(words: list[str]) -> list[str]:
    """
    normalize words by
    1. remove punctuation
    2. remove space
    3. lower words
    Returns: a list of normalized words
    """
    remove_pun = [
        word.translate(str.maketrans("", "", string.punctuation)).strip()
        for word in words
    ]

    return [word.lower() for word in remove_pun]


def get_normalized_price(
    data: str, allow_currency: list = None, allow_length: int = 10
) -> list[float]:
    """
    extract digits near the currency sign.
    This help functions aims to find all digits between 1 and 10 digits before and after

    Returns: a list of all digits near the currency sign
    """
    if allow_currency is None:
        allow_currency = ["€", "$"]
    target_currency = "|".join(allow_currency)
    search_pattern = (
        r"\d{1,%d}[\,\.]\d{1,%d}}(?=.*[%s])"  # pylint: disable=consider-using-f-string
        % (
            allow_length,
            allow_length,
            target_currency,
        )
    )
    price_lst = re.findall(search_pattern, data)
    return [float(p.strip().replace(",", ".")) for p in price_lst]


def extract_categories_from_wappalyzer(wappalyzed_categories: dict) -> dict:
    """
    refactor dict out of wappalyzer.analyze_with_categories function.
    before construct:
    wappalyzer output data = {'Apache': {'categories': ['Web servers']},
                'Google Font API': {'categories': ['Font scripts']},
                'MySQL': {'categories': ['Databases']}}
    after refactor:
    data = {'Web servers': 'Apache',
            'Font scripts': 'Google Font API'},
            'Databases': 'MySQL'
            }

    Returns: a Python dict
    """
    categories_dict = {}
    for key, value in wappalyzed_categories.items():
        for i in value["categories"]:
            if i not in categories_dict:
                categories_dict.update({i: [key] for i in value["categories"]})
            else:
                categories_dict[i].append(key)
    refactor_d = {key: list(set(value)) for key, value in categories_dict.items()}
    return {key: ", ".join(value) for key, value in refactor_d.items()}


def is_empty_file(file_path: Union[Path, str]) -> bool:
    """Check if file is empty by confirming if its size is 0 bytes"""

    return os.path.exists(file_path) and os.stat(file_path).st_size == 0
