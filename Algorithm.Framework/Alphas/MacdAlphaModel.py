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
from QuantConnect.Util import PythonUtil
from QuantConnect.Orders import *
from QuantConnect.Indicators import *
from QuantConnect.Algorithm import *
from QuantConnect.Algorithm.Framework import *
from QuantConnect.Data.UniverseSelection import *
from datetime import timedelta
import numpy as np

class MacdAlphaModel:
    def __init__(self, insightPeriod, consolidatorPeriod, bounceThresholdPercent):
        self.insightPeriod = insightPeriod
        self.consolidatorPeriod = consolidatorPeriod
        self.bounceThresholdPercent = abs(bounceThresholdPercent)
        self.symbolData = { };

    def Update(self, algorithm, data):

        for key, sd in self.symbolData.items():
            if sd.Security.Price == 0:
                continue

            direction = InsightDirection.Flat
            normalized_signal = sd.MACD.Signal.Current.Value / sd.Security.Price
            if normalized_signal > self.bounceThresholdPercent:
                direction = InsightDirection.Up
            elif normalized_signal < -self.bounceThresholdPercent:
                direction = InsightDirection.Down

            insight = Insight(sd.Security.Symbol, InsightType.Price, direction, self.insightPeriod)
            if insight == sd.previous_insight:
                continue

            sd.previous_insight = insight.Clone()

            yield insight


    def OnSecuritiesChanged(self, algorithm, changes):

        for added in changes.AddedSecurities:
            self.symbolData[added.Symbol] = SymbolData(algorithm, added, self.consolidatorPeriod)

        for removed in changes.RemovedSecurities:
            data = self.symbolData.get(removed.Symbol)
            if data is not None:
                data.CleanUp(algorithm)
                self.symbolData.pop(removed.Symbol)

class SymbolData:
    def __init__(self, algorithm, security, period):
        self.Security = security
        self.Consolidator = algorithm.ResolveConsolidator(security.Symbol, period)
        algorithm.SubscriptionManager.AddConsolidator(security.Symbol, self.Consolidator)

        self.MACD = MovingAverageConvergenceDivergence(12, 26, 9, MovingAverageType.Exponential)
        self.Consolidator.DataConsolidated += self.OnDataConsolidated

        self.previous_insight = None

    def OnDataConsolidated(self, sender, consolidated):
        self.MACD.Update(consolidated.EndTime, consolidated.Value)

    def CleanUp(self, algorithm):
        self.Consolidator.DataConsolidated -= self.OnDataConsolidated
        algorithm.SubscriptionManager.RemoveConsolidator(self.Security.Symbol, self.Consolidator)