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
from Execution.ImmediateExecutionModel import ImmediateExecutionModel
from Portfolio.SimplePortfolioConstructionModel import SimplePortfolioConstructionModel
from Risk.MaximumDrawdownPercentPerSecurity import MaximumDrawdownPercentPerSecurity
from Selection.FundamentalPortfolioSelectionModel import FundamentalPortfolioSelectionModel
from Alphas.MacdAlphaModel import MacdAlphaModel
from QuantConnect.Data.UniverseSelection import *
from datetime import timedelta
import numpy as np

### <summary>
### This example algorithm defines its own custom coarse/fine fundamental selection model
### combined with the MACD alpha model.
### </summary>
### <meta name="tag" content="using data" />
### <meta name="tag" content="using quantconnect" />
### <meta name="tag" content="trading and orders" />
class CustomFrameworkModelsAlgorithm(QCAlgorithmFramework):

    def Initialize(self):

        # Set requested data resolution
        self.UniverseSettings.Resolution = Resolution.Minute

        self.SetStartDate(2013,10,7)   #Set Start Date
        self.SetEndDate(2013,10,11)    #Set End Date
        self.SetCash(100000)           #Set Strategy Cash

        self.SetPortfolioSelection(CustomFundamentalPortfolioSelectionModel(True, None, None))
        self.SetAlpha(MacdAlphaModel(timedelta(minutes = 10), timedelta(minutes = 30), 0.01))
        self.SetPortfolioConstruction(SimplePortfolioConstructionModel())
        self.SetExecution(ImmediateExecutionModel())
        self.SetRiskManagement(MaximumDrawdownPercentPerSecurity(1.01))

    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status == OrderStatus.Filled:
            self.Debug("Purchased Stock: {}".format(orderEvent.Symbol))


class CustomFundamentalPortfolioSelectionModel(FundamentalPortfolioSelectionModel):
    def SelectCoarse(self, algorithm, coarse):
        coarse = filter(lambda c: c.HasFundamentalData if self.filterFineData else c, coarse)
        sortedByDollarVolume = sorted(coarse, key=lambda c: c.DollarVolume, reverse=True)
        return [ x.Symbol for x in sortedByDollarVolume[:100] ]

    def SelectFine(self, algorithm, fine):
        sortedByEarningYield = sorted(fine, key=lambda f: f.ValuationRatios.EarningYield, reverse=True)
        return [ x.Symbol for x in sortedByEarningYield[:20] ]