import tempfile, webbrowser, os, uuid
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import mm

class PDFReportPreview:
    def __init__(self, headers, data_rows, title="Laporan", subtitle=None, ts_columns=None, col_widths=None):
        self.headers = headers
        self.data_rows = data_rows or []
        self.title = title
        self.subtitle = subtitle
        self.ts_columns = ts_columns
        self.col_widths = col_widths or [60] * len(headers)  # default width

    def is_timestamp(self, val):
        try:
            val_int = int(val)
            return 946684800 <= val_int <= 4102444800
        except:
            return False

    def format_ts(self, ts):
        try:
            return datetime.fromtimestamp(int(ts)).strftime("%d/%m/%Y %H:%M")
        except:
            return "-"

    def format_data(self):
        formatted = []
        try:
            idx_ket = self.headers.index("Keterangan")
        except ValueError:
            idx_ket = -1

        for row in self.data_rows:
            row_clean = []
            for i, val in enumerate(row):
                if self.ts_columns and i in self.ts_columns:
                    row_clean.append(self.format_ts(val))
                elif not self.ts_columns and self.is_timestamp(val):
                    row_clean.append(self.format_ts(val))
                else:
                    row_clean.append(val)
            # simpan keterangan dan kosongkan di baris utama
            keterangan_value = str(row_clean[idx_ket]) if idx_ket != -1 else ""
            if idx_ket != -1:
                row_clean[idx_ket] = ""  # kosongkan sel keterangan di row utama

            formatted.append(row_clean)

            # baris tambahan untuk keterangan, isi di kolom pertama saja
            if keterangan_value:
                keterangan_row = [""] * len(self.headers)
                keterangan_row[0] = f"Keterangan: {keterangan_value}"
                formatted.append(keterangan_row)
        return formatted

    def safe_int(self, val):
        try:
            return int(str(val).replace(",", "").strip())
        except:
            return 0

    def safe_float(self, val):
        try:
            return float(str(val).replace(",", "").strip())
        except:
            return 0.0

    def build_footer(self, canvas_obj, doc):
        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica", 7)
        footer = f"Dicetak oleh: {os.getlogin()} | {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        canvas_obj.drawString(20 * mm, 10 * mm, footer)
        canvas_obj.drawRightString(280 * mm, 10 * mm, f"Halaman {doc.page}")
        canvas_obj.restoreState()

    def append_total_row(self, table_data):
        try:
            idx_netto = self.headers.index("Netto")
        except:
            idx_netto = 8

        jumlah_transaksi = len(self.data_rows)
        total_netto = round(sum(self.safe_float(row[idx_netto]) for row in self.data_rows), 1)
        total_row = [""] * len(self.headers)
        total_row[0] = f"Total ({jumlah_transaksi} transaksi)"
        total_row[idx_netto] = f"{total_netto:,}"

        table_data.append(total_row)
        return table_data

    def format_data_with_keterangan(self):
        result = []
        try:
            idx_keterangan = self.headers.index("Keterangan")
        except:
            idx_keterangan = -1  # fallback kalau tidak ada

        for row in self.data_rows:
            main_row = list(row)
            keterangan_text = str(main_row[idx_keterangan])
            main_row[idx_keterangan] = ""  # kosongkan di baris utama
            result.append(main_row)

            # baris tambahan hanya berisi keterangan di kolom pertama
            keterangan_row = [""] * len(self.headers)
            keterangan_row[0] = f"📝 {keterangan_text}"
            result.append(keterangan_row)
        return result

    def preview(self, landscape_mode=True):
        file_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}_preview.pdf")
        page_size = landscape(A4) if landscape_mode else A4
        doc = SimpleDocTemplate(file_path, pagesize=page_size)

        styles = getSampleStyleSheet()
        elements = [Paragraph(self.title, styles["Title"])]



        if self.subtitle:
            elements.append(Paragraph(self.subtitle, styles["Normal"]))
        elements.append(Spacer(1, 12))

        table_data = [self.headers] + self.format_data_with_keterangan()
        table_data = self.append_total_row(table_data)

        table = Table(table_data, repeatRows=1, colWidths=self.col_widths)
        table_styles = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d9d9d9")),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#f4f4f4")),
                ('SPAN', (0, -1), (2, -1)),  # baris total
            ]

        for i in range(2, len(table_data) - 1, 2):
            table_styles.append(('SPAN', (0, i), (-1, i)))  # baris i adalah baris keterangan
            table_styles.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Oblique'))
            table_styles.append(('TEXTCOLOR', (0, i), (-1, i), colors.HexColor("#444444")))

        table.setStyle(TableStyle(table_styles))

        elements.append(table)
        doc.build(elements, onFirstPage=self.build_footer, onLaterPages=self.build_footer)
        webbrowser.open(f"file://{file_path}")