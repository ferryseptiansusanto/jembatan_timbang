import tempfile, webbrowser, os, uuid, xlsxwriter
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import mm


class PDFReportPreviewConfigurable:
    def __init__(self, title, subtitle=None, landscape_mode=True):
        self.title = title
        self.subtitle = subtitle
        self.landscape_mode = landscape_mode

    def safe_float(self, val):
        try:
            return round(float(str(val).replace(",", "").strip()), 1)
        except:
            return 0.0

    def build_footer(self, canvas_obj, doc):
        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica", 7)
        footer = f"Dicetak oleh: {os.getlogin()} | {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        canvas_obj.drawString(20 * mm, 10 * mm, footer)
        canvas_obj.drawRightString(280 * mm, 10 * mm, f"Halaman {doc.page}")
        canvas_obj.restoreState()

    def from_config(self, headers, data_rows, fields_config, sort_by=None, sort_reverse=False):
        # 🔍 Ambil hanya field yang visible
        visible_fields = [f for f in fields_config if f.get("visible", True)]
        field_keys = [f["key"] for f in visible_fields]
        header_labels = [f.get("alias", f["key"]) for f in visible_fields]
        col_widths = [f.get("width", 60) for f in visible_fields]

        # 🧠 Buat map nama header ke indeks
        header_map = {h.lower(): i for i, h in enumerate(headers)}

        # 🔀 Sorting data jika diminta
        if sort_by:
            idx_sort = header_map.get(sort_by.lower())
            if idx_sort is not None:
                try:
                    data_rows = sorted(data_rows, key=lambda r: r[idx_sort], reverse=sort_reverse)
                except Exception as e:
                    print(f"[WARN] Gagal sort by '{sort_by}':", e)

        # 📄 Bangun struktur tabel
        table_data = [header_labels]
        jumlah_transaksi = len(data_rows)
        total_row = [""] * len(field_keys)

        for row in data_rows:
            record = []
            keterangan_value = None

            # 🔎 Proses hanya field yang visible
            for f in visible_fields:
                idx = header_map.get(f["key"].lower())
                val = row[idx] if idx is not None else ""

                if f.get("is_ts"):
                    try:
                        val = datetime.fromtimestamp(int(val)).strftime("%d/%m/%Y %H:%M")
                    except:
                        val = "-"
                record.append(val)

            table_data.append(record)

            # 📝 Baris keterangan (split_row)
            for f in fields_config:
                if f.get("split_row"):
                    idx_ket = header_map.get(f["key"].lower())
                    val = row[idx_ket] if idx_ket is not None else ""
                    if val:
                        keterangan_value = str(val)

            if keterangan_value:
                ket_row = [""] * len(field_keys)
                ket_row[0] = f"Keterangan: {keterangan_value}"
                table_data.append(ket_row)

        # ➕ Baris total
        for i, f in enumerate(visible_fields):
            if f.get("numeric"):
                idx_raw = header_map.get(f["key"].lower())
                total = round(sum(self.safe_float(row[idx_raw]) for row in data_rows), 1)
                total_row[i] = f"{total:,}"

        total_row[0] = f"Total ({jumlah_transaksi} transaksi)"
        table_data.append(total_row)

        return table_data, col_widths

    def preview(self, headers, data_rows, fields_config, sort_by=None, sort_reverse=False):
        table_data, col_widths = self.from_config(headers, data_rows, fields_config, sort_by, sort_reverse)
        file_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}_preview.pdf")
        page_size = landscape(A4) if self.landscape_mode else A4
        doc = SimpleDocTemplate(file_path, pagesize=page_size)
        styles = getSampleStyleSheet()
        elements = [Paragraph(self.title, styles["Title"])]

        if self.subtitle:
            elements.append(Paragraph(self.subtitle, styles["Normal"]))
        elements.append(Spacer(1, 12))

        table = Table(table_data, repeatRows=1, colWidths=col_widths)
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d9d9d9")),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#f4f4f4")),
            ('SPAN', (0, -1), (2, -1)),
        ]

        for i in range(2, len(table_data) - 1, 2):
            if str(table_data[i][0]).lower().startswith("keterangan:"):
                style.append(('SPAN', (0, i), (-1, i)))
                style.append(('TEXTCOLOR', (0, i), (-1, i), colors.HexColor("#444444")))
                style.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Oblique'))

        table.setStyle(TableStyle(style))
        elements.append(table)
        doc.build(elements, onFirstPage=self.build_footer, onLaterPages=self.build_footer)
        webbrowser.open(f"file://{file_path}")

    def export_excel(self, headers, data_rows, fields_config, file_path, sort_by=None, sort_reverse=False):
        table_data, _ = self.from_config(headers, data_rows, fields_config, sort_by, sort_reverse)
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet("Laporan")

        cell_format = workbook.add_format({"font_size": 9, "align": "left"})
        bold_format = workbook.add_format({"bold": True, "bg_color": "#d9d9d9"})

        for row_idx, row in enumerate(table_data):
            for col_idx, val in enumerate(row):
                fmt = bold_format if row_idx == 0 else cell_format
                worksheet.write(row_idx, col_idx, val, fmt)

        workbook.close()
        os.startfile(file_path)