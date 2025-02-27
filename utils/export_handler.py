import pandas as pd
import streamlit as st
from io import BytesIO
import json

class ExportHandler:
    @staticmethod
    def to_csv(df: pd.DataFrame, filename: str) -> None:
        """Export DataFrame to CSV"""
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=filename,
            mime='text/csv'
        )

    @staticmethod
    def to_excel(df: pd.DataFrame, filename: str) -> None:
        """Export DataFrame to Excel"""
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        excel_data = output.getvalue()
        st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name=filename,
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    @staticmethod
    def to_json(df: pd.DataFrame, filename: str) -> None:
        """Export DataFrame to JSON"""
        json_str = df.to_json(orient='records', date_format='iso')
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=filename,
            mime='application/json'
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
