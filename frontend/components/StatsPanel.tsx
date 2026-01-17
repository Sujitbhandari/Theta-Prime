interface StatsPanelProps {
  ticker: string;
  spotPrice?: number;
  expiry?: string;
  opportunities?: any[];
  vix?: number;
  safetyScore?: number;
}

export default function StatsPanel({ ticker, spotPrice, expiry, opportunities, vix, safetyScore }: StatsPanelProps) {
  const avgWinProb = opportunities && opportunities.length > 0
    ? opportunities.reduce((sum, opp) => sum + (opp.win_prob * 100), 0) / opportunities.length
    : 0;

  const avgPremium = opportunities && opportunities.length > 0
    ? opportunities.reduce((sum, opp) => sum + opp.premium, 0) / opportunities.length
    : 0;

  const avgDelta = opportunities && opportunities.length > 0
    ? opportunities.reduce((sum, opp) => sum + Math.abs(opp.delta), 0) / opportunities.length
    : 0;

  const totalPremium = opportunities && opportunities.length > 0
    ? opportunities.reduce((sum, opp) => sum + opp.premium, 0)
    : 0;

  return (
    <div className="w-full h-[500px] bg-gradient-to-br from-black via-gray-950 to-black rounded-lg border border-white/10 p-6 overflow-y-auto">
      <h3 className="text-white font-mono font-bold text-lg mb-6">Market Analytics - {ticker}</h3>
      
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <div className="text-gray-400 text-xs font-mono mb-1">Current Price</div>
            <div className="text-white font-mono font-bold text-2xl">
              {spotPrice ? `$${spotPrice.toFixed(2)}` : '--'}
            </div>
          </div>

          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <div className="text-gray-400 text-xs font-mono mb-1">VIX Level</div>
            <div className={`font-mono font-bold text-2xl ${vix && vix < 18 ? 'text-emerald-400' : vix && vix <= 25 ? 'text-yellow-400' : 'text-red-400'}`}>
              {vix ? vix.toFixed(1) : '--'}
            </div>
          </div>

          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <div className="text-gray-400 text-xs font-mono mb-1">Safety Score</div>
            <div className={`font-mono font-bold text-2xl ${safetyScore && safetyScore >= 75 ? 'text-emerald-400' : safetyScore && safetyScore >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
              {safetyScore ? `${safetyScore.toFixed(1)}%` : '--'}
            </div>
          </div>

          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <div className="text-gray-400 text-xs font-mono mb-1">Avg Win Prob</div>
            <div className={`font-mono font-bold text-2xl ${avgWinProb >= 80 ? 'text-emerald-400' : avgWinProb >= 60 ? 'text-yellow-400' : 'text-gray-400'}`}>
              {avgWinProb > 0 ? `${avgWinProb.toFixed(1)}%` : '--'}
            </div>
          </div>
        </div>

        {opportunities && opportunities.length > 0 && (
          <>
            <div className="border-t border-white/10 pt-4 mt-4">
              <div className="text-gray-400 text-xs font-mono mb-3">Opportunity Metrics</div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                  <div className="text-gray-400 text-xs font-mono mb-1">Total Premium</div>
                  <div className="text-emerald-400 font-mono font-bold text-xl">
                    ${totalPremium.toFixed(2)}
                  </div>
                </div>

                <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                  <div className="text-gray-400 text-xs font-mono mb-1">Avg Premium</div>
                  <div className="text-white font-mono font-bold text-xl">
                    ${avgPremium.toFixed(2)}
                  </div>
                </div>

                <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                  <div className="text-gray-400 text-xs font-mono mb-1">Opportunities</div>
                  <div className="text-white font-mono font-bold text-xl">
                    {opportunities.length}
                  </div>
                </div>

                <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                  <div className="text-gray-400 text-xs font-mono mb-1">Avg Delta</div>
                  <div className="text-white font-mono font-bold text-xl">
                    {avgDelta > 0 ? avgDelta.toFixed(4) : '--'}
                  </div>
                </div>
              </div>
            </div>

            {expiry && (
              <div className="border-t border-white/10 pt-4 mt-4">
                <div className="text-gray-400 text-xs font-mono mb-1">Next Expiry</div>
                <div className="text-white font-mono text-sm">
                  {new Date(expiry).toLocaleDateString('en-US', { 
                    weekday: 'short', 
                    year: 'numeric', 
                    month: 'short', 
                    day: 'numeric' 
                  })}
                </div>
              </div>
            )}

            <div className="border-t border-white/10 pt-4 mt-4">
              <div className="text-gray-400 text-xs font-mono mb-3">Risk Assessment</div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-xs font-mono">Market Condition</span>
                  <span className={`text-xs font-mono font-bold ${vix && vix < 18 ? 'text-emerald-400' : vix && vix <= 25 ? 'text-yellow-400' : 'text-red-400'}`}>
                    {vix && vix < 18 ? 'SAFE' : vix && vix <= 25 ? 'CAUTION' : 'DANGER'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-xs font-mono">Strategy Suitability</span>
                  <span className={`text-xs font-mono font-bold ${avgWinProb >= 80 ? 'text-emerald-400' : avgWinProb >= 60 ? 'text-yellow-400' : 'text-gray-400'}`}>
                    {avgWinProb >= 80 ? 'HIGH' : avgWinProb >= 60 ? 'MODERATE' : 'LOW'}
                  </span>
                </div>
              </div>
            </div>
          </>
        )}

        {(!opportunities || opportunities.length === 0) && (
          <div className="border-t border-white/10 pt-6 mt-6 text-center">
            <div className="text-gray-500 text-sm font-mono">
              No opportunities found
            </div>
            <div className="text-gray-600 text-xs font-mono mt-2">
              Try a different ticker or adjust filters
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

