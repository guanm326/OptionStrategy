from enum import Enum
import pandas as pd
import numpy as np
from typing import List, Union
import math
import datetime
import typing


class CloseSignal(Enum):
    CLOSE_ALL = 1
    CLOSE_PARTIAL = 2
    FLASE = -1