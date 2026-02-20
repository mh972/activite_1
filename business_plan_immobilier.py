#!/usr/bin/env python3
"""
============================================================
  BUSINESS PLAN - INVESTISSEMENT IMMOBILIER MEUBLE
  Comparaison : SCI a l'IS vs SARL de Famille a l'IR
  Duree de detention : 12 ans
============================================================

Hypotheses fiscales (2024) :
  SCI IS  : IS 15% jusqu'a 42 500 EUR, 25% au-dela
            PFU 30% (12.8% IR + 17.2% PS) sur dividendes
            Plus-value = prix vente - Valeur Nette Comptable (VNC)
            PV taxee a l'IS (comme resultat ordinaire)

  SARL IR : Regime LMNP (Location Meublee Non Professionnelle) BIC reel
            IR a la TMI + Prelevements sociaux 17.2%
            Amortissements non deductibles au-dela du resultat
            Amortissements differes reportables sans limite de temps
            Deficit de charges reportable 10 ans
            Plus-value = prix vente - prix d'acquisition INITIAL
            (amortissements non reintegres en LMNP)
            Abattements IR : 6%/an de la 6e a la 21e annee
            Abattements PS : 1.65%/an de la 6e a la 21e annee
"""

from dataclasses import dataclass
from typing import List, Dict


# ============================================================
#  PARAMETRES DE L'INVESTISSEMENT (modifiez cette section)
# ============================================================

@dataclass
class Parametres:
    # --- Bien immobilier ---
    nom_bien: str = "Appartement T2 meuble"
    prix_achat: float = 200_000       # Prix d'achat du bien hors frais (EUR)
    part_terrain: float = 0.20        # Part non amortissable (terrain) : 20 %
    frais_notaire: float = 16_000     # Frais de notaire (~8 %)
    travaux: float = 20_000           # Travaux de renovation
    mobilier: float = 10_000          # Mobilier et equipements

    # --- Financement ---
    apport: float = 50_000            # Apport personnel
    taux_interet: float = 0.035       # Taux annuel du pret (3.5 %)
    duree_pret: int = 20              # Duree du pret en annees
    taux_assurance_pret: float = 0.003  # Assurance emprunteur sur capital initial (0.3 %)

    # --- Revenus locatifs ---
    loyer_mensuel: float = 1_200      # Loyer mensuel brut (charges incluses)
    charges_recup_mensuelles: float = 100   # Charges refacturees au locataire (non imposables)
    taux_vacance: float = 0.05        # Taux de vacance locative (5 %)
    revalorisation_loyer: float = 0.02      # Revalorisation annuelle IRL (2 %)

    # --- Charges annuelles d'exploitation ---
    taxe_fonciere: float = 1_500      # Taxe fonciere
    charges_copro: float = 1_200      # Charges copropriete non recuperables
    assurance_pno: float = 400        # Assurance Proprietaire Non Occupant
    taux_gestion: float = 0.08        # Honoraires gestion locative (% loyers encaisses)
    entretien: float = 500            # Entretien courant / provisions
    honoraires_comptables: float = 1_500    # Expert-comptable / CGP
    revalorisation_charges: float = 0.02    # Revalorisation annuelle des charges (2 %)

    # --- Amortissements comptables ---
    duree_amort_batiment: int = 30    # Batiment (hors terrain) : 30 ans
    duree_amort_travaux: int = 15     # Travaux : 15 ans
    duree_amort_mobilier: int = 7     # Mobilier : 7 ans

    # --- Fiscalite IR (SARL de famille) ---
    tmi: float = 0.30                 # Tranche marginale d'imposition
    taux_ps: float = 0.172            # Prelevements sociaux (17.2 %)

    # --- Fiscalite IS (SCI) ---
    taux_is_reduit: float = 0.15      # IS reduit : 15 % jusqu'au seuil
    seuil_is_reduit: float = 42_500   # Seuil IS reduit (EUR)
    taux_is_normal: float = 0.25      # IS normal : 25 %
    taux_pfu: float = 0.30            # Flat Tax (PFU) sur dividendes : 30 %

    # --- Revente ---
    duree_detention: int = 12         # Duree de detention en annees
    prix_revente: float = 260_000     # Prix de revente estime (EUR)
    frais_agence_vente: float = 0.05  # Frais d'agence a la vente (5 %)


# ============================================================
#  FONCTIONS UTILITAIRES
# ============================================================

def mensualite_pret(capital: float, taux_annuel: float, duree_ans: int) -> float:
    """Calcule la mensualite hors assurance d'un pret immobilier."""
    if taux_annuel == 0:
        return capital / (duree_ans * 12)
    tm = taux_annuel / 12
    n = duree_ans * 12
    return capital * tm * (1 + tm) ** n / ((1 + tm) ** n - 1)


