export default function LiveSummaryCard({ summary, actions }) {
  return (
    <div className="bg-neutral-900/60 border border-neutral-800 rounded-2xl p-5 shadow-xl shadow-black/50 flex flex-col min-h-[320px]">
      <div className="mb-4">
        <h2 className="text-sm font-semibold text-neutral-200 flex items-center gap-2">
          <span role="img" aria-label="notes">📝</span> Résumé en direct
        </h2>
        <p className="text-xs text-neutral-500 mt-1">
          Mise à jour automatiquement pendant l'appel
        </p>
      </div>

      <div className="flex-1 overflow-y-auto pr-2 custom-scroll space-y-4">
        <div className="bg-neutral-800/60 border border-neutral-700 rounded-xl p-3 text-sm text-neutral-100 whitespace-pre-line leading-relaxed">
          {summary || "En attente de contenu..."}
        </div>

        <div className="bg-neutral-800/30 border border-neutral-700/50 rounded-xl p-3">
          <div className="text-[10px] text-neutral-500 uppercase tracking-wide mb-2">
            Actions / next steps
          </div>
          {actions?.length ? (
            <ul className="list-disc list-inside text-xs text-neutral-200 space-y-1">
              {actions.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          ) : (
            <div className="text-neutral-500 text-xs">
              Rien pour l’instant
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
