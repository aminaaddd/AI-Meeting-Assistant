export default function ActionBar({ status, onEnd }) {
  const statusColor =
    status === "listening"
      ? "bg-emerald-500"
      : status === "stopped"
      ? "bg-gray-500"
      : "bg-yellow-400";

  return (
    <div className="flex items-center justify-between flex-wrap gap-4 border border-neutral-800 rounded-2xl bg-neutral-900/60 shadow-xl shadow-black/50 p-4">
      <div className="flex items-center gap-2 text-sm">
        <span className={`inline-block w-2 h-2 rounded-full ${statusColor}`}></span>
        <span className="text-neutral-200 font-medium">
          {status === "listening"
            ? "En cours d'écoute"
            : status === "stopped"
            ? "Arrêté"
            : status}
        </span>
      </div>

      <button
        onClick={onEnd}
        className="px-3 py-2 rounded-xl bg-red-600/20 hover:bg-red-600/30 text-red-400 text-xs font-medium border border-red-600/40"
      >
        🛑 End meeting
      </button>
    </div>
  );
}
