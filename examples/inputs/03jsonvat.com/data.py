from typing import List, Optional


class Data:
    details: str
    version: None
    rates: List['Rate']


class Rate:
    name: str
    code: str
    country_code: str
    periods: List['Period']


class Period:
    effective_from: str
    rates: 'Rate_1D'


class Rate_1D:
    standard: float
    super_reduced: Optional[float]
    reduced: Optional[float]
    reduced1: Optional[float]
    reduced2: Optional[float]
    parking: Optional[float]


