from kivy.config import Config
# Configuration plein écran
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'window_state', 'maximized')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.utils import get_color_from_hex
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.animation import Animation
from kivy.uix.popup import Popup
import random
import os
import json
import re

# --- CONFIGURATION ---
C_BLANC = '#FFFFFF'
C_NOIR = '#000000'
C_ROUGE = '#D32F2F'

BAR_COLORS = {
   "ARGENT": '#2C3E50', "SANTE": '#27AE60', "ARMEE": '#34495E', "EDUCATION": '#2980B9',
   "CORRUPTION": '#F39C12', "LIBERTE": '#8E44AD', "BONHEUR": '#E91E63', "ENTREPRISE": '#16A085'
}

# --- COMPOSANTS ---
class CristalBar(ProgressBar):
    def __init__(self, color_hex, **kwargs):
        super().__init__(**kwargs)
        self.color_hex = get_color_from_hex(color_hex)
        with self.canvas.before:
            Color(0.92, 0.92, 0.92, 1)
            self.bg = RoundedRectangle(radius=[3,])
        with self.canvas.after:
            Color(*self.color_hex)
            self.fill = RoundedRectangle(radius=[3,])
        self.bind(pos=self.update_rect, size=self.update_rect, value=self.update_rect)

    def update_rect(self, *args):
        self.bg.pos, self.bg.size = self.pos, self.size
        w = (self.value / 100.0) * self.width if self.width > 0 else 0
        Animation(size=(w, self.height), duration=0.4, t='out_quad').start(self.fill)
        self.fill.pos = self.pos

class ProButton(Button):
    def __init__(self, bg_color_hex=C_NOIR, txt_color=(1,1,1,1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0,0,0,0)
        self.bold = True
        self.size_hint_y = None
        self.height = '60dp'
        self.color = txt_color
        with self.canvas.before:
            self.c_obj = Color(*get_color_from_hex(bg_color_hex))
            self.rect = RoundedRectangle(radius=[10,])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos, self.rect.size = self.pos, self.size

# --- ÉCRANS ---
class EcranAccueil(Screen):
    def on_enter(self):
        self.clear_widgets()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg)

        l = BoxLayout(orientation='vertical', padding=50, spacing=10)
        l.add_widget(Label(text="PRÉSIDENCE", font_size='50sp', bold=True, color=(0,0,0,1)))
        l.add_widget(Label(text="LE CHOIX D'UNE NATION", font_size='22sp', color=(0,0,0,1)))
        l.add_widget(Label(text="Simulation politique v0.2", font_size='14sp', color=(0.4,0.4,0.4,1)))
        
        btn_box = BoxLayout(orientation='vertical', spacing=15, size_hint_y=0.4)
        app = App.get_running_app()
        if app.partie_existe():
            btn_c = ProButton(text="CONTINUER LE MANDAT", bg_color_hex="#2C3E50")
            btn_c.bind(on_release=lambda x: setattr(self.manager, 'current', 'jeu'))
            btn_box.add_widget(btn_c)

        btn_n = ProButton(text="NOUVELLE ÉLECTION", bg_color_hex=C_NOIR)
        btn_n.bind(on_release=self.lancer_nouveau)
        btn_box.add_widget(btn_n)
        l.add_widget(btn_box); self.add_widget(l)

    def _update_bg(self, *args): self.bg_rect.size = self.size; self.bg_rect.pos = self.pos
    def lancer_nouveau(self, *args):
        App.get_running_app().reinit()
        self.manager.current = 'tuto' if App.get_running_app().doit_voir_tuto() else 'jeu'

