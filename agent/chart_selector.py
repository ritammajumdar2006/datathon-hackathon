"""
FRAUDNET AI - Intelligent Chart Selector & Plotly Visualizer
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


class ChartSelector:
    DARK_THEME = {
        'paper_bgcolor': 'rgba(15, 23, 42, 1)',
        'plot_bgcolor': 'rgba(15, 23, 42, 1)',
        'font': {'color': '#E2E8F0'},
        'margin': dict(l=40, r=40, t=50, b=40)
    }

    @classmethod
    def select_and_render_chart(cls, df: pd.DataFrame, intent: str, title: str = ""):
        """
        Selects the optimal visualization type based on data dimensions and intent.
        """
        if df is None or df.empty:
            return None, "No data available to render chart."

        # Case 1: Single scalar KPI
        if df.shape == (1, 1):
            val = df.iloc[0, 0]
            col = df.columns[0]
            formatted_title = title if title else col.replace('_', ' ').title()
            fig = go.Figure(go.Indicator(
                mode="number",
                value=float(val) if isinstance(val, (int, float)) else 0,
                title={"text": f"<b>{formatted_title}</b>", "font": {"size": 18, "color": "#94A3B8"}},
                number={"prefix": "₹" if 'amount' in col.lower() or 'gmv' in col.lower() else "", "font": {"size": 40, "color": "#38BDF8"}}
            ))
            fig.update_layout(cls.DARK_THEME, height=220)
            return fig, "KPI Card"

        # Case 2: Time Trend (Line Chart)
        if intent == 'TREND_ANALYSIS' or any('date' in c.lower() or 'day' in c.lower() or 'timestamp' in c.lower() or 'month' in c.lower() for c in df.columns):
            date_cols = [c for c in df.columns if 'date' in c.lower() or 'day' in c.lower() or 'timestamp' in c.lower() or 'month' in c.lower()]
            date_col = date_cols[0]
            num_cols = [c for c in df.columns if c != date_col and pd.api.types.is_numeric_dtype(df[c])]
            if num_cols:
                val_col = num_cols[0]
                label_val = val_col.replace('_', ' ').title()
                chart_title = title if title else f"{label_val} Over Time"
                fig = px.line(
                    df, x=date_col, y=val_col,
                    title=f"<b>{chart_title}</b>",
                    markers=True,
                    template='plotly_dark',
                    color_discrete_sequence=['#38BDF8', '#F59E0B', '#EF4444']
                )
                fig.update_layout(cls.DARK_THEME, height=400)
                return fig, "Line Chart"

        # Case 3: Categorical Breakdown / Rankings (Horizontal or Vertical Bar Chart)
        str_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or pd.api.types.is_object_dtype(df[c])]
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

        if str_cols and num_cols:
            cat_col = str_cols[0]
            val_col = num_cols[0]
            cat_label = cat_col.replace('_', ' ').title()
            val_label = val_col.replace('_', ' ').title()
            
            if len(df) > 5:
                df_sorted = df.sort_values(by=val_col, ascending=True).tail(15)
                chart_title = title if title else f"Top {cat_label} by {val_label}"
                fig = px.bar(
                    df_sorted, x=val_col, y=cat_col, orientation='h',
                    title=f"<b>{chart_title}</b>",
                    text_auto='.2s',
                    template='plotly_dark',
                    color=val_col,
                    color_continuous_scale='Viridis'
                )
            else:
                chart_title = title if title else f"{val_label} by {cat_label}"
                fig = px.bar(
                    df, x=cat_col, y=val_col,
                    title=f"<b>{chart_title}</b>",
                    text_auto='.2s',
                    template='plotly_dark',
                    color_discrete_sequence=['#38BDF8']
                )
            fig.update_layout(cls.DARK_THEME, height=420)
            return fig, "Bar Chart"

        # Case 4: Distribution (Histogram)
        if len(num_cols) == 1 and len(df) > 15:
            val_col = num_cols[0]
            val_label = val_col.replace('_', ' ').title()
            chart_title = title if title else f"Distribution of {val_label}"
            fig = px.histogram(
                df, x=val_col, nbins=30,
                title=f"<b>{chart_title}</b>",
                template='plotly_dark',
                color_discrete_sequence=['#A855F7']
            )
            fig.update_layout(cls.DARK_THEME, height=380)
            return fig, "Histogram"

        # Case 5: Bivariate Relationship (Scatter Plot)
        if len(num_cols) >= 2:
            chart_title = title if title else f"{num_cols[1].title()} vs {num_cols[0].title()}"
            fig = px.scatter(
                df, x=num_cols[0], y=num_cols[1],
                hover_data=str_cols if str_cols else None,
                title=f"<b>{chart_title}</b>",
                template='plotly_dark',
                color_discrete_sequence=['#EC4899']
            )
            fig.update_layout(cls.DARK_THEME, height=400)
            return fig, "Scatter Plot"

        return None, "Table View"