def tableau_pret(capital: float, taux_annuel: float, duree_ans: int,
                 taux_assurance: float) -> List[Dict]:
    """Retourne le tableau d'amortissement annuel du pret."""
    m = mensualite_pret(capital, taux_annuel, duree_ans)
    tm = taux_annuel / 12
    cr = capital
    tableau = []
    for annee in range(1, duree_ans + 1):
        interets_a = capital_a = assurance_a = 0.0
        for _ in range(12):
            if cr <= 0:
                break
            i = cr * tm
            k = min(m - i, cr)
            interets_a += i
            capital_a += k
            cr -= k
        assurance_a = capital * taux_assurance   # assurance sur capital initial (simplifiee)
        tableau.append({
            "interets": interets_a,
            "capital": capital_a,
            "assurance": assurance_a,
            "capital_restant": max(0.0, cr),
        })
    return tableau


def calculer_tri(flux: List[float]):
    """
    Taux de Rendement Interne par bisection (methode robuste).
    Retourne None si aucun TRI reel n'existe dans [-99%, +500%].
    """
    def vpn(r):
        return sum(f / (1 + r) ** i for i, f in enumerate(flux))

    lo, hi = -0.99, 5.0
    vpn_lo = vpn(lo)
    vpn_hi = vpn(hi)

    # Pas de changement de signe -> pas de TRI dans la plage
    if vpn_lo * vpn_hi > 0:
        return None

    for _ in range(200):
        mid = (lo + hi) / 2.0
        if abs(hi - lo) < 1e-9:
            break
        if vpn(mid) * vpn_lo > 0:
            lo = mid
            vpn_lo = vpn(lo)
        else:
            hi = mid
    return (lo + hi) / 2.0


def calcul_is(resultat: float, p: Parametres) -> float:
    """Calcule l'IS pour un resultat donne."""
    if resultat <= 0:
        return 0.0
    if resultat <= p.seuil_is_reduit:
        return resultat * p.taux_is_reduit
    return (p.seuil_is_reduit * p.taux_is_reduit
            + (resultat - p.seuil_is_reduit) * p.taux_is_normal)


def calcul_surtaxe_pv(pv_imposable: float) -> float:
    """
    Surtaxe sur les plus-values immobilières élevées (art. 1609 nonies G CGI).
    Taux applique a la PV nette imposable (avant surtaxe).
    Note : une attenuation progressive s'applique pres des seuils ; cette
    implementation est simplifiee (taux plein).
    """
    if pv_imposable <= 50_000:
        return 0.0
    elif pv_imposable <= 100_000:
        return pv_imposable * 0.02
    elif pv_imposable <= 150_000:
        return pv_imposable * 0.03
    elif pv_imposable <= 200_000:
        return pv_imposable * 0.04
    elif pv_imposable <= 250_000:
        return pv_imposable * 0.05
    else:
        return pv_imposable * 0.06


# ============================================================
#  CLASSE DE SIMULATION
# ============================================================

