"""
Interface Streamlit - Business Plan Investissement Immobilier Meuble
Comparaison SCI IS vs SARL de Famille IR
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from business_plan_immobilier import Parametres, Simulation

# ── Configuration page ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Business Plan Immobilier Meuble",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Business Plan — Investissement Immobilier Meublé")
st.caption("Comparaison **SCI à l'IS** vs **SARL de Famille à l'IR** (LMNP BIC réel)")

# ── Sidebar : paramètres ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("Paramètres")

    with st.expander("🏗️ Acquisition", expanded=True):
        nom_bien = st.text_input("Nom du bien", "Appartement T2 meublé")
        prix_achat = st.number_input("Prix d'achat (€)", 50_000, 2_000_000, 200_000, step=5_000)
        part_terrain = st.slider("Part terrain (non amortissable)", 0.10, 0.40, 0.20, 0.01,
                                 format="%.0f%%", help="En %")
        frais_notaire = st.number_input("Frais de notaire (€)", 0, 200_000, 16_000, step=500)
        travaux = st.number_input("Travaux (€)", 0, 500_000, 20_000, step=1_000)
        mobilier = st.number_input("Mobilier (€)", 0, 100_000, 10_000, step=500)

    with st.expander("💳 Financement", expanded=True):
        apport = st.number_input("Apport personnel (€)", 0, 1_000_000, 50_000, step=5_000)
        taux_interet = st.slider("Taux d'intérêt", 0.5, 7.0, 3.5, 0.05,
                                 format="%.2f%%") / 100
        duree_pret = st.slider("Durée du prêt (ans)", 5, 30, 20)
        taux_assurance_pret = st.slider("Assurance emprunteur", 0.10, 0.80, 0.30, 0.05,
                                        format="%.2f%%") / 100

    with st.expander("💰 Revenus locatifs"):
        loyer_mensuel = st.number_input("Loyer mensuel brut (€)", 200, 10_000, 1_200, step=50)
        charges_recup = st.number_input("Charges récup. mensuelles (€)", 0, 500, 100, step=10)
        taux_vacance = st.slider("Taux de vacance", 0.0, 20.0, 5.0, 0.5, format="%.1f%%") / 100
        reval_loyer = st.slider("Revalorisation loyers/an", 0.0, 5.0, 2.0, 0.1, format="%.1f%%") / 100

    with st.expander("📋 Charges annuelles"):
        taxe_fonciere = st.number_input("Taxe foncière (€)", 0, 10_000, 1_500, step=100)
        charges_copro = st.number_input("Charges copro non récup. (€)", 0, 10_000, 1_200, step=100)
        assurance_pno = st.number_input("Assurance PNO (€)", 0, 5_000, 400, step=50)
        taux_gestion = st.slider("Gestion locative", 0.0, 15.0, 8.0, 0.5, format="%.1f%%") / 100
        entretien = st.number_input("Entretien/provisions (€)", 0, 10_000, 500, step=100)
        compta = st.number_input("Expert-comptable (€)", 0, 5_000, 1_500, step=100)
        reval_charges = st.slider("Revalorisation charges/an", 0.0, 5.0, 2.0, 0.1,
                                  format="%.1f%%") / 100

    with st.expander("⚙️ Amortissements"):
        dur_bat = st.slider("Durée amort. bâtiment (ans)", 20, 50, 30)
        dur_trav = st.slider("Durée amort. travaux (ans)", 5, 20, 15)
        dur_mob = st.slider("Durée amort. mobilier (ans)", 5, 15, 7)

    with st.expander("🧾 Fiscalité IR (SARL)"):
        tmi = st.select_slider("Tranche marginale d'imposition",
                               options=[0.0, 0.11, 0.30, 0.41, 0.45],
                               value=0.30,
                               format_func=lambda x: f"{x*100:.0f}%")
        taux_ps = 0.172
        st.caption(f"Prélèvements sociaux : 17.2% (fixe)")

    with st.expander("🏢 Fiscalité IS (SCI)"):
        taux_is_reduit = st.slider("IS réduit", 10, 20, 15, format="%d%%") / 100
        seuil_is = st.number_input("Seuil IS réduit (€)", 10_000, 100_000, 42_500, step=500)
        taux_is_normal = st.slider("IS normal", 20, 33, 25, format="%d%%") / 100
        taux_pfu = st.slider("PFU dividendes", 20, 35, 30, format="%d%%") / 100

    with st.expander("🏷️ Revente"):
        duree_detention = st.slider("Durée de détention (ans)", 5, 30, 12)
        prix_revente = st.number_input("Prix de revente (€)", 50_000, 5_000_000, 260_000, step=5_000)
        frais_agence = st.slider("Frais d'agence vente", 2.0, 10.0, 5.0, 0.5, format="%.1f%%") / 100

# ── Construction paramètres & simulation ─────────────────────────────────────
params = Parametres(
    nom_bien=nom_bien,
    prix_achat=prix_achat,
    part_terrain=part_terrain,
    frais_notaire=frais_notaire,
    travaux=travaux,
    mobilier=mobilier,
    apport=apport,
    taux_interet=taux_interet,
    duree_pret=duree_pret,
    taux_assurance_pret=taux_assurance_pret,
    loyer_mensuel=loyer_mensuel,
    charges_recup_mensuelles=charges_recup,
    taux_vacance=taux_vacance,
    revalorisation_loyer=reval_loyer,
    taxe_fonciere=taxe_fonciere,
    charges_copro=charges_copro,
    assurance_pno=assurance_pno,
    taux_gestion=taux_gestion,
    entretien=entretien,
    honoraires_comptables=compta,
    revalorisation_charges=reval_charges,
    duree_amort_batiment=dur_bat,
    duree_amort_travaux=dur_trav,
    duree_amort_mobilier=dur_mob,
    tmi=tmi,
    taux_ps=taux_ps,
    taux_is_reduit=taux_is_reduit,
    seuil_is_reduit=seuil_is,
    taux_is_normal=taux_is_normal,
    taux_pfu=taux_pfu,
    duree_detention=duree_detention,
    prix_revente=prix_revente,
    frais_agence_vente=frais_agence,
)

sim = Simulation(params)
rows_is = sim.sim_sci_is()
rows_ir = sim.sim_sarl_ir()
pv_is = sim.pv_sci_is(rows_is[-1]["vnc"])
pv_ir = sim.pv_sarl_ir()
cap_rest_is = rows_is[-1]["cap_restant"]
cap_rest_ir = rows_ir[-1]["cap_restant"]
treso_sci = pv_is["net_sci"] - cap_rest_is
net_assoc_is = treso_sci - treso_sci * params.taux_pfu
net_assoc_ir = pv_ir["net_associes"] - cap_rest_ir

from business_plan_immobilier import calculer_tri
flux_is = [-params.apport] + [r["cf_net"] for r in rows_is]
flux_is[-1] += net_assoc_is
flux_ir = [-params.apport] + [r["cf_net"] for r in rows_ir]
flux_ir[-1] += net_assoc_ir
tri_is = calculer_tri(flux_is)
tri_ir = calculer_tri(flux_ir)
gain_is = sum(flux_is)
gain_ir = sum(flux_ir)

invest_total = sim.invest_total
capital_emprunte = sim.capital_emprunte

# ── KPIs ─────────────────────────────────────────────────────────────────────
st.subheader("Synthèse")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Investissement total", f"{invest_total:,.0f} €")
col2.metric("Capital emprunté", f"{capital_emprunte:,.0f} €")
loy1 = sim.loyers_annee(1)
ch1 = sim.charges_annee(1)
rdt_brut = params.loyer_mensuel * 12 / invest_total * 100
rdt_net = (loy1["encaisse"] - ch1["exploit"]) / invest_total * 100
col3.metric("Rendement brut (an 1)", f"{rdt_brut:.2f}%")
col4.metric("Rendement net charges (an 1)", f"{rdt_net:.2f}%")

st.divider()

# ── Comparatif KPIs ───────────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.markdown("### 🏢 SCI à l'IS")
    k1, k2, k3 = st.columns(3)
    k1.metric("Net associés (après cession + PFU)",
              f"{net_assoc_is:,.0f} €",
              delta=None)
    k2.metric("IS sur plus-value", f"{pv_is['is_pv']:,.0f} €",
              delta=f"PV imposable : {pv_is['pv_brute']:,.0f} €",
              delta_color="inverse")
    tri_is_label = f"{tri_is*100:.2f}%" if tri_is is not None else "< 0 (perte)"
    k3.metric("TRI net sur apport", tri_is_label)

with c2:
    st.markdown("### 👨‍👩‍👧 SARL de Famille à l'IR")
    k1, k2, k3 = st.columns(3)
    delta_v = net_assoc_ir - net_assoc_is
    k1.metric("Net associés (après cession)",
              f"{net_assoc_ir:,.0f} €",
              delta=f"+{delta_v:,.0f} € vs SCI IS" if delta_v > 0 else f"{delta_v:,.0f} € vs SCI IS")
    k2.metric("Impôts sur plus-value", f"{pv_ir['total_impots_pv']:,.0f} €",
              delta=f"PV brute : {pv_ir['pv_brute']:,.0f} €",
              delta_color="inverse")
    tri_ir_label = f"{tri_ir*100:.2f}%" if tri_ir is not None else "< 0 (perte)"
    k3.metric("TRI net sur apport", tri_ir_label)

st.divider()

# ── Graphiques ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Cash Flows", "💸 Fiscalité", "📊 Plus-value cession", "📋 Tableaux détaillés"
])

annees = list(range(1, params.duree_detention + 1))

# ─── Tab 1 : Cash flows ───────────────────────────────────────────────────────
with tab1:
    col_a, col_b = st.columns(2)

    cf_brut_is = [r["cf_avant_is"] for r in rows_is]
    cf_net_is  = [r["cf_net"] for r in rows_is]
    cf_brut_ir = [r["cf_avant_impot"] for r in rows_ir]
    cf_net_ir  = [r["cf_net"] for r in rows_ir]

    cum_is = []
    cum_ir = []
    s_is = s_ir = 0.0
    for v_is, v_ir in zip(cf_net_is, cf_net_ir):
        s_is += v_is; cum_is.append(s_is)
        s_ir += v_ir; cum_ir.append(s_ir)

    with col_a:
        fig = go.Figure()
        fig.add_bar(x=annees, y=cf_net_is, name="SCI IS", marker_color="#ef553b",
                    opacity=0.8)
        fig.add_bar(x=annees, y=cf_net_ir, name="SARL IR", marker_color="#636efa",
                    opacity=0.8)
        fig.add_hline(y=0, line_dash="dot", line_color="gray")
        fig.update_layout(title="Cash flow net annuel (après impôts)",
                          xaxis_title="Année", yaxis_title="EUR",
                          barmode="group", legend=dict(orientation="h"),
                          height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig2 = go.Figure()
        fig2.add_scatter(x=annees, y=cum_is, mode="lines+markers",
                         name="SCI IS cumulé", line=dict(color="#ef553b", width=2))
        fig2.add_scatter(x=annees, y=cum_ir, mode="lines+markers",
                         name="SARL IR cumulé", line=dict(color="#636efa", width=2))
        fig2.add_hline(y=0, line_dash="dot", line_color="gray")
        fig2.update_layout(title="Cash flow net cumulé (exploitation)",
                           xaxis_title="Année", yaxis_title="EUR",
                           legend=dict(orientation="h"), height=380)
        st.plotly_chart(fig2, use_container_width=True)

    # Loyers vs Charges évolution
    loy_vals = [sim.loyers_annee(n)["encaisse"] for n in annees]
    ch_vals  = [sim.charges_annee(n)["total_deductible"] for n in annees]
    men_vals = []
    for n in annees:
        if n <= params.duree_pret:
            r = sim.pret[n - 1]
            men_vals.append(r["capital"] + r["interets"] + r["assurance"])
        else:
            men_vals.append(0)

    fig3 = go.Figure()
    fig3.add_scatter(x=annees, y=loy_vals, mode="lines+markers", name="Loyers encaissés",
                     line=dict(color="#00cc96", width=2))
    fig3.add_scatter(x=annees, y=[c + m for c, m in zip(ch_vals, men_vals)],
                     mode="lines+markers", name="Charges + mensualités",
                     line=dict(color="#ff7f0e", width=2))
    fig3.update_layout(title="Loyers encaissés vs Charges totales décaissées",
                       xaxis_title="Année", yaxis_title="EUR",
                       legend=dict(orientation="h"), height=350)
    st.plotly_chart(fig3, use_container_width=True)

# ─── Tab 2 : Fiscalité ────────────────────────────────────────────────────────
with tab2:
    col_a, col_b = st.columns(2)

    with col_a:
        is_vals = [r["is"] for r in rows_is]
        fig = go.Figure()
        fig.add_bar(x=annees, y=is_vals, name="IS", marker_color="#ef553b")
        fig.update_layout(title="IS annuel — SCI à l'IS",
                          xaxis_title="Année", yaxis_title="EUR", height=320)
        st.plotly_chart(fig, use_container_width=True)

        res_is = [r["res_fiscal"] for r in rows_is]
        vnc_vals = [r["vnc"] for r in rows_is]
        fig2 = go.Figure()
        fig2.add_scatter(x=annees, y=res_is, mode="lines+markers",
                         name="Résultat fiscal IS", line=dict(color="#ef553b"))
        fig2.add_scatter(x=annees, y=vnc_vals, mode="lines+markers",
                         name="VNC", line=dict(color="#aaa", dash="dash"))
        fig2.update_layout(title="Résultat fiscal & VNC — SCI IS",
                           xaxis_title="Année", yaxis_title="EUR", height=320)
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        irps_vals = [r["impot_total"] for r in rows_ir]
        fig3 = go.Figure()
        fig3.add_bar(x=annees, y=[r["ir"] for r in rows_ir], name="IR", marker_color="#636efa")
        fig3.add_bar(x=annees, y=[r["ps"] for r in rows_ir], name="PS", marker_color="#ab63fa")
        fig3.update_layout(title="IR + PS annuels — SARL IR",
                           barmode="stack", xaxis_title="Année", yaxis_title="EUR",
                           legend=dict(orientation="h"), height=320)
        st.plotly_chart(fig3, use_container_width=True)

        res_ir = [r["res_fiscal"] for r in rows_ir]
        amort_ded = [r["amort_deductible"] for r in rows_ir]
        amort_diff = [r["amort_differe"] for r in rows_ir]
        fig4 = go.Figure()
        fig4.add_scatter(x=annees, y=res_ir, mode="lines+markers",
                         name="Résultat fiscal", line=dict(color="#636efa"))
        fig4.add_scatter(x=annees, y=amort_ded, mode="lines+markers",
                         name="Amort. déduit", line=dict(color="#00cc96"))
        fig4.add_scatter(x=annees, y=amort_diff, mode="lines+markers",
                         name="Amort. différé cumulé", line=dict(color="#aaa", dash="dash"))
        fig4.update_layout(title="Résultat fiscal & amortissements — SARL IR",
                           xaxis_title="Année", yaxis_title="EUR",
                           legend=dict(orientation="h"), height=320)
        st.plotly_chart(fig4, use_container_width=True)

# ─── Tab 3 : Plus-value ───────────────────────────────────────────────────────
with tab3:
    col_a, col_b = st.columns(2)

    # SCI IS waterfall
    with col_a:
        st.markdown("#### SCI à l'IS — Cession")
        labels_is = [
            "Prix de vente brut",
            "Frais d'agence",
            "VNC (déduite)",
            "IS sur plus-value",
            "Capital prêt restant",
            "PFU dividendes (30%)",
            "Net associés",
        ]
        values_is = [
            pv_is["prix_brut"],
            -pv_is["frais_agence"],
            -pv_is["vnc"],
            -pv_is["is_pv"],
            -cap_rest_is,
            -(treso_sci * params.taux_pfu),
            net_assoc_is,
        ]
        measure_is = ["absolute", "relative", "relative", "relative",
                      "relative", "relative", "total"]
        colors_is = ["#00cc96" if v >= 0 else "#ef553b" for v in values_is]

        fig_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=measure_is,
            x=labels_is,
            y=values_is,
            connector=dict(line=dict(color="rgb(63,63,63)")),
            increasing=dict(marker_color="#00cc96"),
            decreasing=dict(marker_color="#ef553b"),
            totals=dict(marker_color="#636efa"),
            text=[f"{v:,.0f} €" for v in values_is],
            textposition="outside",
        ))
        fig_wf.update_layout(title="Décomposition du produit de cession — SCI IS",
                             height=480, yaxis_title="EUR")
        st.plotly_chart(fig_wf, use_container_width=True)
        st.info(f"**Plus-value imposable (IS)** : {pv_is['pv_brute']:,.0f} € "
                f"= Prix vente net − VNC ({rows_is[-1]['vnc']:,.0f} €)")

    # SARL IR waterfall
    with col_b:
        st.markdown("#### SARL de Famille IR — Cession")
        ir_abatt = pv_ir["pv_brute"] * pv_ir["abatt_ir_pct"]
        ps_abatt = pv_ir["pv_brute"] * pv_ir["abatt_ps_pct"]
        labels_ir = [
            "Prix de vente brut",
            "Frais d'agence",
            "Prix acquisition (déduit)",
            f"Abattement IR ({pv_ir['abatt_ir_pct']*100:.0f}%)",
            "IR forfaitaire (19%)",
            f"Abattement PS ({pv_ir['abatt_ps_pct']*100:.2f}%)",
            "Prél. sociaux (17.2%)",
            "Capital prêt restant",
            "Net associés",
        ]
        values_ir = [
            pv_ir["prix_brut"],
            -pv_ir["frais_agence"],
            -pv_ir["prix_acquisition"],
            ir_abatt,
            -pv_ir["ir_pv"],
            ps_abatt,
            -pv_ir["ps_pv"],
            -cap_rest_ir,
            net_assoc_ir,
        ]
        measure_ir = ["absolute"] + ["relative"] * (len(values_ir) - 2) + ["total"]

        fig_wf2 = go.Figure(go.Waterfall(
            orientation="v",
            measure=measure_ir,
            x=labels_ir,
            y=values_ir,
            connector=dict(line=dict(color="rgb(63,63,63)")),
            increasing=dict(marker_color="#00cc96"),
            decreasing=dict(marker_color="#ef553b"),
            totals=dict(marker_color="#636efa"),
            text=[f"{v:,.0f} €" for v in values_ir],
            textposition="outside",
        ))
        fig_wf2.update_layout(title="Décomposition du produit de cession — SARL IR",
                              height=480, yaxis_title="EUR")
        st.plotly_chart(fig_wf2, use_container_width=True)
        st.info(f"**Plus-value brute (LMNP)** : {pv_ir['pv_brute']:,.0f} € "
                f"= Prix vente net − Prix acquisition initial ({pv_ir['prix_acquisition']:,.0f} €) "
                f"| Amortissements **non** réintégrés")

    # Comparaison pie impôts cession
    st.markdown("#### Comparaison fiscalité cession")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        fig_pie_is = go.Figure(go.Pie(
            labels=["IS sur PV", "Net distribué", "PFU dividendes"],
            values=[pv_is["is_pv"], net_assoc_is, treso_sci * params.taux_pfu],
            hole=0.45,
            marker_colors=["#ef553b", "#636efa", "#ab63fa"],
        ))
        fig_pie_is.update_layout(title="SCI IS — Répartition produit de cession",
                                 height=300, showlegend=True,
                                 legend=dict(orientation="h"))
        st.plotly_chart(fig_pie_is, use_container_width=True)

    with col_p2:
        fig_pie_ir = go.Figure(go.Pie(
            labels=["Impôts PV", "Capital prêt", "Net associés"],
            values=[pv_ir["total_impots_pv"], cap_rest_ir, net_assoc_ir],
            hole=0.45,
            marker_colors=["#ef553b", "#ff7f0e", "#00cc96"],
        ))
        fig_pie_ir.update_layout(title="SARL IR — Répartition produit de cession",
                                 height=300, showlegend=True,
                                 legend=dict(orientation="h"))
        st.plotly_chart(fig_pie_ir, use_container_width=True)

    with col_p3:
        fig_bar_comp = go.Figure()
        fig_bar_comp.add_bar(
            x=["SCI IS", "SARL IR"],
            y=[net_assoc_is, net_assoc_ir],
            marker_color=["#ef553b", "#00cc96"],
            text=[f"{net_assoc_is:,.0f} €", f"{net_assoc_ir:,.0f} €"],
            textposition="outside",
        )
        fig_bar_comp.update_layout(title="Net perçu par les associés",
                                   yaxis_title="EUR", height=300)
        st.plotly_chart(fig_bar_comp, use_container_width=True)

# ─── Tab 4 : Tableaux détaillés ───────────────────────────────────────────────
with tab4:
    st.markdown("### SCI à l'IS — Détail annuel")
    df_is = pd.DataFrame([{
        "Année": r["n"],
        "Loyers imposables (€)": round(r["loyers"]["imposable"]),
        "Charges déductibles (€)": round(r["charges"]["total_deductible"]),
        "dont intérêts (€)": round(r["charges"]["interets"]),
        "Amortissement (€)": round(r["amort"]),
        "Résultat fiscal (€)": round(r["res_fiscal"]),
        "IS (€)": round(r["is"]),
        "CF avant IS (€)": round(r["cf_avant_is"]),
        "CF net (€)": round(r["cf_net"]),
        "VNC (€)": round(r["vnc"]),
        "Déficit reporté (€)": round(r["deficit_reporte"]),
    } for r in rows_is])

    st.dataframe(
        df_is.style
            .format("{:,.0f}", subset=[c for c in df_is.columns if c != "Année"])
            .applymap(lambda v: "color: #ef553b" if isinstance(v, (int, float)) and v < 0 else "",
                      subset=[c for c in df_is.columns if c != "Année"])
            .background_gradient(subset=["CF net (€)"], cmap="RdYlGn"),
        use_container_width=True, height=420
    )

    st.markdown("### SARL de Famille IR — Détail annuel")
    df_ir = pd.DataFrame([{
        "Année": r["n"],
        "Loyers imposables (€)": round(r["loyers"]["imposable"]),
        "Charges déductibles (€)": round(r["charges"]["total_deductible"]),
        "dont intérêts (€)": round(r["charges"]["interets"]),
        "Amort. calculé (€)": round(r["amort_calc"]),
        "Amort. déduit (€)": round(r["amort_deductible"]),
        "Amort. différé cumulé (€)": round(r["amort_differe"]),
        "Résultat fiscal (€)": round(r["res_fiscal"]),
        "IR (€)": round(r["ir"]),
        "PS (€)": round(r["ps"]),
        "CF avant impôts (€)": round(r["cf_avant_impot"]),
        "CF net (€)": round(r["cf_net"]),
    } for r in rows_ir])

    st.dataframe(
        df_ir.style
            .format("{:,.0f}", subset=[c for c in df_ir.columns if c != "Année"])
            .applymap(lambda v: "color: #ef553b" if isinstance(v, (int, float)) and v < 0 else "",
                      subset=[c for c in df_ir.columns if c != "Année"])
            .background_gradient(subset=["CF net (€)"], cmap="RdYlGn"),
        use_container_width=True, height=420
    )

    # Tableau comparatif final
    st.markdown("### Tableau comparatif de synthèse")
    df_comp = pd.DataFrame({
        "Indicateur": [
            "Investissement total",
            "Capital emprunté",
            "Apport",
            "—",
            "Total IS / IR+PS sur exploitation",
            "Cash flow net cumulé (exploitation)",
            "——",
            "Plus-value brute",
            "Impôts sur plus-value",
            "Capital prêt restant",
            "Net perçu par les associés",
            "———",
            "TRI net sur apport",
            "Gain / perte net global",
        ],
        "SCI à l'IS": [
            f"{invest_total:,.0f} €",
            f"{capital_emprunte:,.0f} €",
            f"{params.apport:,.0f} €",
            "",
            f"{sum(r['is'] for r in rows_is):,.0f} €",
            f"{sum(r['cf_net'] for r in rows_is):,.0f} €",
            "",
            f"{pv_is['pv_brute']:,.0f} €",
            f"{pv_is['is_pv']:,.0f} €",
            f"{cap_rest_is:,.0f} €",
            f"{net_assoc_is:,.0f} €",
            "",
            f"{tri_is*100:.2f}%" if tri_is is not None else "N/A (perte)",
            f"{gain_is:,.0f} €",
        ],
        "SARL Famille IR": [
            f"{invest_total:,.0f} €",
            f"{capital_emprunte:,.0f} €",
            f"{params.apport:,.0f} €",
            "",
            f"{sum(r['impot_total'] for r in rows_ir):,.0f} €",
            f"{sum(r['cf_net'] for r in rows_ir):,.0f} €",
            "",
            f"{pv_ir['pv_brute']:,.0f} €",
            f"{pv_ir['total_impots_pv']:,.0f} €",
            f"{cap_rest_ir:,.0f} €",
            f"{net_assoc_ir:,.0f} €",
            "",
            f"{tri_ir*100:.2f}%" if tri_ir is not None else "N/A (perte)",
            f"{gain_ir:,.0f} €",
        ],
    })
    st.dataframe(df_comp, use_container_width=True, hide_index=True, height=530)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Hypothèses fiscales 2024 — Résultats à titre indicatif. "
    "Consultez un expert-comptable ou un CGP avant toute décision d'investissement."
)
