"use client";

import { useEffect, useRef } from "react";
import { createChart, ColorType, IChartApi, ISeriesApi, Time } from "lightweight-charts";

interface PriceChartProps {
  ticker: string;
  data?: { time: string; open: number; high: number; low: number; close: number }[];
  isLoading?: boolean;
}

export default function PriceChart({ ticker, data, isLoading = false }: PriceChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const cleanup = () => {
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
      seriesRef.current = null;
    };

    cleanup();

    try {
      const chart = createChart(chartContainerRef.current, {
        layout: {
          background: { type: ColorType.Solid, color: "#000000" },
          textColor: "#9ca3af",
        },
        width: chartContainerRef.current.clientWidth,
        height: 500,
        grid: {
          vertLines: { color: "rgba(255, 255, 255, 0.05)", visible: true },
          horzLines: { color: "rgba(255, 255, 255, 0.05)", visible: true },
        },
        crosshair: {
          mode: 1,
        },
        rightPriceScale: {
          borderColor: "rgba(255, 255, 255, 0.1)",
          scaleMargins: {
            top: 0.1,
            bottom: 0.1,
          },
        },
        timeScale: {
          borderColor: "rgba(255, 255, 255, 0.1)",
          timeVisible: true,
          secondsVisible: false,
        },
      });

      const candlestickSeries = (chart as any).addCandlestickSeries({
        upColor: "#10b981",
        downColor: "#ef4444",
        borderVisible: false,
        wickUpColor: "#10b981",
        wickDownColor: "#ef4444",
      }) as ISeriesApi<"Candlestick">;

      chartRef.current = chart;
      seriesRef.current = candlestickSeries;

      const handleResize = () => {
        if (chartContainerRef.current && chartRef.current) {
          const width = chartContainerRef.current.clientWidth;
          chartRef.current.applyOptions({ width });
        }
      };

      const resizeObserver = new ResizeObserver(handleResize);
      if (chartContainerRef.current) {
        resizeObserver.observe(chartContainerRef.current);
      }

      return () => {
        resizeObserver.disconnect();
        cleanup();
      };
    } catch (error) {
      console.error("Chart initialization error:", error);
      cleanup();
    }
  }, [ticker]);

  useEffect(() => {
    if (!seriesRef.current || !data || data.length === 0) {
      if (data && data.length === 0) {
        console.log("Chart Data: Empty array received");
      }
      return;
    }

    console.log("Chart Data:", data.length, "items received");

    try {
      const formattedData = data
        .map((item) => {
          const timeStr = item.time;
          let timeValue: Time;
          
          if (typeof timeStr === 'string' && timeStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
            timeValue = timeStr.replace(/-/g, '') as Time;
          } else {
            timeValue = timeStr as Time;
          }

          return {
            time: timeValue,
            open: Number(item.open),
            high: Number(item.high),
            low: Number(item.low),
            close: Number(item.close),
          };
        })
        .filter(item => !isNaN(item.open) && !isNaN(item.high) && !isNaN(item.low) && !isNaN(item.close))
        .sort((a, b) => {
          const timeA = typeof a.time === 'string' ? a.time : String(a.time);
          const timeB = typeof b.time === 'string' ? b.time : String(b.time);
          return timeA.localeCompare(timeB);
        });

      console.log("Formatted Chart Data:", formattedData.length, "items after processing");
      
      if (formattedData.length > 0) {
        console.log("Setting chart data...");
        seriesRef.current.setData(formattedData);
        
        if (chartRef.current) {
          chartRef.current.timeScale().fitContent();
        }
        console.log("Chart data set successfully");
      } else {
        console.log("No valid chart data after formatting");
      }
    } catch (error) {
      console.error("Chart data update error:", error);
    }
  }, [data]);

  const hasData = data && data.length > 0;

  return (
    <div className="w-full h-[500px] relative bg-black">
      <div ref={chartContainerRef} className="w-full h-full" style={{ minHeight: "500px" }} />
      {!hasData && !isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-lg backdrop-blur-sm z-10 pointer-events-none">
          <div className="text-center px-4">
            <p className="text-gray-400 text-sm mb-1 font-mono">Loading Chart...</p>
            <p className="text-gray-500 text-xs font-mono">Historical price data will appear here</p>
          </div>
        </div>
      )}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-lg backdrop-blur-sm z-10 pointer-events-none">
          <div className="text-center">
            <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin mx-auto mb-2"></div>
            <div className="text-gray-400 text-sm animate-pulse font-mono">Loading chart...</div>
          </div>
        </div>
      )}
    </div>
  );
}
