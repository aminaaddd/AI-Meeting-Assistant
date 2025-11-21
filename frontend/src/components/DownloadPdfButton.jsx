export default function DownloadPdfButton({ className = "" }) {
  async function handleDownload() {
    try {
      const res = await fetch("/api/meeting/summary_pdf");
      if (!res.ok) {
        alert("Failed to generate PDF.");
        return;
      }

      // Convert the response to a Blob
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);

      // Create a temporary <a> element to trigger download
      const a = document.createElement("a");
      a.href = url;
      a.download = "meeting_summary.pdf";
      a.click();

      // Clean up
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Error downloading PDF:", err);
      alert("Something went wrong while downloading the PDF.");
    }
  }

  return (
    <button
      onClick={handleDownload}
      className={`rounded-xl px-3 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm ${className}`}
    >
      ⬇ Download PDF
    </button>
  );
}
