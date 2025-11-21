export default function LiveSummaryCard({ summary, actions }) {
  return (
    <div className="relative min-h-[320px]">
      <div className="absolute -inset-0.5 rounded-3xl bg-gradient-to-b from-emerald-500/35 via-sky-500/30 to-purple-500/40 opacity-70 blur-xl" />
      <div className="relative bg-neutral-950/95 border border-neutral-800 rounded-3xl p-5 shadow-[0_28px_70px_-45px_rgba(0,0,0,1)] flex flex-col">
        <div className="mb-4 flex items-center justify-between gap-2">
          <div>
            <h2 className="text-sm font-semibold text-neutral-100 flex items-center gap-2">
              <span role="img" aria-label="notes">
              </span>
              Live Summary
            </h2>
            <p className="text-[11px] text-neutral-500 mt-1">
              Automatically generated summary of the meeting
            </p>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto pr-1 custom-scroll space-y-4">
          <div className="bg-neutral-900/80 border border-neutral-800 rounded-xl p-3 text-xs text-neutral-100 whitespace-pre-line leading-relaxed">
            {summary || "En attente de contenu..."}
          </div>
        </div>
      </div>
    </div>
  );
}
