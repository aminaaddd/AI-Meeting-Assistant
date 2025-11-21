import { useEffect, useState } from "react";

export default function MeetingInfoCard() {
  const [info, setInfo] = useState({
    meet_link: null,
    start: null,
    end: null,
    participants: [],
  });

  useEffect(() => {
    fetch("/api/meeting/info")
      .then(r => r.json())
      .then(json => setInfo(json))
      .catch(() => {});
  }, []);

  return (
    <div className="bg-neutral-900/60 border border-neutral-800 rounded-2xl p-5 shadow-xl shadow-black/50 text-sm space-y-4">
      <div>
        <div className="text-neutral-400 text-[10px] uppercase tracking-wide mb-1">
          Lien Meet
        </div>
        {info.meet_link ? (
          <a
            className="text-emerald-400 hover:text-emerald-300 break-all underline"
            href={info.meet_link}
            target="_blank"
            rel="noreferrer"
          >
            {info.meet_link}
          </a>
        ) : (
          <div className="text-neutral-500 text-xs">
            Pas de réunion active
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 text-xs">
        <div>
          <div className="text-neutral-500 uppercase tracking-wide mb-1 text-[10px]">
            Début
          </div>
          <div className="text-neutral-200">
            {info.start || "—"}
          </div>
        </div>
        <div>
          <div className="text-neutral-500 uppercase tracking-wide mb-1 text-[10px]">
            Fin
          </div>
          <div className="text-neutral-200">
            {info.end || "—"}
          </div>
        </div>
      </div>

      <div>
        <div className="text-neutral-500 uppercase tracking-wide mb-1 text-[10px]">
          Invités
        </div>
        {info.participants?.length ? (
          <div className="flex flex-wrap gap-2">
            {info.participants.map((p, i) => (
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
            Aucun invité
          </div>
        )}
      </div>
    </div>
  );
}
