import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";

/**
 * Exporta o elemento do documento (papel do editor) para PDF.
 */
export async function exportarPdfCaderno(elemento, titulo = "Anotacao") {
  if (!elemento) throw new Error("Elemento do documento não encontrado.");

  const canvas = await html2canvas(elemento, {
    scale: 2,
    useCORS: true,
    backgroundColor: "#ffffff",
    logging: false,
  });

  const imgData = canvas.toDataURL("image/png");
  const pdf = new jsPDF({ orientation: "p", unit: "mm", format: "a4" });
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 10;
  const imgWidth = pageWidth - margin * 2;
  const imgHeight = (canvas.height * imgWidth) / canvas.width;

  let heightLeft = imgHeight;
  let position = margin;

  pdf.addImage(imgData, "PNG", margin, position, imgWidth, imgHeight);
  heightLeft -= pageHeight - margin * 2;

  while (heightLeft > 0) {
    position = heightLeft - imgHeight + margin;
    pdf.addPage();
    pdf.addImage(imgData, "PNG", margin, position, imgWidth, imgHeight);
    heightLeft -= pageHeight - margin * 2;
  }

  const nome = titulo.replace(/[^\w\s-]/g, "").trim() || "anotacao";
  pdf.save(`${nome}.pdf`);
}
