interface StatsPanelProps {
  ticker: string;
  spotPrice?: number;
  expiry?: string;
  opportunities?: {
    strike: number;
    expiry: string;
    premium: number;
    win_prob: number;
    delta: number;
    gamma: number;
    theta: number;
    vega: number;
    iv: number;
  }[];
  vix?: number;
  safetyScore?: number;
}

function ProgressBar({ value, max = 100, color }: { value: number; max?: number; color: string }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  return (
    <div className="w-full bg-white/10 rounded-full h-1.5 mt-1.5">
      <div
        className={`h-1.5 rounded-full transition-all duration-500 ${color}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

function StatCard({
  label,
  value,
  sub,
  barValue,
  barColor,
}: {
  label: string;
  value: string;
  sub?: string;
  barValue?: number;
  barColor?: string;
}) {
  return (
    <div className="bg-white/5 rounded-lg p-4 border border-white/10">
      <div className="text-gray-400 text-xs font-mono mb-1">{label}</div>
      <div className="font-mono font-bold text-2xl text-white">{value}</div>
      {sub && <div className="text-gray-500 text-xs font-mono mt-0.5">{sub}</div>}
      {barValue !== undefined && barColor && (
        <ProgressBar value={barValue} color={barColor} />
      )}
    </div>
  );
}

export default function StatsPanel({
  ticker,
  spotPrice,
  expiry,
  opportunities,
  vix,
  safetyScore,
}: StatsPanelProps) {
  const count = opportunities?.length ?? 0;

  const avgWinProb =
    count > 0
      ? opportunities!.reduce((s, o) => s + o.win_prob * 100, 0) / count
      : 0;

  const avgPremium =
    count > 0
      ? opportunities!.reduce((s, o) => s + o.premium, 0) / count
      : 0;

  const avgDelta =
    count > 0
      ? opportunities!.reduce((s, o) => s + Math.abs(o.delta), 0) / count
      : 0;

  const totalPremium =
    count > 0 ? opportunities!.reduce((s, o) => s + o.premium, 0) : 0;

  const vixColor =
    vix === undefined
      ? "text-gray-400"
      : vix < 18
      ? "text-emerald-400"
      : vix <= 25
      ? "text-yellow-400"
      : "text-red-400";

  const safetyColor =
    safetyScore === undefined
      ? "text-gray-400"
      : safetyScore >= 75
      ? "text-emerald-400"
      : safetyScore >= 50
      ? "text-yellow-400"
      : "text-red-400";

  const winColor =
    avgWinProb >= 80
      ? "bg-emerald-500"
      : avgWinProb >= 60
      ? "bg-yellow-500"
      : "bg-gray-500";

  const safetyBarColor =
    (safetyScore ?? 0) >= 75
      ? "bg-emerald-500"
      : (safetyScore ?? 0) >= 50
      ? "bg-yellow-500"
      : "bg-red-500";

  return (
    <div className="w-full h-[500px] bg-gradient-to-br from-black via-gray-950 to-black rounded-lg border border-white/10 p-6 overflow-y-auto">
      <h3 className="text-white font-mono font-bold text-lg mb-6">
        Market Analytics — {ticker}
      </h3>

      <div className="space-y-4">
        {/* Primary stats */}
        <div className="grid grid-cols-2 gap-4">
          <StatCard
            label="Current Price"
            value={spotPrice ? `$${spotPrice.toFixed(2)}` : "—"}
          />

          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <div className="text-gray-400 text-xs font-mono mb-1">VIX Level</div>
            <div className={`font-mono font-bold text-2xl ${vixColor}`}>
              {vix ? vix.toFixed(1) : "—"}
            </div>
            {vix && (
              <ProgressBar
                value={vix}
                max={50}
                color={
                  vix < 18
                    ? "bg-emerald-500"
                    : vix <= 25
                    ? "bg-yellow-500"
                    : "bg-red-500"
                }
              />
            )}
          </div>

          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <div className="text-gray-400 text-xs font-mono mb-1">Safety Score</div>
            <div className={`font-mono font-bold text-2xl ${safetyColor}`}>
              {safetyScore ? `${safetyScore.toFixed(1)}%` : "—"}
            </div>
            {safetyScore !== undefined && (
              <ProgressBar value={safetyScore} color={safetyBarColor} />
            )}
          </div>

          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <div className="text-gray-400 text-xs font-mono mb-1">Avg Win Prob</div>
            <div
              className={`font-mono font-bold text-2xl ${
                avgWinProb >= 80
                  ? "text-emerald-400"
                  : avgWinProb >= 60
                  ? "text-yellow-400"
                  : "text-gray-400"
              }`}
            >
              {avgWinProb > 0 ? `${avgWinProb.toFixed(1)}%` : "—"}
            </div>
            {avgWinProb > 0 && (
              <ProgressBar value={avgWinProb} color={winColor} />
            )}
          </div>
        </div>

        {/* Opportunity metrics */}
        {count > 0 && (
          <>
            <div className="border-t border-white/10 pt-4 mt-4">
              <div className="text-gray-400 text-xs font-mono mb-3">
                Opportunity Metrics
              </div>
              <div className="grid grid-cols-2 gap-4">
                <StatCard
                  label="Total Premium"
                  value={`$${totalPremium.toFixed(2)}`}
                  sub="across all opportunities"
                />
                <StatCard
                  label="Avg Premium"
                  value={`$${avgPremium.toFixed(2)}`}
                />
                <StatCard
                  label="Opportunities"
                  value={`${count}`}
                  sub={`above threshold`}
                />
                <StatCard
                  label="Avg |Delta|"
                  value={avgDelta > 0 ? avgDelta.toFixed(4) : "—"}
                />
              </div>
            </div>

            {expiry && (
              <div className="border-t border-white/10 pt-4 mt-4">
                <div className="text-gray-400 text-xs font-mono mb-1">
                  Next Expiry
                </div>
                <div className="text-white font-mono text-sm">
                  {new Date(expiry).toLocaleDateString("en-US", {
                    weekday: "short",
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                  })}
                </div>
              </div>
            )}

            <div className="border-t border-white/10 pt-4 mt-4">
              <div className="text-gray-400 text-xs font-mono mb-3">
                Risk Assessment
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-xs font-mono">
                    Market Condition
                  </span>
                  <span
                    className={`text-xs font-mono font-bold ${
                      vix && vix < 18
                        ? "text-emerald-400"
                        : vix && vix <= 25
                        ? "text-yellow-400"
                        : "text-red-400"
                    }`}
                  >
                    {vix && vix < 18
                      ? "SAFE"
                      : vix && vix <= 25
                      ? "CAUTION"
                      : "DANGER"}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-xs font-mono">
                    Strategy Suitability
                  </span>
                  <span
                    className={`text-xs font-mono font-bold ${
                      avgWinProb >= 80
                        ? "text-emerald-400"
                        : avgWinProb >= 60
                        ? "text-yellow-400"
                        : "text-gray-400"
                    }`}
                  >
                    {avgWinProb >= 80
                      ? "HIGH"
                      : avgWinProb >= 60
                      ? "MODERATE"
                      : "LOW"}
                  </span>
                </div>
              </div>
            </div>
          </>
        )}

        {count === 0 && (
          <div className="border-t border-white/10 pt-6 mt-6 text-center">
            <div className="text-gray-500 text-sm font-mono">
              No opportunities found
            </div>
            <div className="text-gray-600 text-xs font-mono mt-2">
              Try a different ticker or lower the win-prob threshold
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
