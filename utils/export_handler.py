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
    def to_csv(df: pd.DataFrame, filename: str) -> None:
        """Export DataFrame to CSV"""
        # Convert timezone-aware dates to timezone-naive
        df_export = df.copy()
        if 'date' in df_export.columns:
            df_export['date'] = df_export['date'].dt.tz_localize(None)

        csv = df_export.to_csv(index=False)
        st.download_button(label="Last ned CSV",
                           data=csv,
                           file_name=filename,
                           mime='text/csv')

    @staticmethod
    def to_excel(df: pd.DataFrame, filename: str) -> None:
        """Export DataFrame to Excel"""
        output = BytesIO()

        # Convert timezone-aware dates to timezone-naive
        df_export = df.copy()
        datetime_columns = df_export.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns, Europe/Oslo]']).columns

        for col in datetime_columns:
            df_export[col] = df_export[col].dt.tz_localize(None)

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False)
        excel_data = output.getvalue()
        st.download_button(
            label="Last ned Excel",
            data=excel_data,
            file_name=filename,
            mime=
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    @staticmethod
    def to_json(df: pd.DataFrame, filename: str) -> None:
        """Export DataFrame to JSON"""
        # Convert timezone-aware dates to timezone-naive for JSON compatibility
        df_export = df.copy()
        datetime_columns = df_export.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns, Europe/Oslo]']).columns

        for col in datetime_columns:
            df_export[col] = df_export[col].dt.tz_localize(None)

        json_str = df_export.to_json(orient='records', date_format='iso')
        st.download_button(label="Last ned JSON",
                           data=json_str,
                           file_name=filename,
                           mime='application/json')

    @staticmethod
    def to_pdf(df: pd.DataFrame, filename: str, title: str) -> None:
        """Export DataFrame to PDF with formatting"""
        # Create a BytesIO buffer for the PDF
        buffer = BytesIO()

        # Create the PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Add title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 12))

        # Convert DataFrame to list of lists for the table
        df_export = df.copy()

        # Convert timezone-aware dates to timezone-naive
        datetime_columns = df_export.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns, Europe/Oslo]']).columns
        for col in datetime_columns:
            df_export[col] = df_export[col].dt.tz_localize(None)

        # Format numeric columns
        numeric_columns = df_export.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            df_export[col] = df_export[col].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "")

        # Convert DataFrame to table data
        table_data = [df_export.columns.tolist()] + df_export.values.tolist()

        # Create table
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))

        elements.append(table)

        # Build PDF document
        doc.build(elements)
        pdf_data = buffer.getvalue()
        buffer.close()

        # Create download button
        st.download_button(
            label="Last ned PDF",
            data=pdf_data,
            file_name=filename,
            mime='application/pdf'
        )

    @staticmethod
    def export_data(df: pd.DataFrame, name: str, format: str) -> None:
        """Export data in specified format"""
        if df.empty:
            st.warning(f"No {name} data available to export")
            return

        filename = f"woocommerce_{name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"

        if format == 'CSV':
            filename += '.csv'
            ExportHandler.to_csv(df, filename)
        elif format == 'Excel':
            filename += '.xlsx'
            ExportHandler.to_excel(df, filename)
        elif format == 'JSON':
            filename += '.json'
            ExportHandler.to_json(df, filename)
        elif format == 'PDF':
            filename += '.pdf'
            title = f"WooCommerce {name.capitalize()} Report"
            ExportHandler.to_pdf(df, filename, title)