class Simulation:
    def __init__(self, p: Parametres):
        self.p = p
        p_ = p

        # Investissement total
        self.invest_total = p_.prix_achat + p_.frais_notaire + p_.travaux + p_.mobilier
        self.capital_emprunte = self.invest_total - p_.apport

        # Bases amortissables
        self.val_batiment = p_.prix_achat * (1 - p_.part_terrain)
        self.val_terrain = p_.prix_achat * p_.part_terrain

        # Amortissements annuels
        self.amort_bat = self.val_batiment / p_.duree_amort_batiment
        self.amort_trav = p_.travaux / p_.duree_amort_travaux
        self.amort_mob = p_.mobilier / p_.duree_amort_mobilier

        # Tableau d'amortissement pret
        self.pret = tableau_pret(
            self.capital_emprunte, p_.taux_interet,
            p_.duree_pret, p_.taux_assurance_pret
        )

    # ----------------------------------------------------------
    #  Revenus et charges annuels
    # ----------------------------------------------------------

    def loyers_annee(self, n: int) -> Dict:
        p = self.p
        fact = (1 + p.revalorisation_loyer) ** (n - 1)
        loyer_brut = p.loyer_mensuel * 12 * fact
        charges_recup = p.charges_recup_mensuelles * 12 * fact
        encaisse = loyer_brut * (1 - p.taux_vacance)
        # Part imposable = loyers - charges récupérables (qui ne sont pas des revenus nets)
        imposable = (loyer_brut - charges_recup) * (1 - p.taux_vacance)
        return {
            "loyer_brut": loyer_brut,
            "encaisse": encaisse,
            "charges_recup": charges_recup * (1 - p.taux_vacance),
            "imposable": imposable,
        }

    def charges_annee(self, n: int) -> Dict:
        p = self.p
        fact = (1 + p.revalorisation_charges) ** (n - 1)
        loy = self.loyers_annee(n)

        fonciere = p.taxe_fonciere * fact
        copro = p.charges_copro * fact
        assurance = p.assurance_pno * fact
        gestion = loy["encaisse"] * p.taux_gestion
        entretien = p.entretien * fact
        compta = p.honoraires_comptables * fact
        exploit = fonciere + copro + assurance + gestion + entretien + compta

        interets = assurance_pret = 0.0
        if n <= p.duree_pret:
            row = self.pret[n - 1]
            interets = row["interets"]
            assurance_pret = row["assurance"]

        return {
            "fonciere": fonciere,
            "copro": copro,
            "assurance_pno": assurance,
            "gestion": gestion,
            "entretien": entretien,
            "compta": compta,
            "exploit": exploit,
            "interets": interets,
            "assurance_pret": assurance_pret,
            "total_deductible": exploit + interets + assurance_pret,
        }

    def amort_annee(self, n: int) -> float:
        p = self.p
        a = 0.0
        if n <= p.duree_amort_batiment:
            a += self.amort_bat
        if n <= p.duree_amort_travaux:
            a += self.amort_trav
        if n <= p.duree_amort_mobilier:
            a += self.amort_mob
        return a

    # ----------------------------------------------------------
    #  Simulation SCI a l'IS
    # ----------------------------------------------------------

    def sim_sci_is(self) -> List[Dict]:
        """
        Simulation annuelle SCI a l'IS.
        - Amortissements deductibles sans restriction
        - Deficits reportables en avant sans limite de duree
        - IS sur le resultat net comptable
        """
        rows = []
        deficit = 0.0
        vnc = self.invest_total - self.val_terrain  # valeur amortissable initiale

        for n in range(1, self.p.duree_detention + 1):
            loy = self.loyers_annee(n)
            ch = self.charges_annee(n)
            amort = self.amort_annee(n)

            res_brut = loy["imposable"] - ch["total_deductible"] - amort
            res_fiscal = res_brut + deficit  # deficit est negatif -> reduit le resultat
            # On stocke le deficit cumule (signe positif = montant reportable)
            if res_fiscal < 0:
                deficit = res_fiscal        # negatif
                res_fiscal = 0.0
            else:
                deficit = 0.0

            is_du = calcul_is(res_fiscal, self.p)

            # Cash flow reel
            mensualite_totale = 0.0
            cap_restant = 0.0
            if n <= self.p.duree_pret:
                row_p = self.pret[n - 1]
                mensualite_totale = row_p["capital"] + row_p["interets"] + row_p["assurance"]
                cap_restant = row_p["capital_restant"]

            cf_avant_is = loy["encaisse"] - mensualite_totale - ch["exploit"]
            cf_net = cf_avant_is - is_du
            vnc -= amort

            rows.append({
                "n": n,
                "loyers": loy,
                "charges": ch,
                "amort": amort,
                "res_fiscal": res_fiscal,
                "is": is_du,
                "cf_avant_is": cf_avant_is,
                "cf_net": cf_net,
                "cap_restant": cap_restant,
                "vnc": max(0.0, vnc),
                "deficit_reporte": abs(deficit),
            })
        return rows

    def pv_sci_is(self, vnc_finale: float) -> Dict:
        """Plus-value SCI IS : taxee a l'IS sur prix_vente_net - VNC."""
        p = self.p
        net_agence = p.prix_revente * (1 - p.frais_agence_vente)
        pv = net_agence - vnc_finale
        is_pv = calcul_is(pv, p)
        return {
            "prix_brut": p.prix_revente,
            "frais_agence": p.prix_revente * p.frais_agence_vente,
            "net_agence": net_agence,
            "vnc": vnc_finale,
            "pv_brute": pv,
            "is_pv": is_pv,
            "net_sci": pv - is_pv,
        }

    # ----------------------------------------------------------
    #  Simulation SARL de Famille a l'IR (LMNP BIC reel)
    # ----------------------------------------------------------

    def sim_sarl_ir(self) -> List[Dict]:
        """
        Simulation annuelle SARL de famille IR - regime LMNP BIC reel.
        Regles LMNP :
          1) Les amortissements ne peuvent PAS creer de deficit.
          2) Les amortissements non deduits sont reportables sans limite.
          3) Un deficit provenant des charges (hors amort) est reportable 10 ans.
        """
        rows = []
        deficit_charges = 0.0      # Deficit sur charges (hors amort), reportable 10 ans
        amort_differe = 0.0        # Amortissements non déduits, reportables illimites

        for n in range(1, self.p.duree_detention + 1):
            loy = self.loyers_annee(n)
            ch = self.charges_annee(n)
            amort_calc = self.amort_annee(n)

            # Resultat avant amortissements (en appliquant le deficit de charges reporte)
            res_av_amort = loy["imposable"] - ch["total_deductible"] - deficit_charges

            if res_av_amort < 0:
                # Nouveau deficit de charges
                deficit_charges = abs(res_av_amort)
                amort_deductible = 0.0
                res_fiscal = 0.0
            else:
                deficit_charges = 0.0
                # Amortissements disponibles = calcules cette annee + reportes
                amort_dispo = amort_calc + amort_differe
                # Plafond : ne pas descendre sous zero
                amort_deductible = min(amort_dispo, res_av_amort)
                amort_differe = amort_dispo - amort_deductible
                res_fiscal = res_av_amort - amort_deductible

            ir = res_fiscal * self.p.tmi
            ps = res_fiscal * self.p.taux_ps
            impot_total = ir + ps

            # Cash flow reel
            mensualite_totale = 0.0
            cap_restant = 0.0
            if n <= self.p.duree_pret:
                row_p = self.pret[n - 1]
                mensualite_totale = row_p["capital"] + row_p["interets"] + row_p["assurance"]
                cap_restant = row_p["capital_restant"]

            cf_avant_impot = loy["encaisse"] - mensualite_totale - ch["exploit"]
            cf_net = cf_avant_impot - impot_total

            rows.append({
                "n": n,
                "loyers": loy,
                "charges": ch,
                "amort_calc": amort_calc,
                "amort_deductible": amort_deductible,
                "amort_differe": amort_differe,
                "deficit_charges": deficit_charges,
                "res_fiscal": res_fiscal,
                "ir": ir,
                "ps": ps,
                "impot_total": impot_total,
                "cf_avant_impot": cf_avant_impot,
                "cf_net": cf_net,
                "cap_restant": cap_restant,
            })
        return rows

    def pv_sarl_ir(self) -> Dict:
        """
        Plus-value LMNP IR : calculee sur prix acquisition (amort non reintegres).
        Abattements pour duree de detention (12 ans).
        """
        p = self.p
        net_agence = p.prix_revente * (1 - p.frais_agence_vente)
        pv_brute = net_agence - self.invest_total

        # Abattements (duree = 12 ans)
        annees_abatt = max(0, p.duree_detention - 5)  # Annees ouvrant droit (6e -> 21e)
        abatt_ir_pct = min(annees_abatt * 0.06, 1.0)   # 6 %/an de la 6e a la 21e
        abatt_ps_pct = min(annees_abatt * 0.0165, 1.0) # 1.65 %/an de la 6e a la 21e

        if pv_brute <= 0:
            return {
                "prix_brut": p.prix_revente,
                "frais_agence": p.prix_revente * p.frais_agence_vente,
                "net_agence": net_agence,
                "prix_acquisition": self.invest_total,
                "pv_brute": pv_brute,
                "abatt_ir_pct": 0.0,
                "abatt_ps_pct": 0.0,
                "pv_imposable_ir": 0.0,
                "pv_imposable_ps": 0.0,
                "ir_pv": 0.0,
                "ps_pv": 0.0,
                "surtaxe": 0.0,
                "total_impots_pv": 0.0,
                "net_associes": net_agence,
            }

        pv_imp_ir = pv_brute * (1 - abatt_ir_pct)
        pv_imp_ps = pv_brute * (1 - abatt_ps_pct)

        ir_pv = pv_imp_ir * 0.19        # Taux IR forfaitaire PV immobiliere : 19 %
        ps_pv = pv_imp_ps * p.taux_ps
        surtaxe = calcul_surtaxe_pv(pv_imp_ir)
        total = ir_pv + ps_pv + surtaxe

        return {
            "prix_brut": p.prix_revente,
            "frais_agence": p.prix_revente * p.frais_agence_vente,
            "net_agence": net_agence,
            "prix_acquisition": self.invest_total,
            "pv_brute": pv_brute,
            "abatt_ir_pct": abatt_ir_pct,
            "abatt_ps_pct": abatt_ps_pct,
            "pv_imposable_ir": pv_imp_ir,
            "pv_imposable_ps": pv_imp_ps,
            "ir_pv": ir_pv,
            "ps_pv": ps_pv,
            "surtaxe": surtaxe,
            "total_impots_pv": total,
            "net_associes": net_agence - total,
        }

    # ----------------------------------------------------------
    #  Rapport
    # ----------------------------------------------------------

    def rapport(self):
        p = self.p
        S = "=" * 104
        s = "-" * 104

        def eur(v): return f"{v:>14,.0f} EUR"
        def pct(v): return f"{v*100:>13.2f} %"

        print(S)
        print(f"  BUSINESS PLAN - INVESTISSEMENT IMMOBILIER MEUBLE : {p.nom_bien}")
        print(f"  Duree de detention : {p.duree_detention} ans")
        print(f"  Comparaison : SCI a l'IS  vs  SARL de Famille a l'IR (LMNP BIC reel)")
        print(S)

        # ---------- Parametres ----------
        print("\n[ PARAMETRES DE L'INVESTISSEMENT ]")
        print(s)
        amort_an1 = self.amort_bat + self.amort_trav + self.amort_mob
        print(f"  Prix d'achat :                    {eur(p.prix_achat)}")
        print(f"  Frais de notaire :                {eur(p.frais_notaire)}")
        print(f"  Travaux :                         {eur(p.travaux)}")
        print(f"  Mobilier :                        {eur(p.mobilier)}")
        print(f"  -------------------------------------------------------")
        print(f"  Investissement total :            {eur(self.invest_total)}")
        print(f"  Apport personnel :                {eur(p.apport)}")
        print(f"  Capital emprunte :                {eur(self.capital_emprunte)}")
        print(f"  Taux interet :                    {pct(p.taux_interet)}")
        print(f"  Duree pret :                      {p.duree_pret:>14d} ans")
        m_pret = mensualite_pret(self.capital_emprunte, p.taux_interet, p.duree_pret)
        print(f"  Mensualite (hors assurance) :     {eur(m_pret)}")
        print(f"  Loyer mensuel brut :              {eur(p.loyer_mensuel)}")
        print(f"  Taux de vacance :                 {pct(p.taux_vacance)}")
        print(f"  Amort. batiment (an 1) :          {eur(self.amort_bat)}  ({p.duree_amort_batiment} ans)")
        print(f"  Amort. travaux (an 1) :           {eur(self.amort_trav)}  ({p.duree_amort_travaux} ans)")
        print(f"  Amort. mobilier (an 1) :          {eur(self.amort_mob)}  ({p.duree_amort_mobilier} ans)")
        print(f"  Total amort. annuel (an 1) :      {eur(amort_an1)}")

        # ========================================================
        #  SCI A L'IS
        # ========================================================
        rows_is = self.sim_sci_is()

        print(f"\n\n{'='*104}")
        print("  1. SCI A L'IMPOT SUR LES SOCIETES (IS)")
        print(f"{'='*104}")
        print(f"  IS : {p.taux_is_reduit*100:.0f}% jusqu'a {p.seuil_is_reduit:,.0f} EUR | {p.taux_is_normal*100:.0f}% au-dela")
        print(f"  PFU dividendes : {p.taux_pfu*100:.0f}% (12.8% IR + 17.2% PS)")
        print(f"  Plus-value imposable = prix vente net - VNC (taxee a l'IS, pas d'abattement)")

        hdr = (f"\n  {'An':>3} | {'Loyers imp.':>11} | {'Charges ded.':>12} | "
               f"{'Amort.':>9} | {'Res.fiscal':>10} | {'IS':>8} | "
               f"{'CF av. IS':>10} | {'CF net':>10} | {'VNC':>10}")
        sep_t = (f"  {'':->3}-+-{'':->11}-+-{'':->12}-+-"
                 f"{'':->9}-+-{'':->10}-+-{'':->8}-+-"
                 f"{'':->10}-+-{'':->10}-+-{'':->10}")
        print(hdr)
        print(sep_t)

        tot_is = tot_cf_av_is = tot_cf_net_is = 0.0
        for r in rows_is:
            lo = r["loyers"]["imposable"]
            ch = r["charges"]["total_deductible"]
            am = r["amort"]
            rf = r["res_fiscal"]
            is_ = r["is"]
            cf1 = r["cf_avant_is"]
            cfn = r["cf_net"]
            vnc = r["vnc"]
            tot_is += is_
            tot_cf_av_is += cf1
            tot_cf_net_is += cfn
            dr = f"  (deficit reporte: {r['deficit_reporte']:,.0f})" if r["deficit_reporte"] > 0 else ""
            print(f"  {r['n']:>3} | {lo:>11,.0f} | {ch:>12,.0f} | "
                  f"{am:>9,.0f} | {rf:>10,.0f} | {is_:>8,.0f} | "
                  f"{cf1:>10,.0f} | {cfn:>10,.0f} | {vnc:>10,.0f}{dr}")
        print(sep_t)
        print(f"  {'TOT':>3} | {'':>11} | {'':>12} | "
              f"{'':>9} | {'':>10} | {tot_is:>8,.0f} | "
              f"{tot_cf_av_is:>10,.0f} | {tot_cf_net_is:>10,.0f} |")

        # Plus-value IS
        vnc_fin = rows_is[-1]["vnc"]
        cap_rest_is = rows_is[-1]["cap_restant"]
        pv_is = self.pv_sci_is(vnc_fin)
        treso_sci = pv_is["net_sci"] - cap_rest_is
        pfu = treso_sci * p.taux_pfu
        net_assoc_is = treso_sci - pfu

        print(f"\n  >> CESSION ANNEE {p.duree_detention} - SCI IS")
        print(f"  Prix de vente brut :                    {eur(pv_is['prix_brut'])}")
        print(f"  Frais d'agence ({p.frais_agence_vente*100:.0f}%) :               -{eur(pv_is['frais_agence']).lstrip()}")
        print(f"  Prix de vente net :                     {eur(pv_is['net_agence'])}")
        print(f"  Valeur Nette Comptable (VNC) :          {eur(pv_is['vnc'])}")
        print(f"  Plus-value imposable :                  {eur(pv_is['pv_brute'])}")
        print(f"  IS sur PV ({p.taux_is_reduit*100:.0f}%/{p.taux_is_normal*100:.0f}%) :            -{eur(pv_is['is_pv']).lstrip()}")
        print(f"  Capital pret restant :                  -{eur(cap_rest_is).lstrip()}")
        print(f"  Tresorerie nette SCI :                  {eur(treso_sci)}")
        print(f"  PFU 30% sur dividendes :               -{eur(pfu).lstrip()}")
        print(f"  NET PERCUS PAR LES ASSOCIES :           {eur(net_assoc_is)}")

        # ========================================================
        #  SARL DE FAMILLE A L'IR
        # ========================================================
        rows_ir = self.sim_sarl_ir()

        print(f"\n\n{'='*104}")
        print("  2. SARL DE FAMILLE A L'IR - Regime LMNP BIC Reel")
        print(f"{'='*104}")
        print(f"  TMI : {p.tmi*100:.0f}% | Prelevements sociaux : {p.taux_ps*100:.1f}%")
        print(f"  Taux global IR+PS : {(p.tmi+p.taux_ps)*100:.1f}%")
        print(f"  Plus-value = prix vente - prix acquisition (amort. non reintegres en LMNP)")
        print(f"  Abattement IR : 6%/an de la 6e a la 21e annee | Abattement PS : 1.65%/an")

        hdr2 = (f"\n  {'An':>3} | {'Loyers imp.':>11} | {'Charges ded.':>12} | "
                f"{'Amort.ded.':>10} | {'Res.fiscal':>10} | {'IR+PS':>10} | "
                f"{'CF av.imp.':>10} | {'CF net':>10}")
        sep_t2 = (f"  {'':->3}-+-{'':->11}-+-{'':->12}-+-"
                  f"{'':->10}-+-{'':->10}-+-{'':->10}-+-"
                  f"{'':->10}-+-{'':->10}")
        print(hdr2)
        print(sep_t2)

        tot_irps = tot_cf_av_ir = tot_cf_net_ir = 0.0
        for r in rows_ir:
            lo = r["loyers"]["imposable"]
            ch = r["charges"]["total_deductible"]
            am = r["amort_deductible"]
            rf = r["res_fiscal"]
            ip = r["impot_total"]
            cf1 = r["cf_avant_impot"]
            cfn = r["cf_net"]
            tot_irps += ip
            tot_cf_av_ir += cf1
            tot_cf_net_ir += cfn
            diff = f"  (amort. differe cumul: {r['amort_differe']:,.0f})" if r["amort_differe"] > 0 else ""
            print(f"  {r['n']:>3} | {lo:>11,.0f} | {ch:>12,.0f} | "
                  f"{am:>10,.0f} | {rf:>10,.0f} | {ip:>10,.0f} | "
                  f"{cf1:>10,.0f} | {cfn:>10,.0f}{diff}")
        print(sep_t2)
        print(f"  {'TOT':>3} | {'':>11} | {'':>12} | "
              f"{'':>10} | {'':>10} | {tot_irps:>10,.0f} | "
              f"{tot_cf_av_ir:>10,.0f} | {tot_cf_net_ir:>10,.0f}")

        # Plus-value IR
        cap_rest_ir = rows_ir[-1]["cap_restant"]
        pv_ir = self.pv_sarl_ir()
        net_assoc_ir = pv_ir["net_associes"] - cap_rest_ir

        print(f"\n  >> CESSION ANNEE {p.duree_detention} - SARL IR (LMNP)")
        print(f"  Prix de vente brut :                    {eur(pv_ir['prix_brut'])}")
        print(f"  Frais d'agence ({p.frais_agence_vente*100:.0f}%) :               -{eur(pv_ir['frais_agence']).lstrip()}")
        print(f"  Prix de vente net :                     {eur(pv_ir['net_agence'])}")
        print(f"  Prix d'acquisition :                   -{eur(pv_ir['prix_acquisition']).lstrip()}")
        print(f"  Plus-value brute :                      {eur(pv_ir['pv_brute'])}")
        print(f"  Abattement IR ({pv_ir['abatt_ir_pct']*100:.0f}%) :               -{eur(pv_ir['pv_brute']*pv_ir['abatt_ir_pct']).lstrip()}")
        print(f"  PV imposable IR :                       {eur(pv_ir['pv_imposable_ir'])}")
        print(f"  IR forfaitaire (19%) :                 -{eur(pv_ir['ir_pv']).lstrip()}")
        print(f"  Abattement PS ({pv_ir['abatt_ps_pct']*100:.2f}%) :           -{eur(pv_ir['pv_brute']*pv_ir['abatt_ps_pct']).lstrip()}")
        print(f"  PV imposable PS :                       {eur(pv_ir['pv_imposable_ps'])}")
        print(f"  Prelevements sociaux (17.2%) :         -{eur(pv_ir['ps_pv']).lstrip()}")
        if pv_ir["surtaxe"] > 0:
            print(f"  Surtaxe PV elevee :                    -{eur(pv_ir['surtaxe']).lstrip()}")
        print(f"  Total impots cession :                 -{eur(pv_ir['total_impots_pv']).lstrip()}")
        print(f"  Capital pret restant :                 -{eur(cap_rest_ir).lstrip()}")
        print(f"  NET PERCUS PAR LES ASSOCIES :           {eur(net_assoc_ir)}")

        # ========================================================
        #  SYNTHESE COMPARATIVE
        # ========================================================
        print(f"\n\n{'='*104}")
        print("  SYNTHESE COMPARATIVE")
        print(f"{'='*104}")

        # TRI
        flux_is = [-p.apport] + [r["cf_net"] for r in rows_is]
        flux_is[-1] += net_assoc_is

        flux_ir = [-p.apport] + [r["cf_net"] for r in rows_ir]
        flux_ir[-1] += net_assoc_ir

        tri_is = calculer_tri(flux_is)
        tri_ir = calculer_tri(flux_ir)

        # Rendements an 1
        loy1 = self.loyers_annee(1)
        ch1 = self.charges_annee(1)
        rdt_brut = (p.loyer_mensuel * 12) / self.invest_total
        rdt_net = (loy1["encaisse"] - ch1["exploit"]) / self.invest_total

        lbl = "{:<47}"
        col = "{:>22}"

        print(f"\n  {lbl.format('Indicateur')} | {col.format('SCI a l IS')} | {col.format('SARL Famille IR')}")
        print(f"  {'-'*47}-+-{'-'*22}-+-{'-'*22}")

        def ligne(label, v1, v2):
            print(f"  {lbl.format(label)} | {col.format(v1)} | {col.format(v2)}")

        def sep_ligne():
            print(f"  {'-'*47}-+-{'-'*22}-+-{'-'*22}")

        def e(v): return f"{v:,.0f} EUR"
        def p_(v): return f"{v*100:.2f} %"

        ligne("Investissement total", e(self.invest_total), e(self.invest_total))
        ligne("Capital emprunte", e(self.capital_emprunte), e(self.capital_emprunte))
        ligne("Rendement brut (loyers / invest, an 1)", p_(rdt_brut), p_(rdt_brut))
        ligne("Rendement net charges (an 1)", p_(rdt_net), p_(rdt_net))
        sep_ligne()
        ligne("Total impots exploitation (12 ans)", e(tot_is), e(tot_irps))
        ligne("Cash flow cumule avant impots", e(tot_cf_av_is), e(tot_cf_av_ir))
        ligne("Cash flow net cumule (exploitation)", e(tot_cf_net_is), e(tot_cf_net_ir))
        sep_ligne()
        ligne("Prix de revente brut", e(p.prix_revente), e(p.prix_revente))
        ligne("Plus-value brute", e(pv_is["pv_brute"]), e(pv_ir["pv_brute"]))
        ligne("Impots sur plus-value", e(pv_is["is_pv"]), e(pv_ir["total_impots_pv"]))
        sep_ligne()
        ligne("Capital pret restant (an 12)", e(cap_rest_is), e(cap_rest_ir))
        ligne("Net associes apres cession (avant PFU)", e(treso_sci), "N/A (transparent)")
        ligne("Net associes apres cession et PFU", e(net_assoc_is), e(net_assoc_ir))
        sep_ligne()
        tri_is_str = p_(tri_is) if tri_is is not None else "N/A (invest. deficitaire)"
        tri_ir_str = p_(tri_ir) if tri_ir is not None else "N/A (invest. deficitaire)"
        ligne(f"TRI net sur apport ({e(p.apport)})", tri_is_str, tri_ir_str)
        sep_ligne()
        # Bilan global (flux non actualises)
        gain_is = sum(flux_is)
        gain_ir = sum(flux_ir)
        ligne("Gain/perte net global (non actualise)", e(gain_is), e(gain_ir))

        # ========================================================
        #  POINTS CLES
        # ========================================================
        print(f"\n\n{'='*104}")
        print("  ANALYSE : POINTS CLES DE LA COMPARAISON")
        print(f"{'='*104}")

        print(f"""
  SCI A L'IS
  ----------
  + Taux IS reduit (15%) attractif si resultat fiscal < {p.seuil_is_reduit:,.0f} EUR
  + Amortissements integralement deductibles -> resultat fiscal souvent nul ou faible
  + Souplesse pour distribuer ou capitaliser les resultats dans la societe
  - Double imposition : IS sur les benefices + PFU 30% lors de la distribution
  - PIEGES CESSION : PV = prix vente - VNC (reduite par amortissements)
    => Assiette imposable tres elevee au bout de 12 ans (VNC = {rows_is[-1]['vnc']:,.0f} EUR)
  - Pas d'abattement pour duree de detention sur la PV (regime des PV professionnelles)
  - IS effectif sur PV : {pv_is['is_pv']:,.0f} EUR ({pv_is['is_pv']/pv_is['pv_brute']*100:.1f}% de la PV brute)

  SARL DE FAMILLE A L'IR (LMNP BIC Reel)
  ----------------------------------------
  + Amortissements deductibles (limites a zero, reportables illimites)
  + Deficit de charges reportable 10 ans sur BIC meublé non professionnel
  + PV FAVORABLE : calculee sur prix acquisition initial ({e(self.invest_total)})
    => Amortissements NON reintegres en LMNP (avantage majeur vs LMP ou IS)
  + Abattements pour duree de detention :
    IR : {pv_ir['abatt_ir_pct']*100:.0f}% d'abattement ({p.duree_detention} ans)  |  PS : {pv_ir['abatt_ps_pct']*100:.2f}% d'abattement
  + Taux forfaitaire PV IR : 19% (+ PS 17.2%) avant abattements
  + Impots cession : {pv_ir['total_impots_pv']:,.0f} EUR ({pv_ir['total_impots_pv']/pv_ir['pv_brute']*100:.1f}% de la PV brute) -> nettement inferieur a l'IS
  - IR + PS sur revenus locatifs au taux marginal ({(p.tmi + p.taux_ps)*100:.1f}%) si resultat positif
  - Risque requalification LMP si revenus > 23 000 EUR ET > 50% revenus foyer

  CONCLUSION
  ----------
  Pour une detention de {p.duree_detention} ans avec cession finale, la SARL de famille a l'IR
  est generalement PLUS AVANTAGEUSE sur le plan fiscal grace a la plus-value
  calculee sur le prix d'acquisition (non reduite par les amortissements).
  En SCI IS, les amortissements crees une bombe fiscale a la revente.
  La SCI IS peut etre interessante sur une duree tres longue sans intention
  de vendre, ou dans une logique de transmission patrimoniale.

  AVERTISSEMENT : Ce business plan est fourni a titre indicatif (donnees 2024).
  La fiscalite immobiliere est complexe et peut evoluer. Consultez un
  expert-comptable et/ou un conseiller en gestion de patrimoine avant
  toute decision d'investissement.
""")


