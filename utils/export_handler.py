import pandas as pd
import streamlit as st
from io import BytesIO
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import requests
from zipfile import ZipFile
import io

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

    @staticmethod
    def download_invoices_zip(invoice_urls: list, filename: str = None) -> None:
        """Download multiple invoices and create a ZIP file"""
        if not invoice_urls:
            st.warning("Ingen fakturaer tilgjengelig for nedlasting")
            return

        # Custom CSS for black button with proper sizing
        st.markdown("""
            <style>
            div[data-testid="stDownloadButton"] button {
                background-color: black !important;
                color: white !important;
                border: none !important;
                padding: 0.5rem 1rem !important;
                border-radius: 0.3rem !important;
                width: auto !important;
                max-width: 300px !important;
            }
            div[data-testid="stDownloadButton"] button:hover {
                background-color: #333333 !important;
                color: white !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Create a BytesIO object to store the ZIP file
        zip_buffer = io.BytesIO()

        # Create a ZIP file
        success_count = 0
        error_count = 0

        with ZipFile(zip_buffer, 'w') as zip_file:
            with st.spinner('Laster ned fakturaer...'):
                progress_bar = st.progress(0)

                for idx, (invoice_number, url) in enumerate(invoice_urls, 1):
                    try:
                        # Download the PDF
                        response = requests.get(
                            url,
                            verify=False,
                            timeout=30,  # Increased timeout
                            headers={
                                'User-Agent': 'Mozilla/5.0',
                                'Accept': 'application/pdf'
                            }
                        )

                        if response.status_code == 200 and response.content:
                            # Verify it's actually a PDF
                            if response.headers.get('content-type', '').lower().startswith('application/pdf'):
                                zip_file.writestr(f"{invoice_number}.pdf", response.content)
                                success_count += 1
                            else:
                                error_count += 1
                                st.warning(f"Faktura {invoice_number} er ikke i PDF-format")
                        else:
                            error_count += 1
                            st.warning(f"Kunne ikke laste ned faktura {invoice_number} (Status: {response.status_code})")

                    except requests.exceptions.Timeout:
                        error_count += 1
                        st.warning(f"Tidsavbrudd ved nedlasting av faktura {invoice_number}")
                    except Exception as e:
                        error_count += 1
                        st.warning(f"Feil ved nedlasting av faktura {invoice_number}: {str(e)}")

                    # Update progress
                    progress = (idx / len(invoice_urls))
                    progress_bar.progress(progress)

                progress_bar.empty()

        if success_count > 0:
            # Create the download button if we have any successful downloads
            st.download_button(
                label=f"⬇️ Last ned fakturaer ({success_count} av {len(invoice_urls)})",
                data=zip_buffer.getvalue(),
                file_name=filename,
                mime="application/zip",
                use_container_width=False
            )

            if error_count > 0:
                st.warning(f"{error_count} fakturaer kunne ikke lastes ned. Prøv igjen senere eller last ned enkeltvis.")
        else:
            st.error("Ingen fakturaer ble lastet ned. Prøv igjen senere.")