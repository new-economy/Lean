# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from clr import AddReference
AddReference("System")
AddReference("QuantConnect.Algorithm")
AddReference("QuantConnect.Common")
AddReference("QuantConnect.Indicators")

from System import *
from QuantConnect import *
from QuantConnect.Orders import *
from QuantConnect.Algorithm import *
from QuantConnect.Algorithm.Framework import *
from QuantConnect.Algorithm.Framework.Execution import *
from QuantConnect.Algorithm.Framework.Portfolio import *
from QuantConnect.Algorithm.Framework.Risk import *
from QuantConnect.Algorithm.Framework.Selection import *
from QuantConnect.Algorithm.Framework.Alphas import *
from datetime import timedelta
import numpy as np

class SimplePortfolioConstructionModel:
    def __init__(self):
        self.securities = [ ]

    def CreateTargets(self, algorithm, insights):
        if len(self.securities) == 0:
            return [ ]

        # give equal weighting to each security
        percent = 1.0 / len(self.securities)
        for insight in insights:
            yield PortfolioTarget.Percent(algorithm, insight.Symbol, insight.Direction * percent)

    def OnSecuritiesChanged(self, algorithm, changes):
        for added in changes.AddedSecurities:
            self.securities.append(added)
        for removed in changes.RemovedSecurities:
            if removed in self.securities:
                self.securities.remove(removed)