class EcranTuto(Screen):
    def on_enter(self):
        self.clear_widgets()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg)
        self.step = 0
        self.tips = [
            {"t": "VOTRE POUVOIR", "c": "Gérez les 8 piliers de la nation. Si l'un atteint 0% ou 100%, le mandat s'arrête."},
            {"t": "DIFFICULTÉ", "c": "Plus vous régnez, plus les malus de vos choix augmentent. Soyez vigilant."},
            {"t": "DIALOGUES", "c": "Chaque action déclenche un rapport. Lisez-les pour voir votre impact sur le monde."},
            {"t": "SAUVEGARDE", "c": "Le jeu enregistre votre progression automatiquement après chaque décision."}
        ]
        self.l = BoxLayout(orientation='vertical', padding=60, spacing=30)
        self.lbl_t = Label(text="", font_size='30sp', bold=True, color=(0,0,0,1))
        self.lbl_c = Label(text="", halign='center', color=(0.1,0.1,0.1,1), font_size='18sp')
        self.lbl_c.bind(size=lambda s,v: setattr(s, 'text_size', (s.width*0.8, None)))
        self.btn = ProButton(text="SUIVANT", bg_color_hex=C_NOIR)
        self.btn.bind(on_release=self.next_step)
        self.l.add_widget(self.lbl_t); self.l.add_widget(self.lbl_c); self.l.add_widget(self.btn)
        self.add_widget(self.l); self.update_tuto()

    def update_tuto(self):
        self.lbl_t.text = self.tips[self.step]["t"]; self.lbl_c.text = self.tips[self.step]["c"]
    def _update_bg(self, *args): self.bg_rect.size = self.size; self.bg_rect.pos = self.pos
    def next_step(self, *args):
        self.step += 1
        if self.step < len(self.tips): self.update_tuto()
        else: App.get_running_app().marquer_tuto_vu(); self.manager.current = 'jeu'

class EcranJeu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.en_feedback = False
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg)

        self.main = BoxLayout(orientation='vertical', padding=25, spacing=15)
        
        # HUD: Mois à gauche, Gouvernement à droite
        hud = BoxLayout(size_hint_y=0.08)
        self.lbl_mois = Label(text="", color=(0,0,0,1), bold=True, halign='left')
        self.lbl_gouv = Label(text="", color=(0,0,0,1), bold=True, halign='right')
        hud.add_widget(self.lbl_mois); hud.add_widget(self.lbl_gouv)
        self.main.add_widget(hud)

        self.grid = GridLayout(cols=2, spacing=15, size_hint_y=0.35)
        self.bars, self.val_labels = {}, {}
        for s, color in BAR_COLORS.items():
            box = BoxLayout(orientation='vertical', spacing=2)
            l_box = BoxLayout(size_hint_y=None, height='18dp')
            l_box.add_widget(Label(text=s, font_size='11sp', color=(0.4,0.4,0.4,1)))
            v_l = Label(text="50%", font_size='11sp', color=get_color_from_hex(color), bold=True)
            l_box.add_widget(v_l)
            pb = CristalBar(color_hex=color, size_hint_y=None, height='8dp')
            box.add_widget(l_box); box.add_widget(pb)
            self.grid.add_widget(box); self.bars[s] = pb; self.val_labels[s] = v_l
        self.main.add_widget(self.grid)

        self.lbl_msg = Label(text="", halign='center', markup=True, color=(0,0,0,1), font_size='18sp')
        self.lbl_msg.bind(size=lambda s,v: setattr(s, 'text_size', (s.width*0.9, None)))
        self.main.add_widget(self.lbl_msg)

        self.btn_a = ProButton(text="", bg_color_hex="#27AE60")
        self.btn_b = ProButton(text="", bg_color_hex="#C0392B")
        self.btn_a.bind(on_release=lambda x: self.appliquer("A"))
        self.btn_b.bind(on_release=lambda x: self.appliquer("B"))
        self.main.add_widget(self.btn_a); self.main.add_widget(self.btn_b); self.add_widget(self.main)

    def _update_bg(self, *args): self.bg_rect.size = self.size; self.bg_rect.pos = self.pos
    def on_enter(self): 
        App.get_running_app().charger_partie()
        self.nouveau_tour()

    def nouveau_tour(self):
        app = App.get_running_app()
        self.en_feedback = False
        self.btn_b.opacity = 1; self.btn_b.disabled = False
        self.lbl_mois.text = f"MOIS: {app.mois}"
        self.lbl_gouv.text = f"GOUVERNEMENT: {int(app.stats['GOUVERNEMENT'])}%"
        
        for k, v in app.stats.items():
            if k in self.bars:
                self.bars[k].value = v
                self.val_labels[k].text = f"{int(v)}%"
                if (v <= 0 or v >= 100) and app.mois > 0:
                    app.raison_fin = f"L'effondrement de {k} a causé votre chute."
                    app.supprimer_partie()
                    self.manager.current = 'fin'; return

        self.ev = random.choice(app.events)
        self.lbl_msg.text = f"[b]{self.ev['min']}[/b]\n\n{self.ev['arg']}"
        self.btn_a.text = self.ev['A']['t']; self.btn_b.text = self.ev['B']['t']

    def appliquer(self, choix):
        app = App.get_running_app()
        if not self.en_feedback:
            res = self.ev[choix]
            # DIFFICULTÉ PROGRESSIVE INTELLIGENTE
            diff_factor = 1 + (app.mois / 20)
            for k, v in res['i'].items():
                key = k.replace('É', 'E').strip()
                if key in app.stats:
                    val = v * diff_factor if v < 0 else v
                    app.stats[key] = max(0, min(100, app.stats[key] + val))
            
            self.lbl_msg.text = f"[i]{res['dialogue']}[/i]"
            self.btn_a.text = "CONTINUER LE RÈGNE"; self.btn_b.opacity = 0; self.btn_b.disabled = True
            self.en_feedback = True; app.mois += 1; app.sauvegarder_partie()
        else:
            self.nouveau_tour()

