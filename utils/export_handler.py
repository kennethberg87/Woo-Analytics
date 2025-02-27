import pandas as pd
import streamlit as st
from io import BytesIO
import json


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