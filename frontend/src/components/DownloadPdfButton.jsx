export default function DownloadPdfButton({ className = "" }) {
  async function handleDownload() {
    try {
      const res = await fetch("/api/meeting/summary_pdf");
      if (!res.ok) {
        alert("Failed to generate PDF.");
        return;
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "meeting_summary.pdf";
      a.click();

      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Error downloading PDF:", err);
      alert("Something went wrong while downloading the PDF.");
    }
  }

  return (
    <button
      onClick={handleDownload}
      className={`inline-flex items-center gap-2 rounded-xl px-4 py-2 text-xs font-semibold text-white bg-gradient-to-r from-emerald-600 via-emerald-500 to-sky-500 shadow-[0_0_18px_-4px_rgba(16,185,129,0.9)] hover:shadow-[0_0_25px_-2px_rgba(56,189,248,1)] transition ${className}`}
    >
      Download PDF
    </button>
  );
}
