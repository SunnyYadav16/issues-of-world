# ruff: noqa: E501  (real titles kept verbatim)
import pytest

from iow.core.headline import clean_headline

# (title as GDELT stored it, expected). Real titles from the first-slice store; None means drop the item.
CASES = [
    ("From young hearts to hidden symptoms, Assam steps up awareness on cardiac risks | Guwahati News",
     "From young hearts to hidden symptoms, Assam steps up awareness on cardiac risks"),
    ("First time since 1947, Dibrugarh back on river trade map; to ship methanol to B'desh | Guwahati News",
     "First time since 1947, Dibrugarh back on river trade map; to ship methanol to B'desh"),
    ("Assembly adjourned sine die | Bhubaneswar News - The Times of India", "Assembly adjourned sine die"),
    ("Cong stages protest over alleged SIR irregularities | Varanasi News",
     "Cong stages protest over alleged SIR irregularities"),
    ("Surprise check in Handia, Hanumanganj: BDO faces salary cut | Prayagraj News",
     "Surprise check in Handia, Hanumanganj: BDO faces salary cut"),
    ("Travel agent booked for fraud - The Tribune", "Travel agent booked for fraud"),
    ("Priest thrashed over Loud Bhajans at Jaipur temple, CCTV captures attack | Indiablooms - First Portal on Digital News Management",
     "Priest thrashed over Loud Bhajans at Jaipur temple, CCTV captures attack"),
    ("Omar Abdullah's statehood push blocked? J&K bureaucrats write to Speaker; CM hits back | Indiablooms",
     "Omar Abdullah's statehood push blocked? J&K bureaucrats write to Speaker; CM hits back"),
    ("Amit Shah launches new Extradition Portal – The Indian Awaaz", "Amit Shah launches new Extradition Portal"),
    ("Philippine Airlines Expands Australia–India Connectivity with New Delhi and First-Ever Mumbai Services – Indus Age",
     "Philippine Airlines Expands Australia–India Connectivity with New Delhi and First-Ever Mumbai Services"),
    ("Kashmir, India changing: Farooq - Daily Excelsior", "Kashmir, India changing: Farooq"),
    ("ECI and the Gandhi Test of Public Integrity | The Shillong Times", "ECI and the Gandhi Test of Public Integrity"),
    ("Delhi slap row: NCR against minister Verma, FIR against AAP MLA Jarnail | Rediff-TV",
     "Delhi slap row: NCR against minister Verma, FIR against AAP MLA Jarnail"),
    ("Two dozen children vs Pablo Escobar's hippo: The legal battle to get to a Colombian school | International",
     "Two dozen children vs Pablo Escobar's hippo: The legal battle to get to a Colombian school"),
    # nothing headline-like left: dropped
    ("Ubiquitous drones - Taipei Times", None),
    ("Forest Clearance Gridlock - Daily Excelsior", None),
    ("Meghalaya Nuggets | The Shillong Times", None),
    ("The Times of India", None),
    ("Indiablooms - First Portal on Digital News Management", None),
    ("   ", None),
    # left alone: a long segment after a pipe is a sub-headline, not an outlet
    ("Suo Motu Case On Delhi Rapes | Supreme Court Issues Directions To Make Public Spaces Safer; Orders Safety Audit Within 4 Weeks",
     "Suo Motu Case On Delhi Rapes | Supreme Court Issues Directions To Make Public Spaces Safer; Orders Safety Audit Within 4 Weeks"),
    ("Navratri Navadurga Havan | Nine Navadurga Homams during Navaratri",
     "Navratri Navadurga Havan | Nine Navadurga Homams during Navaratri"),
    ("Ludhiana: 4 women pickpockets arrested", "Ludhiana: 4 women pickpockets arrested"),
    ("Best NIRF Management Colleges in 2026: Ranking, Admission, Fees & Placement",
     "Best NIRF Management Colleges in 2026: Ranking, Admission, Fees & Placement"),
    ("Minal Bibi & Ors vs The State Of West Bengal & Ors on 25 September, 2026",
     "Minal Bibi & Ors vs The State Of West Bengal & Ors on 25 September, 2026"),
    ("Waqf Board Review Pending Cases", "Waqf Board Review Pending Cases"),
    ("Friends again, through trade", "Friends again, through trade"),
    ("LankaWeb – Is Sallay Conspiring with the CIA to Implement the Stated US Objective (Part 2)",
     "LankaWeb – Is Sallay Conspiring with the CIA to Implement the Stated US Objective (Part 2)"),
    # whitespace and entities
    ("Aditya A. Shriram  &  Prashant J. Mahale re-elected as President  &  Vice President of AMAI",
     "Aditya A. Shriram & Prashant J. Mahale re-elected as President & Vice President of AMAI"),
    ("Rain &amp; floods hit Mumbai", "Rain & floods hit Mumbai"),
]  # fmt: skip


@pytest.mark.parametrize(("title", "expected"), CASES)
def test_clean_headline(title, expected):
    assert clean_headline(title) == expected