# ============================================================
#  POINT D'ENTREE - Modifiez les parametres ici
# ============================================================

def main():
    params = Parametres(
        nom_bien="Appartement T2 meuble - Centre-ville",

        # --- Acquisition ---
        prix_achat=200_000,       # EUR
        part_terrain=0.20,        # 20% non amortissable
        frais_notaire=16_000,     # EUR (~8%)
        travaux=20_000,           # EUR
        mobilier=10_000,          # EUR

        # --- Financement ---
        apport=50_000,            # EUR
        taux_interet=0.035,       # 3.5%
        duree_pret=20,            # ans
        taux_assurance_pret=0.003, # 0.3% sur capital initial

        # --- Revenus ---
        loyer_mensuel=1_200,      # EUR/mois
        charges_recup_mensuelles=100,
        taux_vacance=0.05,        # 5%
        revalorisation_loyer=0.02, # 2%/an

        # --- Charges ---
        taxe_fonciere=1_500,
        charges_copro=1_200,
        assurance_pno=400,
        taux_gestion=0.08,        # 8% loyers encaisses
        entretien=500,
        honoraires_comptables=1_500,
        revalorisation_charges=0.02,

        # --- Amortissements ---
        duree_amort_batiment=30,
        duree_amort_travaux=15,
        duree_amort_mobilier=7,

        # --- Fiscalite IR ---
        tmi=0.30,                 # 30%
        taux_ps=0.172,            # 17.2%

        # --- Fiscalite IS ---
        taux_is_reduit=0.15,
        seuil_is_reduit=42_500,
        taux_is_normal=0.25,
        taux_pfu=0.30,

        # --- Revente ---
        duree_detention=12,
        prix_revente=260_000,
        frais_agence_vente=0.05,
    )

    sim = Simulation(params)
    sim.rapport()


if __name__ == "__main__":
    main()
