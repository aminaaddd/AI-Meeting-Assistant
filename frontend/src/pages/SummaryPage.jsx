import { useState } from "react";

export default function SummaryPage() {
  const [report, setReport] = useState(null);

  async function loadReport() {
    const res = await fetch("/api/meeting/export");
    const json = await res.json();
    setReport(json);
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

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-neutral-900/60 border border-neutral-800 rounded-2xl p-5 shadow-xl shadow-black/50 flex flex-col space-y-4">
        <div className="flex items-start justify-between">
          <div>
            <div className="text-sm font-semibold text-neutral-200 flex items-center gap-2">
              Final report
            </div>
            <div className="text-xs text-neutral-500 mt-1">
              Meeting recap
            </div>
          </div>

          <button
            onClick={loadReport}
            className="px-3 py-2 rounded-xl bg-neutral-800 hover:bg-neutral-700 border border-neutral-600 text-[11px] font-medium text-neutral-200"
          >
            Load
          </button>
        </div>

        <div className="flex-1 text-xs text-neutral-300 bg-neutral-800/40 border border-neutral-700/50 rounded-xl p-3 whitespace-pre-line overflow-y-auto custom-scroll min-h-[200px]">
          {report ? (
            <>
              <div className="text-neutral-500 text-[10px] uppercase tracking-wide mb-1">
                Title
              </div>
              <div className="mb-3 text-neutral-200 font-semibold">
                {report.title}
              </div>

              <div className="text-neutral-500 text-[10px] uppercase tracking-wide mb-1">
                Summary
              </div>
              <div className="mb-3">{report.summary || "—"}</div>

              <div className="text-neutral-500 text-[10px] uppercase tracking-wide mb-1">
                Action items
              </div>
              <ul className="list-disc list-inside mb-3">
                {report.actions?.length ? (
                  report.actions.map((a, i) => <li key={i}>{a}</li>)
                ) : (
                  <li>No action captured</li>
                )}
              </ul>

              <div className="text-neutral-500 text-[10px] uppercase tracking-wide mb-1">
                Meet link
              </div>
              <div className="mb-3 break-all">
                {report.meet_link || "—"}
              </div>

              <div className="text-neutral-500 text-[10px] uppercase tracking-wide mb-1">
                Time window
              </div>
              <div className="mb-3">
                {report.start || "?"} → {report.end || "?"}
              </div>

              <div className="text-neutral-500 text-[10px] uppercase tracking-wide mb-1">
                Raw transcript (latest state)
              </div>
              <div className="text-[10px] text-neutral-400 max-h-[150px] overflow-y-auto custom-scroll border border-neutral-700/50 rounded-lg p-2 bg-neutral-900/80">
                {report.raw_transcript?.length
                  ? report.raw_transcript.map((line, idx) => (
                      <div key={idx} className="mb-2">
                        <div className="text-neutral-300">{line.text}</div>
                        <div className="text-neutral-500 italic">
                          {line.translated}
                        </div>
                      </div>
                    ))
                  : "—"}
              </div>
            </>
          ) : (
            <div className="text-neutral-500">
              Click “Load” to display the final report.
            </div>
          )}
        </div>

        <button
          className="px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-medium text-white"
          onClick={downloadTxt}
          disabled={!report}
        >
          ⬇ Download .txt
        </button>
      </div>

      <div className="text-sm text-neutral-400 leading-relaxed bg-neutral-900/40 border border-neutral-800 rounded-2xl p-5 shadow-xl shadow-black/50">
        <div className="text-neutral-200 font-semibold text-base mb-2">
          What next?
        </div>
        <ul className="list-disc list-inside space-y-2 text-xs text-neutral-300">
          <li>You can send this summary in a recap email.</li>
          <li>You can extract “Action items” and add them to Jira/Trello.</li>
          <li>You can keep the raw transcript for audit/compliance.</li>
        </ul>
      </div>
    </div>
  );
}
