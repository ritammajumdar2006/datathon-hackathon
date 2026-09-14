"""
FRAUDNET AI - Graph-Based Fraud Detection & Network Intelligence
TransOrg AgentIQ Datathon - FinTech & BFSI Track
"""

import os
import networkx as nx
import plotly.graph_objects as go
import pandas as pd
import numpy as np


class FraudGraphEngine:
    def __init__(self, df_tx, df_merchants, df_kyc, df_cbk):
        self.df_tx = df_tx.copy()
        self.df_merchants = df_merchants.copy()
        self.df_kyc = df_kyc.copy()
        self.df_cbk = df_cbk.copy()
        self.G = nx.Graph()
        self._build_graph()

    def _build_graph(self):
        """Construct heterogeneous network graph of Users, Merchants, and Settlement Accounts"""
        # 1. Add Merchant Nodes
        for _, r in self.df_merchants.iterrows():
            m_id = r['merchant_id']
            self.G.add_node(
                m_id,
                node_type='MERCHANT',
                name=r.get('merchant_name', m_id),
                category=r.get('merchant_category', 'General'),
                status=r.get('merchant_status', 'ACTIVE'),
                risk_score=r.get('risk_score', 15.0),
                risk_level=r.get('risk_level', 'LOW'),
                settlement_account=r.get('settlement_account', 'UNKNOWN'),
                is_shared_settlement=r.get('is_shared_settlement_hub', False)
            )

        # 2. Add User Nodes
        for _, r in self.df_kyc.iterrows():
            u_id = r['user_id']
            self.G.add_node(
                u_id,
                node_type='USER',
                name=r.get('full_name', u_id),
                kyc_status=r.get('kyc_status', 'VERIFIED'),
                risk_score=r.get('risk_score', 15.0),
                risk_level=r.get('risk_level', 'LOW'),
                is_synthetic=r.get('is_synthetic_identity_suspect', False)
            )

        # 3. Add Settlement Account Hub Nodes & Edges
        for _, r in self.df_merchants[self.df_merchants['is_shared_settlement_hub']].iterrows():
            m_id = r['merchant_id']
            s_acc = r['settlement_account']
            s_node = f"ACC_{s_acc}"
            if not self.G.has_node(s_node):
                self.G.add_node(
                    s_node,
                    node_type='SETTLEMENT_ACCOUNT',
                    name=f"Settlement Hub ({s_acc})",
                    risk_score=75.0,
                    risk_level='HIGH'
                )
            self.G.add_edge(m_id, s_node, edge_type='SETTLES_INTO', weight=2.0)

        # 4. Add Transaction Edges (User -> Merchant)
        for _, r in self.df_tx.iterrows():
            u_id = r['user_id']
            m_id = r['merchant_id']
            if not self.G.has_node(u_id):
                self.G.add_node(u_id, node_type='USER', name=u_id, kyc_status='UNKNOWN', risk_score=20.0, risk_level='LOW')
            if not self.G.has_node(m_id):
                self.G.add_node(m_id, node_type='MERCHANT', name=m_id, category='General', risk_score=20.0, risk_level='LOW')

            if self.G.has_edge(u_id, m_id):
                self.G[u_id][m_id]['weight'] += 1
                self.G[u_id][m_id]['amount'] += r['amount']
            else:
                self.G.add_edge(
                    u_id,
                    m_id,
                    edge_type='TRANSACTION',
                    weight=1,
                    amount=r['amount'],
                    txn_id=r['txn_id'],
                    status=r['status']
                )

    def detect_suspicious_networks(self, outputs_dir='outputs'):
        """
        Detect connected suspicious rings:
        1. Shared settlement collusion rings
        2. High-risk dense clusters (components with high mean risk)
        """
        os.makedirs(outputs_dir, exist_ok=True)
        networks = []
        ring_id = 1

        # A. Detect Shared Settlement Collusion Hubs
        for node, data in self.G.nodes(data=True):
            if data.get('node_type') == 'SETTLEMENT_ACCOUNT':
                neighbors = list(self.G.neighbors(node))
                if len(neighbors) > 1:
                    mch_names = [self.G.nodes[n].get('name', n) for n in neighbors]
                    mch_categories = [self.G.nodes[n].get('category', 'General') for n in neighbors]
                    
                    # Compute subgraph transactions
                    sub_edges = self.G.edges(neighbors, data=True)
                    tx_count = sum([e[2].get('weight', 0) for e in sub_edges if e[2].get('edge_type') == 'TRANSACTION'])
                    tx_gmv = sum([e[2].get('amount', 0) for e in sub_edges if e[2].get('edge_type') == 'TRANSACTION'])

                    networks.append({
                        'network_id': f"RING_{ring_id:03d}",
                        'network_type': 'Shared Settlement Collusion Hub',
                        'node_count': len(neighbors) + 1,
                        'merchant_count': len(neighbors),
                        'user_count': 0,
                        'transaction_count': tx_count,
                        'total_gmv': round(tx_gmv, 2),
                        'risk_score': 85.0,
                        'risk_level': 'HIGH',
                        'entities': ", ".join(neighbors),
                        'risk_factors': f"Multiple merchants ({len(neighbors)}) pooling funds into identical settlement account {node}"
                    })
                    ring_id += 1

        # B. Detect High-Risk Connected Components
        components = list(nx.connected_components(self.G))
        for comp in components:
            if len(comp) >= 4:
                comp_nodes = [self.G.nodes[n] for n in comp]
                mchs = [n for n in comp if self.G.nodes[n].get('node_type') == 'MERCHANT']
                users = [n for n in comp if self.G.nodes[n].get('node_type') == 'USER']
                
                high_risk_count = sum([1 for n in comp if self.G.nodes[n].get('risk_level') == 'HIGH'])
                if high_risk_count >= 2:
                    sub_g = self.G.subgraph(comp)
                    tx_count = sum([d.get('weight', 0) for _, _, d in sub_g.edges(data=True) if d.get('edge_type') == 'TRANSACTION'])
                    tx_gmv = sum([d.get('amount', 0) for _, _, d in sub_g.edges(data=True) if d.get('edge_type') == 'TRANSACTION'])
                    avg_score = np.mean([self.G.nodes[n].get('risk_score', 15.0) for n in comp])

                    networks.append({
                        'network_id': f"RING_{ring_id:03d}",
                        'network_type': 'High-Risk Collusion Cluster',
                        'node_count': len(comp),
                        'merchant_count': len(mchs),
                        'user_count': len(users),
                        'transaction_count': tx_count,
                        'total_gmv': round(tx_gmv, 2),
                        'risk_score': round(avg_score, 1),
                        'risk_level': 'HIGH' if avg_score >= 60 else 'MEDIUM',
                        'entities': ", ".join(list(comp)[:10]),
                        'risk_factors': f"Dense interaction cluster connecting {len(users)} users and {len(mchs)} merchants with {high_risk_count} flagged high-risk entities"
                    })
                    ring_id += 1

        df_networks = pd.DataFrame(networks)
        if df_networks.empty:
            df_networks = pd.DataFrame(columns=['network_id', 'network_type', 'node_count', 'merchant_count', 'user_count', 'transaction_count', 'total_gmv', 'risk_score', 'risk_level', 'entities', 'risk_factors'])
        
        df_networks.to_csv(os.path.join(outputs_dir, 'suspicious_networks.csv'), index=False)
        return df_networks

    def generate_network_plot(self, max_nodes=120, selected_entity=None, filter_risk='ALL'):
        """
        Generate high-performance interactive Plotly Network visualization.
        """
        # Filter subgraph
        sub_nodes = set()
        if selected_entity and self.G.has_node(selected_entity):
            # 2-hop neighborhood
            sub_nodes.add(selected_entity)
            neighbors = set(self.G.neighbors(selected_entity))
            sub_nodes.update(neighbors)
            for nb in list(neighbors):
                sub_nodes.update(self.G.neighbors(nb))
        else:
            # Top high risk nodes + sample
            nodes_by_risk = sorted(self.G.nodes(data=True), key=lambda x: x[1].get('risk_score', 0), reverse=True)
            if filter_risk != 'ALL':
                nodes_by_risk = [n for n in nodes_by_risk if n[1].get('risk_level') == filter_risk]
            
            selected_nodes = [n[0] for n in nodes_by_risk[:max_nodes]]
            sub_nodes = set(selected_nodes)
            # Add their immediate edges
            for n in selected_nodes:
                sub_nodes.update(list(self.G.neighbors(n))[:3])

        subgraph = self.G.subgraph(list(sub_nodes)[:max_nodes])
        if len(subgraph) == 0:
            subgraph = self.G.subgraph(list(self.G.nodes())[:50])

        pos = nx.spring_layout(subgraph, k=0.35, iterations=50, seed=42)

        # Edges trace
        edge_x = []
        edge_y = []
        for edge in subgraph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1.0, color='#4A5568'),
            hoverinfo='none',
            mode='lines'
        )

        # Nodes traces grouped by entity type
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []
        node_symbol = []

        color_map = {
            'HIGH': '#EF4444',
            'MEDIUM': '#F59E0B',
            'LOW': '#10B981'
        }

        for node in subgraph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            d = subgraph.nodes[node]
            ntype = d.get('node_type', 'UNKNOWN')
            score = d.get('risk_score', 15.0)
            level = d.get('risk_level', 'LOW')
            name = d.get('name', node)

            hover = f"<b>{ntype}</b>: {node}<br>Name: {name}<br>Risk Score: {score}/100 ({level})"
            if ntype == 'MERCHANT':
                hover += f"<br>Category: {d.get('category', 'N/A')}<br>Status: {d.get('status', 'ACTIVE')}"
                node_size.append(18)
                node_symbol.append('square')
            elif ntype == 'USER':
                hover += f"<br>KYC Status: {d.get('kyc_status', 'VERIFIED')}"
                node_size.append(14)
                node_symbol.append('circle')
            else:
                hover += "<br>Type: Central Settlement Account"
                node_size.append(22)
                node_symbol.append('diamond')

            node_text.append(hover)
            node_color.append(color_map.get(level, '#6B7280'))

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[n if subgraph.degree(n) > 2 else '' for n in subgraph.nodes()],
            textposition="top center",
            textfont=dict(size=9, color='#E2E8F0'),
            hovertext=node_text,
            marker=dict(
                color=node_color,
                size=node_size,
                symbol=node_symbol,
                line=dict(width=1.5, color='#FFFFFF')
            )
        )

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=10, l=10, r=10, t=30),
                paper_bgcolor='rgba(15, 23, 42, 1)',
                plot_bgcolor='rgba(15, 23, 42, 1)',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=550
            )
        )
        return fig

    def generate_3d_network_plot(self, max_nodes=120, filter_risk='ALL'):
        """
        Generate immersive 3D Topological Fraud Network visualization using Plotly Scatter3d.
        """
        if self.G.number_of_nodes() == 0:
            self.build_heterogeneous_graph()

        # Filter nodes
        nodes_by_risk = sorted(self.G.nodes(data=True), key=lambda x: x[1].get('risk_score', 0), reverse=True)
        if filter_risk != 'ALL':
            nodes_by_risk = [n for n in nodes_by_risk if n[1].get('risk_level') == filter_risk]
        
        selected_nodes = [n[0] for n in nodes_by_risk[:max_nodes]]
        sub_nodes = set(selected_nodes)
        for n in selected_nodes:
            sub_nodes.update(list(self.G.neighbors(n))[:4])

        subgraph = self.G.subgraph(list(sub_nodes)[:max_nodes])
        if len(subgraph) == 0:
            subgraph = self.G.subgraph(list(self.G.nodes())[:60])

        # Compute 3D Spring Layout coordinates
        pos_3d = nx.spring_layout(subgraph, dim=3, k=0.4, iterations=60, seed=42)

        # 3D Edges
        edge_x = []
        edge_y = []
        edge_z = []
        for edge in subgraph.edges():
            x0, y0, z0 = pos_3d[edge[0]]
            x1, y1, z1 = pos_3d[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_z.extend([z0, z1, None])

        edge_trace_3d = go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            mode='lines',
            line=dict(color='rgba(148, 163, 184, 0.4)', width=2),
            hoverinfo='none',
            name='Money Flow / Settlement'
        )

        # 3D Nodes
        node_x = []
        node_y = []
        node_z = []
        node_text = []
        node_color = []
        node_size = []
        node_symbol = []

        color_map = {
            'HIGH': '#EF4444',
            'MEDIUM': '#F59E0B',
            'LOW': '#10B981'
        }

        for node in subgraph.nodes():
            x, y, z = pos_3d[node]
            node_x.append(x)
            node_y.append(y)
            node_z.append(z)

            d = subgraph.nodes[node]
            ntype = d.get('node_type', 'UNKNOWN')
            score = d.get('risk_score', 15.0)
            level = d.get('risk_level', 'LOW')
            name = d.get('name', node)

            hover = f"<b>{ntype}</b>: {node}<br>Name: {name}<br>Risk Score: <b>{score:.1f}/100</b> ({level})"
            if ntype == 'MERCHANT':
                hover += f"<br>Category: {d.get('category', 'N/A')}<br>Status: {d.get('status', 'ACTIVE')}"
                node_size.append(7 + (score / 15.0))
                node_symbol.append('square')
            elif ntype == 'USER':
                hover += f"<br>KYC Status: {d.get('kyc_status', 'VERIFIED')}"
                node_size.append(5 + (score / 20.0))
                node_symbol.append('circle')
            else:
                hover += "<br>Type: 💎 Central Settlement Collusion Hub"
                node_size.append(12)
                node_symbol.append('diamond')

            node_text.append(hover)
            node_color.append(score)

        node_trace_3d = go.Scatter3d(
            x=node_x, y=node_y, z=node_z,
            mode='markers',
            hoverinfo='text',
            hovertext=node_text,
            marker=dict(
                size=node_size,
                color=node_color,
                colorscale='Turbo',
                colorbar=dict(title="Risk Score", thickness=15, len=0.75, x=1.02),
                opacity=0.9,
                line=dict(color='#FFFFFF', width=1)
            ),
            name='Entities'
        )

        fig_3d = go.Figure(
            data=[edge_trace_3d, node_trace_3d],
            layout=go.Layout(
                title=dict(text="🌐 3D Topological Fraud & Collusion Universe (Interactive Orbit)", font=dict(color="#38BDF8", size=16)),
                showlegend=False,
                margin=dict(b=10, l=10, r=10, t=40),
                paper_bgcolor='rgba(11, 17, 32, 1)',
                scene=dict(
                    xaxis=dict(showbackground=False, showgrid=True, gridcolor='rgba(51, 65, 85, 0.4)', showticklabels=False, title=''),
                    yaxis=dict(showbackground=False, showgrid=True, gridcolor='rgba(51, 65, 85, 0.4)', showticklabels=False, title=''),
                    zaxis=dict(showbackground=False, showgrid=True, gridcolor='rgba(51, 65, 85, 0.4)', showticklabels=False, title=''),
                    bgcolor='rgba(11, 17, 32, 1)',
                    camera=dict(
                        eye=dict(x=1.3, y=1.3, z=1.1)
                    )
                ),
                height=650
            )
        )
        return fig_3d

    def generate_3d_risk_landscape(self):
        """
        Generate 3D Dispute & Risk Exposure Landscape across Merchant Categories.
        """
        mch_agg = self.df_merchants.groupby('merchant_category').agg(
            txn_count=('txn_count', 'sum'),
            total_gmv=('total_gmv', 'sum'),
            chargeback_count=('chargeback_count', 'sum'),
            chargeback_amount=('chargeback_amount', 'sum'),
            avg_risk=('risk_score', 'mean')
        ).reset_index().sort_values(by='total_gmv', ascending=False).head(15)

        fig_surf = go.Figure(data=[
            go.Scatter3d(
                x=mch_agg['txn_count'],
                y=mch_agg['chargeback_amount'],
                z=mch_agg['avg_risk'],
                text=[f"<b>{row['merchant_category']}</b><br>Txns: {row['txn_count']:,}<br>Disputed: ₹{row['chargeback_amount']:,.2f}<br>Avg Risk: {row['avg_risk']:.1f}/100" for _, row in mch_agg.iterrows()],
                hoverinfo='text',
                mode='markers+text',
                marker=dict(
                    size=12 + (mch_agg['chargeback_count'] * 0.2),
                    color=mch_agg['avg_risk'],
                    colorscale='Reds',
                    colorbar=dict(title="Category Risk", thickness=15, len=0.75),
                    opacity=0.9,
                    line=dict(color='#38BDF8', width=2)
                ),
                textposition='top center',
                textfont=dict(color='#F8FAFC', size=10)
            )
        ])

        fig_surf.update_layout(
            title=dict(text="📊 3D Multi-Dimensional Risk & Dispute Landscape", font=dict(color="#38BDF8", size=15)),
            paper_bgcolor='rgba(11, 17, 32, 1)',
            scene=dict(
                xaxis=dict(title='Transaction Volume', backgroundcolor='rgba(15, 23, 42, 0.6)', gridcolor='rgba(51, 65, 85, 0.4)', color='#94A3B8'),
                yaxis=dict(title='Disputed Amount (₹)', backgroundcolor='rgba(15, 23, 42, 0.6)', gridcolor='rgba(51, 65, 85, 0.4)', color='#94A3B8'),
                zaxis=dict(title='Average Risk Score (0-100)', backgroundcolor='rgba(15, 23, 42, 0.6)', gridcolor='rgba(51, 65, 85, 0.4)', color='#94A3B8'),
                bgcolor='rgba(11, 17, 32, 1)',
                camera=dict(eye=dict(x=1.5, y=1.4, z=1.2))
            ),
            margin=dict(l=10, r=10, t=40, b=10),
            height=520
        )
        return fig_surf
