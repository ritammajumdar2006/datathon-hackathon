"""
FRAUDNET AI - UI/UX Styling & Design System
High-performance Cyberpunk & Fintech Dark Theme with Glassmorphism and Animated Micro-interactions
"""

def get_custom_css():
    return """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .main {
        background: radial-gradient(circle at 10% 20%, rgba(15, 23, 42, 1) 0%, rgba(11, 17, 32, 1) 90%);
        color: #F8FAFC;
    }

    /* Keyframe Animations */
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.2); }
        50% { box-shadow: 0 0 25px rgba(56, 189, 248, 0.5); }
        100% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.2); }
    }

    @keyframes floatCard {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-4px); }
        100% { transform: translateY(0px); }
    }

    @keyframes neonBorder {
        0% { border-color: rgba(56, 189, 248, 0.3); }
        50% { border-color: rgba(139, 92, 246, 0.6); }
        100% { border-color: rgba(56, 189, 248, 0.3); }
    }

    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.25rem;
        margin-bottom: 1.5rem;
    }

    .kpi-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 16px;
        padding: 1.35rem 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #38BDF8, #818CF8, #C084FC);
        opacity: 0.6;
        transition: opacity 0.3s ease;
    }

    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: rgba(56, 189, 248, 0.5);
        box-shadow: 0 12px 35px -5px rgba(56, 189, 248, 0.25);
    }

    .kpi-card:hover::before {
        opacity: 1;
    }

    .kpi-title {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94A3B8;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }

    .kpi-subtext {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 0.4rem;
        font-weight: 500;
    }

    /* Risk Badges */
    .badge-high {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(185, 28, 28, 0.3) 100%);
        color: #FCA5A5;
        border: 1px solid rgba(239, 68, 68, 0.5);
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        letter-spacing: 0.03em;
        display: inline-block;
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.2);
    }

    .badge-medium {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(180, 83, 9, 0.3) 100%);
        color: #FDE68A;
        border: 1px solid rgba(245, 158, 11, 0.5);
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        display: inline-block;
    }

    .badge-low {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(4, 120, 87, 0.3) 100%);
        color: #A7F3D0;
        border: 1px solid rgba(16, 185, 129, 0.5);
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        display: inline-block;
    }

    /* Modern Panel Cards */
    .panel-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.7) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 14px;
        padding: 1.4rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    /* 3D Visualizer Canvas Box */
    .canvas-3d-box {
        background: #0B1120;
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 16px;
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.15);
        overflow: hidden;
        margin-bottom: 1.5rem;
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.8);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(56, 189, 248, 0.3);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(56, 189, 248, 0.6);
    }
    </style>
    """