class EcranFin(Screen):
    def on_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        with self.canvas.before:
            Color(*get_color_from_hex(C_ROUGE))
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg)
        
        l = BoxLayout(orientation='vertical', padding=50, spacing=20)
        l.add_widget(Label(text="FIN DU RÈGNE", font_size='40sp', bold=True))
        
        # SYSTEME DE TITRES
        titre = "LE SURVIVANT"
        if app.stats['ARMEE'] > 80: titre = "LE DICTATEUR D'ACIER"
        elif app.stats['BONHEUR'] > 80: titre = "LE PÈRE DU PEUPLE"
        elif app.stats['CORRUPTION'] > 70: titre = "LE TYRAN CORROMPU"
        elif app.stats['LIBERTE'] > 80: titre = "L'IDÉALISTE"
        
        l.add_widget(Label(text=f"TITRE ACQUIS : {titre}", font_size='22sp', bold=True))
        l.add_widget(Label(text=f"Vous avez régné {app.mois} mois"))
        l.add_widget(Label(text=app.raison_fin, halign='center', italic=True))
        
        btn_c = ProButton(text="VOIR LES CRÉDITS", bg_color_hex="#000000")
        btn_c.bind(on_release=self.show_credits)
        l.add_widget(btn_c)
        
        btn_r = ProButton(text="NOUVELLE TENTATIVE", bg_color_hex=C_BLANC, txt_color=(0,0,0,1))
        btn_r.bind(on_release=lambda x: app.reinit() or setattr(self.manager, 'current', 'jeu'))
        l.add_widget(btn_r); self.add_widget(l)

    def _update_bg(self, *args): self.bg_rect.size = self.size; self.bg_rect.pos = self.pos
    def show_credits(self, *args):
        content = Label(text="CRÉDITS :\n\nSCORE MILLE HÉROS • NICODÈME\nDARUIS S'EN FOUT • MR DE SOUZA\nÉSAÏE L'ORIGINAL", halign='center')
        p = Popup(title="Remerciements", content=content, size_hint=(0.8, 0.4)); p.open()

