export default function ParticipantsCard({ participants, speaker }) {
  return (
    <div className="bg-neutral-900/60 border border-neutral-800 rounded-2xl p-5 shadow-xl shadow-black/50 space-y-6">
      <div>
        <h2 className="text-sm font-semibold text-neutral-200 flex items-center gap-2 mb-2">
          <span role="img" aria-label="people">👥</span> Participants
        </h2>
        {participants?.length ? (
          <div className="flex flex-wrap gap-2">
            {participants.map((p, i) => (
              <span
                key={i}
                className="bg-neutral-800/80 text-neutral-200 text-xs px-2 py-1 rounded-lg border border-neutral-700"
              >
                {p}
              </span>
            ))}
          </div>
        ) : (
          <div className="text-neutral-500 text-xs">
            No participants detected
          </div>
        )}
      </div>

      <div>
        <h2 className="text-sm font-semibold text-neutral-200 flex items-center gap-2 mb-3">
          <span role="img" aria-label="mic">🎙</span> Who’s speaking?
        </h2>
        {speaker ? (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-neutral-800 border border-neutral-700 flex items-center justify-center text-neutral-300 text-sm font-medium">
              {speaker.slice(0, 2).toUpperCase()}
            </div>
            <div>
              <div className="text-neutral-100 text-sm font-medium">
                {speaker}
              </div>
              <div className="text-neutral-500 text-xs">
                Microphone detected in real time
              </div>
            </div>
          </div>
        ) : (
          <div className="text-neutral-500 text-xs">
            No one is speaking
          </div>
        )}
      </div>
    </div>
  );
}
