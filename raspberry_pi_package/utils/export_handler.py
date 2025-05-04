import pandas as pd
import streamlit as st
from io import BytesIO
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class ExportHandler:
    @staticmethod
    def export_data(df, data_type, export_format):
        """Export data to various formats"""
        if df.empty:
            st.warning(f"No {data_type} data available to export.")
            return

        if export_format == 'CSV':
            csv = df.to_csv(index=False)
            st.download_button(
                label=f"Last ned {data_type} som CSV",
                data=csv,
                file_name=f"{data_type}_export.csv",
                mime="text/csv",
            )

        elif export_format == 'Excel':
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name=data_type.capitalize())
            output.seek(0)

            st.download_button(
                label=f"Last ned {data_type} som Excel",
                data=output,
                file_name=f"{data_type}_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        elif export_format == 'JSON':
            json_str = df.to_json(orient='records', date_format='iso')
            st.download_button(
                label=f"Last ned {data_type} som JSON",
                data=json_str,
                file_name=f"{data_type}_export.json",
                mime="application/json",
            )

        elif export_format == 'PDF':
            # Create PDF with reportlab
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()

            # Title
            elements = []
            title_style = styles['Heading1']
            title = Paragraph(f"{data_type.capitalize()} Report", title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.5*inch))

            # Convert DataFrame to a list of lists for the table
            data = [df.columns.tolist()]  # Header row
            for i, row in df.iterrows():
                data.append([str(x) for x in row.values])

            # Create table with the data
            table = Table(data)
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ])
            table.setStyle(style)
            elements.append(table)

            # Build PDF
            doc.build(elements)
            buffer.seek(0)

            st.download_button(
                label=f"Last ned {data_type} som PDF",
                data=buffer,
                file_name=f"{data_type}_export.pdf",
                mime="application/pdf",
            )