class PresidentApp(App):
    def build(self):
        self.save_f, self.tuto_f = "sauvegarde.json", "tuto_ok.txt"
        self.reinit()
        self.charger_evenements()
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(EcranAccueil(name='accueil'))
        sm.add_widget(EcranTuto(name='tuto'))
        sm.add_widget(EcranJeu(name='jeu'))
        sm.add_widget(EcranFin(name='fin'))
        return sm

    def reinit(self):
        self.stats = {k: 50 for k in BAR_COLORS}; self.stats["GOUVERNEMENT"] = 50
        self.mois = 0; self.raison_fin = ""

    def charger_evenements(self):
        # TES ÉVÉNEMENTS ORIGINAUX CORRIGÉS (Orthographe/Grammaire respectée)
        raw = [
            {"min": "LE MINISTRE DE LA SANTÉ", "arg": "Le peuple demande l'augmentation du budget du ministère de la Santé afin de rendre les médicaments gratuits pour les enfants.", "A": {"t": "AUGMENTER (+SAN / -ARG)", "i": {"SANTE": 25, "ARGENT": -35}, "d": "Le peuple vous acclame, la santé s'améliore."}, "B": {"t": "MAINTENIR (-SAN / +ARG)", "i": {"SANTE": -30, "ARGENT": 15}, "d": "Les finances sont stables, mais les familles souffrent."}},
            {"min": "LE MINISTRE DE L'ÉDUCATION", "arg": "Nos écoles sont devenues vieilles. Il faut une rénovation immédiate, le futur de nos enfants est menacé.", "A": {"t": "RÉNOVER (+EDU / -ARM)", "i": {"EDUCATION": 35, "ARMEE": -35}, "d": "Les écoles brillent, mais les généraux grognent."}, "B": {"t": "REFUSER (-EDU)", "i": {"EDUCATION": -25}, "d": "Le budget est préservé, l'éducation recule."}},
            {"min": "UN HAUT DIGNITAIRE", "arg": "Le PDG de COPROM vous propose un soutien financier secret si nous réduisons certaines taxes sur ses entreprises.", "A": {"t": "ACCEPTER (+COR / +ENT)", "i": {"CORRUPTION": 45, "ENTREPRISE": 25}, "d": "Les entreprises prospèrent dans l'ombre."}, "B": {"t": "DÉNONCER (-COR / -ENT)", "i": {"CORRUPTION": -20, "ENTREPRISE": -15}, "d": "Votre intégrité renforce la nation."}},
            {"min": "LE MINISTRE DE LA JUSTICE", "arg": "Nos forces de l'ordre affirment avoir besoin de l'autorisation d'utiliser tous les moyens en leur possession.", "A": {"t": "AUTORISER (+ARM / -LIB)", "i": {"ARMEE": 30, "LIBERTE": -55}, "d": "L'ordre règne, la liberté s'éteint."}, "B": {"t": "INTERDIRE (+LIB / -ARM)", "i": {"LIBERTE": 20, "ARMEE": -20}, "d": "La liberté est sauve, mais l'insécurité monte."}},
            {"min": "LE CHEF D'ÉTAT-MAJOR", "arg": "Mes hommes demandent des surveillances numériques massives pour prévenir les futures menaces terroristes.", "A": {"t": "SURVEILLER (+ARM / -LIB)", "i": {"ARMEE": 25, "LIBERTE": -35}, "d": "Sécurité totale, vie privée sous contrôle."}, "B": {"t": "PROTÉGER LA VIE (+LIB / -ARM)", "i": {"LIBERTE": 20, "ARMEE": -25}, "d": "Le peuple respire sans espionnage."}},
            {"min": "LE MINISTRE DE L'ÉCONOMIE", "arg": "Le pays est en crise. Je pense qu'il faut nationaliser les entreprises privées pour sauver les caisses publiques.", "A": {"t": "NATIONALISER (+ARG / -ENT)", "i": {"ARGENT": 35, "ENTREPRISE": -35}, "d": "L'État s'enrichit, l'investissement privé meurt."}, "B": {"t": "LAISSER LE PRIVÉ (+ENT / -ARG)", "i": {"ENTREPRISE": 25, "ARGENT": -15}, "d": "Le marché est libre et dynamique."}},
            {"min": "LE CONSEILLER SOCIAL", "arg": "Les syndicats affirment que la semaine de 4 jours est nécessaire pour le bien-être des familles.", "A": {"t": "ACCEPTER (+BON / -ARG)", "i": {"BONHEUR": 35, "ARGENT": -35}, "d": "Le bonheur explose, l'économie ralentit."}, "B": {"t": "REFUSER (-BON / +ENT)", "i": {"BONHEUR": -25, "ENTREPRISE": 15}, "d": "Productivité maximale, fatigue sociale."}},
            {"min": "LE MINISTRE DE L'INFRASTRUCTURE", "arg": "Propose de construire un pont géant prestigieux. Cela aiderait les entreprises à transporter leurs marchandises.", "A": {"t": "CONSTRUIRE (+ENT / -ARG)", "i": {"ENTREPRISE": 25, "ARGENT": -35}, "d": "Le commerce s'accélère via cet ouvrage."}, "B": {"t": "ANNULER (+ARG)", "i": {"ARGENT": 15}, "d": "Économie budgétaire réussie."}},
            {"min": "LE MINISTRE DE L'AGRICULTURE", "arg": "L'usage de pesticides puissants permettra de doubler nos récoltes cette année.", "A": {"t": "AUTORISER (+ARG / -SAN)", "i": {"ARGENT": 30, "SANTE": -40}, "d": "Abondance alimentaire, mais crise sanitaire."}, "B": {"t": "INTERDIRE (+SAN / -ARG)", "i": {"SANTE": 25, "ARGENT": -20}, "d": "Nature protégée, récoltes limitées."}},
            {"min": "LE MINISTRE DE L'ÉNERGIE", "arg": "Le pays manque d'énergie. Il faut qu'on passe au nucléaire, qui est la seule issue viable malgré la peur.", "A": {"t": "NUCLÉAIRE (+ARG / -BON)", "i": {"ARGENT": 35, "BONHEUR": -30}, "d": "Énergie garantie, peuple inquiet."}, "B": {"t": "SOLAIRE (+SAN / -ARG)", "i": {"SANTE": 20, "ARGENT": -25}, "d": "Énergie verte, coût très élevé."}},
            {"min": "LE PRÉFET DE POLICE", "arg": "Des gangs contrôlent les ports. Il affirme qu'envoyer l'armée pour les déloger est la seule solution.", "A": {"t": "LES ENVOYER (+ARM / -BON)", "i": {"ARMEE": 25, "BONHEUR": -20}, "d": "Ports libérés, mais le sang a coulé."}, "B": {"t": "NÉGOCIER (+COR / -ARG)", "i": {"CORRUPTION": 35, "ARGENT": -25}, "d": "La paix est achetée au prix de l'honneur."}},
            {"min": "LE MINISTRE DU NUMÉRIQUE", "arg": "Taxer les géants du web nous permettrait de financer nos hôpitaux.", "A": {"t": "TAXER (+SAN / +ARG / -ENT)", "i": {"SANTE": 25, "ARGENT": 25, "ENTREPRISE": -35}, "d": "Les hôpitaux respirent grâce au web."}, "B": {"t": "REFUSER (+ENT)", "i": {"ENTREPRISE": 20}, "d": "Paradis fiscal tech maintenu."}},
            {"min": "LE MINISTRE DES AFFAIRES ÉTRANGÈRES", "arg": "Nos voisins menacent de droits de douane si vous refusez d'expulser leurs opposants réfugiés.", "A": {"t": "EXPULSER (+ENT / -BON)", "i": {"ENTREPRISE": 20, "BONHEUR": -40}, "d": "Économie sauvée, humanité trahie."}, "B": {"t": "PROTÉGER (+BON / -ARG)", "i": {"BONHEUR": 35, "ARGENT": -25}, "d": "Terre d'asile fière mais taxée."}},
            {"min": "LA SÉCURITÉ NATIONALE", "arg": "Des dossiers compromettants ont été saisis. Faut-il les déclassifier ou les étouffer ?", "A": {"t": "DÉCLASSIFIER (+BON / +COR)", "i": {"BONHEUR": 35, "CORRUPTION": 40}, "d": "Vérité éclatante, chaos politique."}, "B": {"t": "ÉTOUFFER (+COR / +ARG)", "i": {"CORRUPTION": 35, "ARGENT": 20}, "d": "Le secret d'État est préservé."}},
            {"min": "LE DIRECTEUR DE LA POLICE", "arg": "Mes agents disent qu'ils ne peuvent plus travailler sans une prime de risque importante.", "A": {"t": "PAYER (+ARM / -ARG)", "i": {"ARMEE": 20, "ARGENT": -30}, "d": "Police fidèle et motivée."}, "B": {"t": "REFUSER (-ARM / +ARG)", "i": {"ARMEE": -25, "ARGENT": 20}, "d": "Grogne dans les commissariats."}},
            {"min": "LE JOURNALISTE", "arg": "Allez-vous enfin réduire les impôts des plus pauvres pour calmer la colère sociale ?", "A": {"t": "OUI (+BON / -ARG)", "i": {"BONHEUR": 30, "ARGENT": -30}, "d": "Popularité record dans les faubourgs."}, "B": {"t": "NON (-BON / +ARG)", "i": {"BONHEUR": -30, "ARGENT": 25}, "d": "Rigueur budgétaire impopulaire."}},
            {"min": "L'AMBASSADEUR VOISIN", "arg": "Notre nation est stable. Venez investir chez nous pour fructifier vos richesses.", "A": {"t": "INVESTIR (+BON / +ARG / +ENT)", "i": {"BONHEUR": 20, "ARGENT": 20, "ENTREPRISE": 20}, "d": "Alliance économique forte."}, "B": {"t": "DÉCLINER (-ARG / -ENT / +LIB)", "i": {"ARGENT": -15, "ENTREPRISE": -15, "LIBERTE": 10}, "d": "Souveraineté totale préservée."}},
            {"min": "LE PRÉSIDENT DU PARLEMENT", "arg": "Nos députés gaspillent l'argent. Je propose de dissoudre le Parlement.", "A": {"t": "DISSOUDRE (+BON / +ARG / -COR)", "i": {"BONHEUR": 15, "ARGENT": 20, "CORRUPTION": -15}, "d": "Grand nettoyage politique."}, "B": {"t": "IGNORER (-BON / -ARG / +COR)", "i": {"BONHEUR": -15, "ARGENT": -25, "CORRUPTION": 25}, "d": "Le statu quo continue."}},
            {"min": "UN DÉPUTÉ D'OPPOSITION", "arg": "Vous a accusé de traître à la nation lors de son passage à la télé. Que faites-vous ?", "A": {"t": "CONDAMNER (-BON / +ARM / -LIB)", "i": {"BONHEUR": -15, "ARMEE": 20, "LIBERTE": -15}, "d": "L'autorité est rétablie par la force."}, "B": {"t": "LE RENCONTRER (+BON / +LIB)", "i": {"BONHEUR": 15, "LIBERTE": 25}, "d": "Le dialogue apaise la nation."}},
            {"min": "LE PRÉSIDENT DU SUD", "arg": "Propose une alliance militaire stratégique et la création de bases sur votre sol.", "A": {"t": "ACCEPTER (+BON / -ARG / +ARM)", "i": {"BONHEUR": 10, "ARGENT": -20, "ARMEE": 20}, "d": "Protection régionale assurée."}, "B": {"t": "REFUSEZ (-BON / +ARG / +ARM)", "i": {"BONHEUR": -5, "ARGENT": 1, "ARMEE": 10}, "d": "Neutralité armée maintenue."}},
            {"min": "LE RENSEIGNEMENT", "arg": "Nos Citoyens sont détenus illégalements au Sud. Le président exige une caution de 100 millions.", "A": {"t": "PAYER (+BON / -ARM / -ARG)", "i": {"BONHEUR": 25, "ARGENT": -30, "ARMEE": -10}, "d": "Héros libérés, budget vide."}, "B": {"t": "NÉGOCIER (-BON / +ARM / +ARG)", "i":{"BONHEUR": -20, "ARGENT": 10, "ARMEE": 10}, "d": "Fermeté diplomatique risquée."}},
            {"min":"LE JUGE", "arg": "Votre ministre des sports a détourné beaucoup d'argent. Que prévoyez-vous ?", "A":{"t": "LE VIRER (+ARG / +BON / -COR)", "i":{"BONHEUR": 10, "ARGENT": 15, "LIBERTE": -15, "CORRUPTION": -15}, "d": "La loi s'applique à tous."}, "B":{"t": "CAMOUFLER (-BON / -ARG / +COR)", "i" : {"BONHEUR": -10, "ARGENT": -10, "LIBERTE": 5, "CORRUPTION": 10}, "d": "Secret d'État protégé."}},
            {"min": "LE MAIRE", "arg": " Un grand nombre de personnes sont arrivés dans la capitale ce qui a fait augmenter la population et le nombre de gang. La criminalité a augmenter.", "A":{"t": "POLICE (+ARM / -LIB / -ARG)", "i":{"ARMEE": 10, "LIBERTE": -20, "ARGENT": -15}, "d": "L'ordre revient dans la rue."}, "B":{"t": "IGNORER (+ARG / -BON / -ARM)", "i":{"ARGENT": 25, "BONHEUR": -20, "ARMEE": -15, "SANTE": 15}, "d": "La ville s'adapte lentement."}},
            {"min":"LE PRÉSIDENT DE LA FIFA", "arg": "Votre nation a été sélectionnée pour accueillir le mondial de football.", "A":{"t": "ACCEPTER (+BON / -ARG / +ENT)", "i":{"BONHEUR": 20, "ARGENT": -15 ,"ENTREPRISE": 15}, "d": "Fête nationale inoubliable."}, "B":{"t": "REFUSER (-BON / +ARG)", "i":{"BONHEUR": -15, "ARGENT": 10}, "d": "Économie budgétaire stricte."}},
            {"min": "SERVICES SECRETS", "arg": " nous avons lors de nos opérations capturés des Espions du Nord. Ils ont tout avoué. Que proposez-vous ?", "A":{"t": "LES ENFERMER (-BON / -LIB)", "i":{"BONHEUR": -5, "LIBERTE": -10}, "d": "Ils ne parleront plus."}, "B":{"t": "CAUTION (+ARG / +COR)", "i":{ "ARGENT": 15, "CORRUPTION": 15}, "d": "Profit secret réalisé."}},
            {"min":"LES ENSEIGNANTS", "arg": " Nous proposons de la philosophie par la programmation cela sera bénéfique à notre nation.", "A":{"t": "MODERNISER (-ARG / +EDU)", "i":{"BONHEUR": -10, "ARGENT": -18, "EDUCATION": 20}, "d": "Nation tournée vers l'IA."}, "B":{"t": "RIEN CHANGER (-EDU)", "i":{"ARGENT": 0, "EDUCATION": -20, "SANTE": -5}, "d": "Traditions préservées."}},
            {"min": "LES MÉDECINS", "arg": "Nos hôpitaux sont pleins. Nous exigeons une augmentation et du matériel.", "A":{"t": "ACCEPTER (+BON / +SAN / -ARG)", "i":{"BONHEUR": 15, "SANTE": 20, "ENTREPRISE": 10, "ARGENT": -30}, "d": "Hôpitaux de classe mondiale."}, "B":{"t": "REFUSER (-SAN / -BON)", "i":{"BONHEUR": -15, "SANTE": -25, "ARGENT": 0}, "d": "Grève dans les hôpitaux."}},
            {"min": "L'OPPOSITION", "arg": " je vous présente mes excuses officielles et vous Demande la libération des détenus politiques détenus à la prison centrale,pour la paix sociale.", "A":{"t": "ACCEPTER (+BON / +LIB / +ARG)", "i":{"BONHEUR": 15, "LIBERTE": 20, "ARGENT": 5}, "d": "Un pas vers la démocratie."}, "B":{"t": "REFUSER (-LIB / -BON)", "i":{"BONHEUR": -15, "LIBERTE": -25}, "d": "Le pouvoir reste ferme."}},
            {"min": "MAÎTRE DE CORVETTE", "arg": "Renforcer notre flotte pour prévenir les menaces maritimes à l'Est ?", "A":{"t": "APPROUVER (-ARG / +ARM)", "i":{"ARGENT": -25, "ARMEE": 25}, "d": "Nos eaux sont impénétrables."}, "B": {"t": "REPORTER (-ARM / -BON)", "i":{"ARMEE": -25, "ARGENT": 0, "BONHEUR": -5}, "d": "Vigilance navale réduite."}},
            {"min": "RECHERCHE", "arg": "Nous pouvons transformer notre pays en e-Gouvernement via l'IA.", "A":{"t": "INSTALLER (+EDU / -LIB)", "i":{"EDUCATION": 30, "LIBERTE": -25, "ARGENT": 10}, "d": "Efficacité administrative totale."}, "B":{"t": "REFUSER (+BON)", "i":{"BONHEUR": 15, "EDUCATION": -10}, "d": "L'humain reste au centre."}},
            {"min": "NUMÉRIQUE", "arg": "Un youtubeur renommé à été condamné par le juge d'instruction avoir fait votre caricature.Il s'excuse et demande votre grâce.", "A":{"t": "GRACIER (+LIB / +BON)", "i":{"LIBERTE": 20, "BONHEUR": 15}, "d": "Liberté d'expression saluée."}, "B":{"t": "MAINTENIR (+ARM / -LIB)", "i":{"ARMEE": 10, "LIBERTE": -25}, "d": "Autorité respectée."}},
            {"min": "PREMIER MINISTRE", "arg": "Hier j'ai eu une rencontres avec les géants de la technologie leur demandant plus de restrictions sur la sécurité des données et la protection de la vie privée de nos concitoyens.Ils ont refuser ma proposition de sécurité et menacent de partir.", "A":{"t": "IMPOSER (+BON / -ENT)", "i":{"BONHEUR": 20, "ENTREPRISE": -25}, "d": "Souveraineté numérique imposée."}, "B":{"t": "CÉDER (+ENT / -BON)", "i":{"ENTREPRISE": 20, "BONHEUR": -15}, "d": "Les affaires continuent."}},
            {"min": "TÉLÉSPECTATEUR", "arg": "Le Parlement bloque la nationalisation de la société ALAMINE alors qu'il feras gagner assez d'argent à l'État.", "A": {"t": "SOUTENIR (+ARG / -LIB)", "i": {"ARGENT": 30, "LIBERTE": -25, "ENTREPRISE": -20}, "d": "Les mines sont au peuple."}, "B": {"t": "DÉSAVOUER (+LIB / -ARG)", "i": {"LIBERTE": 20, "ARGENT": -25, "CORRUPTION": -15}, "d": "Marché libre respecté."}},
            {"min": "PRÉSIDENT C.E.I", "arg": " votre parti a obtenu la minoritaire au Parlement ce qui est un problème pour faire passer vos projets. Corrompre des députés ?", "A": {"t": "CORROMPRE (+COR / -ARG)", "i": {"CORRUPTION": 35, "ARGENT": -30, "LIBERTE": -10}, "d": "La majorité est achetée."}, "B": {"t": "DÉCRET (+ARM / -LIB)", "i": {"ARMEE": 25, "LIBERTE": -40, "BONHEUR": -15}, "d": "Le chef décide seul."}},
            {"min": "COUR SUPRÊME", "arg": "Un juge faire appelle à votre Banque pour le gèle de vos comptes car vous êtes suspecté dans une affaire de corruption. Le limoger ?", "A": {"t": "LIMOGER (+ARM / -BON)", "i": {"ARMEE": 25, "BONHEUR": -40, "LIBERTE": -20}, "d": "Les juges vous déteste et vous poursuit."}, "B": {"t": "IMMUNITÉ (+COR / -LIB)", "i": {"CORRUPTION": 35, "LIBERTE": -30, "BONHEUR": -15}, "d": "L'immunité protège le palais."}},
            {"min": "NUMÉRIQUE", "arg": " Monsieur une Intrusion massive dans nos système de défense ont été fait .Nos avons ont tracées et cela viens de la nation voisine. Riposter ?", "A": {"t": "CYBER-RIPOSTE (+ARM / -ARG)", "i": {"ARMEE": 30, "ARGENT": -20, "LIBERTE": -10}, "d": "Notre sytème anti aériens est détruit."}, "B": {"t": "ONU (+LIB / -ARM)", "i": {"LIBERTE": 25, "ARMEE": -20, "BONHEUR": 10}, "d": "Diplomatie internationale."}},
        ]
        
        # TRANSFORMATION POUR LE MODE MERVEILLEUX
        self.events = []
        for e in raw:
            e["A"]["t"] = re.sub(r'[+-]\d+%', lambda m: m.group(0)[0], e["A"]["t"])
            e["B"]["t"] = re.sub(r'[+-]\d+%', lambda m: m.group(0)[0], e["B"]["t"])
            self.events.append({"min": e["min"], "arg": e["arg"], "A": {"t": e["A"]["t"], "i": e["A"]["i"], "dialogue": e["A"]["d"]}, "B": {"t": e["B"]["t"], "i": e["B"]["i"], "dialogue": e["B"]["d"]}})

    def sauvegarder_partie(self):
        with open(self.save_f, "w") as f: json.dump({"stats": self.stats, "mois": self.mois}, f)
    def charger_partie(self):
        if os.path.exists(self.save_f):
            try:
                with open(self.save_f, "r") as f: d = json.load(f); self.stats, self.mois = d["stats"], d["mois"]
            except: pass
    def partie_existe(self): return os.path.exists(self.save_f)
    def supprimer_partie(self):
        if os.path.exists(self.save_f): os.remove(self.save_f)
    def doit_voir_tuto(self): return not os.path.exists(self.tuto_f)
    def marquer_tuto_vu(self):
        with open(self.tuto_f, "w") as f: f.write("1")

if __name__ == '__main__':
    PresidentApp().run()
