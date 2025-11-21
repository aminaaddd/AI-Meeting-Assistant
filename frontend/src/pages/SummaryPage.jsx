import { useState } from "react";

export default function SummaryPage() {
  const [report, setReport] = useState(null);

  async function loadReport() {
    try {
      const res = await fetch("/api/meeting/export");
      const json = await res.json();
      setReport(json);
    } catch (e) {
      console.error(e);
    }
  }

  function downloadTxt() {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], {
      type: "text/plain;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.download = "meeting_report.txt";
    a.href = url;
    a.click();
    URL.revokeObjectURL(url);
  }

  const title = report?.title || "Meeting report";
  const summary = report?.summary || "No summary available yet.";
  const actions = report?.actions || [];
  const meetLink = report?.meet_link || "-";
  const start = report?.start || "-";
  const end = report?.end || "-";
  const transcript = report?.raw_transcript || [];

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* HERO */}
      <section className="relative overflow-hidden rounded-3xl border border-neutral-800 bg-[radial-gradient(circle_at_top,_#22c55e33,_transparent_55%),radial-gradient(circle_at_bottom_left,_#0ea5e933,_transparent_55%),radial-gradient(circle_at_bottom_right,_#a855f733,_transparent_55%),#020617] px-6 py-7 shadow-[0_40px_100px_-50px_rgba(0,0,0,1)] mt-4">
        <div className="pointer-events-none absolute inset-0 opacity-55">
          <div className="absolute -left-20 -top-20 h-48 w-48 rounded-full bg-emerald-400/40 blur-3xl" />
          <div className="absolute right-0 top-6 h-48 w-48 rounded-full bg-sky-500/40 blur-3xl" />
          <div className="absolute left-1/3 bottom-[-80px] h-60 w-60 rounded-full bg-purple-500/35 blur-3xl" />
        </div>

        <div className="relative space-y-2">
          <div className="inline-flex items-center gap-2 rounded-full bg-black/40 border border-white/10 px-3 py-1 text-[11px] text-neutral-100">
            ✨ Summary & Export
          </div>

          <h2 className="text-2xl font-semibold text-white tracking-tight">
            Final meeting report
          </h2>
          <p className="text-sm text-neutral-300 max-w-xl">
          </p>
        </div>
      </section>

      {/* MAIN CARD */}
      <div className="relative">
        <div className="absolute -inset-0.5 rounded-3xl bg-gradient-to-r from-emerald-500/40 via-sky-500/40 to-purple-500/40 opacity-70 blur-xl" />
        <div className="relative bg-neutral-950/95 border border-neutral-800 rounded-3xl p-6 shadow-[0_30px_80px_-50px_rgba(0,0,0,1)] space-y-6">
          {/* header */}
          <div className="flex items-center justify-between gap-4">
            <div>
              <div className="text-xs font-semibold text-emerald-300 uppercase tracking-wide">
                Final report
              </div>
              <div className="text-sm text-neutral-100 font-semibold">{title}</div>
              <div className="text-[11px] text-neutral-500 mt-1">
                {start} → {end}
              </div>
            </div>

            <button
              onClick={loadReport}
              className="px-4 py-2 rounded-xl bg-neutral-900 border border-neutral-700 text-xs text-white hover:border-neutral-500 transition shadow"
            >
              Load
            </button>
          </div>

          {/* meta */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-[11px] text-neutral-300">
            <div className="bg-neutral-900/60 border border-neutral-800 rounded-xl px-3 py-2">
              <div className="text-neutral-500 uppercase tracking-wide text-[10px]">
                Link
              </div>
              <div className="mt-1 break-all text-emerald-300 text-xs">
                {meetLink}
              </div>
            </div>
            <div className="bg-neutral-900/60 border border-neutral-800 rounded-xl px-3 py-2">
              <div className="text-neutral-500 uppercase tracking-wide text-[10px]">
                Start
              </div>
              <div className="mt-1 text-xs">{start}</div>
            </div>
            <div className="bg-neutral-900/60 border border-neutral-800 rounded-xl px-3 py-2">
              <div className="text-neutral-500 uppercase tracking-wide text-[10px]">
                End
              </div>
              <div className="mt-1 text-xs">{end}</div>
            </div>
          </div>

          {/* summary + actions */}
          <div className="grid grid-cols-1 md:grid-cols-[minmax(0,2fr)_minmax(0,1.2fr)] gap-6">
            {/* Summary */}
            <div className="space-y-2">
              <div className="text-[11px] text-neutral-500 uppercase tracking-wide">
                Summary
              </div>
              <div className="bg-neutral-900/70 border border-neutral-800 rounded-xl p-4 text-xs text-neutral-100 leading-relaxed max-h-72 overflow-y-auto custom-scroll whitespace-pre-line">
                {summary}
              </div>
            </div>
          </div>

          {/* download txt */}
          <button
            onClick={downloadTxt}
            disabled={!report}
            className="w-full mt-2 px-4 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-emerald-500 text-white text-sm font-medium shadow-[0_0_20px_-5px_rgba(16,185,129,0.7)] hover:shadow-[0_0_25px_-2px_rgba(16,185,129,0.9)] transition disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Download .txt
          </button>
        </div>
      </div>
    </div>
  );
}
