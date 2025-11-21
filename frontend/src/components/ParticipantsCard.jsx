export default function ParticipantsCard({ participants = [] }) {
  const count = participants.length;

  return (
    <div className="relative">
      <div className="absolute -inset-0.5 rounded-2xl bg-gradient-to-r from-emerald-500/35 via-sky-500/35 to-purple-500/35 opacity-60 blur-xl" />
      <div className="relative bg-neutral-950/90 border border-neutral-800 rounded-2xl p-4 shadow-[0_24px_60px_-40px_rgba(0,0,0,1)]">
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-purple-500/20 border border-purple-400/40 text-[13px]">
              👥
            </span>
            <h2 className="text-sm font-semibold text-neutral-100">Participants</h2>
          </div>
          <span className="text-[11px] text-neutral-400">
            {count ? `${count} detected` : "No one detected yet"}
          </span>
        </div>

        {count ? (
          <div className="flex flex-wrap gap-2">
            {participants.map((p, i) => (
              <span
                key={i}
                className="bg-neutral-900/80 text-neutral-100 text-xs px-2.5 py-1.5 rounded-full border border-neutral-700/80"
              >
                {p}
              </span>
            ))}
          </div>
        ) : (
          <div className="text-xs text-neutral-500">
            Aucun participant détecté pour le moment.
          </div>
        )}
      </div>
    </div>
  );
}
