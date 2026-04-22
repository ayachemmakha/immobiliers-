import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
import plotly.express as px
import hashlib
from datetime import datetime

# =============================================================================
# 🔹 SYSTÈME D'AUTHENTIFICATION AMÉLIORÉ
# =============================================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_auth():
    if 'users' not in st.session_state:
        st.session_state.users = {
            "admin": {"password": hash_password("admin123"), "role": "admin", "name": "Administrateur"},
            "medecin": {"password": hash_password("medecin123"), "role": "medecin", "name": "Dr Dupont"}
        }
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

def login_register_page():
    # Application du CSS
    inject_custom_css()
    
    # Container principal centré
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Carte de connexion
        st.markdown("""
        <div style='background: white; padding: 3rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);'>
            <div class='main-header' style='text-align: center; margin: -3rem -3rem 2rem -3rem; border-radius: 10px 10px 0 0;'>
                <h1 style='color: white; margin: 0;'>🫁 TB Diagnostic Pro</h1>
                <p style='color: white; opacity: 0.9; margin: 0.5rem 0 0 0;'>Système Expert de Diagnostic de la Tuberculose</p>
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🚀 **Connexion**", "👤 **Créer un Compte**"])
        
        with tab1:
            with st.form("login_form"):
                st.subheader("Connectez-vous à votre compte")
                
                username = st.text_input(
                    "**Nom d'utilisateur**",
                    placeholder="Entrez votre nom d'utilisateur...",
                    key="login_username"
                )
                
                password = st.text_input(
                    "**Mot de passe**", 
                    type="password",
                    placeholder="Entrez votre mot de passe...",
                    key="login_password"
                )
                
                col_btn1, col_btn2 = st.columns([2, 1])
                with col_btn1:
                    login_btn = st.form_submit_button(
                        "**Se connecter** 🚀", 
                        use_container_width=True,
                        type="primary"
                    )
                
                if login_btn:
                    if username in st.session_state.users and st.session_state.users[username]["password"] == hash_password(password):
                        st.session_state.logged_in = True
                        st.session_state.current_user = username
                        st.success(f"✅ Connexion réussie! Bienvenue {st.session_state.users[username]['name']}")
                        st.rerun()
                    else:
                        st.error("❌ Identifiants incorrects")
        
        with tab2:
            with st.form("register_form"):
                st.subheader("Créez votre compte")
                
                new_username = st.text_input(
                    "**Nom d'utilisateur**",
                    placeholder="Choisissez un nom d'utilisateur...",
                    key="reg_username"
                )
                
                col_pass1, col_pass2 = st.columns(2)
                with col_pass1:
                    new_password = st.text_input(
                        "**Mot de passe**", 
                        type="password",
                        placeholder="Créez un mot de passe...",
                        key="reg_password"
                    )
                with col_pass2:
                    confirm_password = st.text_input(
                        "**Confirmer le mot de passe**", 
                        type="password",
                        placeholder="Confirmez le mot de passe...",
                        key="reg_confirm"
                    )
                
                full_name = st.text_input(
                    "**Nom complet**",
                    placeholder="Entrez votre nom complet...",
                    key="reg_fullname"
                )
                
                role = st.selectbox(
                    "**Rôle**", 
                    ["medecin", "infirmier"],
                    key="reg_role"
                )
                
                register_btn = st.form_submit_button(
                    "**Créer le compte** 👤", 
                    use_container_width=True,
                    type="primary"
                )
                
                if register_btn:
                    if new_username in st.session_state.users:
                        st.error("❌ Ce nom d'utilisateur existe déjà")
                    elif new_password != confirm_password:
                        st.error("❌ Les mots de passe ne correspondent pas")
                    elif len(new_password) < 4:
                        st.error("❌ Le mot de passe doit avoir au moins 4 caractères")
                    else:
                        st.session_state.users[new_username] = {
                            "password": hash_password(new_password),
                            "role": role,
                            "name": full_name
                        }
                        st.success("✅ Compte créé avec succès! Vous pouvez maintenant vous connecter.")
        
        st.markdown("</div>", unsafe_allow_html=True)
# ==================== CONFIGURATION BASE DE DONNÉES ====================
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'gestion_immobiliere',
    'user': 'root',
    'password': '123456789'
}

# ==================== FONCTIONS BASE DE DONNÉES ====================
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"❌ Erreur de connexion à la base de données: {e}")
        return None


# ==================== FONCTIONS AUTHENTIFICATION ====================
def hash_password(password):
    """Hachage du mot de passe avec SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def creer_compte(username, password):
    """Crée un nouveau compte utilisateur"""
    conn = get_connection()
    if not conn:
        return False, "Problème de connexion à la base de données"
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hash_password(password))
        )
        conn.commit()
        return True, "Compte créé avec succès!"
    except mysql.connector.IntegrityError:
        return False, "Ce nom d'utilisateur existe déjà"
    except Exception as e:
        return False, f"Erreur: {e}"
    finally:
        conn.close()

def verifier_login(username, password):
    """Vérifie les identifiants de connexion"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()
    return user is not None

# ==================== FONCTIONS DASHBOARD ====================
def load_transactions_data():
    """Charge toutes les transactions depuis la base"""
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    
    query = "SELECT date, montant, type, description, mois, annee FROM transactions ORDER BY date DESC"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def ajouter_transaction(date, montant, type_transaction, description):
    """Ajoute une nouvelle transaction"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        mois = date.month
        annee = date.year
        cursor.execute('''
            INSERT INTO transactions (date, montant, type, description, mois, annee)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (date, montant, type_transaction, description, mois, annee))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'ajout: {e}")
        return False
    finally:
        conn.close()

def show_dashboard():
    """Affiche le dashboard avec les graphiques Plotly"""
    st.markdown("## 📊 Tableau de Bord - Analyses Immobilières")
    
    # Chargement des données
    df = load_transactions_data()
    
    if df.empty:
        st.warning("⚠️ Aucune donnée disponible. Ajoutez des transactions pour voir les analyses.")
        return
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    total_ventes = df[df['type'] == 'Vente']['montant'].sum() if 'Vente' in df['type'].values else 0
    total_locations = df[df['type'] == 'Location']['montant'].sum() if 'Location' in df['type'].values else 0
    nb_transactions = len(df)
    montant_moyen = df['montant'].mean()
    
    col1.metric("💰 Total Ventes", f"{total_ventes:,.0f} DH")
    col2.metric("🏠 Total Locations", f"{total_locations:,.0f} DH")
    col3.metric("📈 Nombre Transactions", nb_transactions)
    col4.metric("⭐ Montant Moyen", f"{montant_moyen:,.0f} DH")
    
    st.markdown("---")
    
    # Graphiques Plotly
    col1_graph, col2_graph = st.columns(2)
    
    with col1_graph:
        # Analyse mensuelle
        monthly_data = df.groupby(['annee', 'mois'])['montant'].sum().reset_index()
        monthly_data['periode'] = monthly_data['annee'].astype(str) + '-M' + monthly_data['mois'].astype(str)
        
        fig_monthly = px.bar(
            monthly_data, 
            x='mois', 
            y='montant', 
            color='annee',
            title="📅 Évolution Mensuelle des Revenus",
            labels={'montant': 'Montant (DH)', 'mois': 'Mois', 'annee': 'Année'},
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_monthly.update_layout(height=400)
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with col2_graph:
        # Analyse annuelle
        yearly_data = df.groupby('annee')['montant'].sum().reset_index()
        
        fig_yearly = px.line(
            yearly_data, 
            x='annee', 
            y='montant',
            title="📈 Évolution Annuelle des Revenus",
            labels={'montant': 'Montant Total (DH)', 'annee': 'Année'},
            markers=True,
            line_shape='linear'
        )
        fig_yearly.update_traces(marker=dict(size=10), line=dict(width=3))
        fig_yearly.update_layout(height=400)
        st.plotly_chart(fig_yearly, use_container_width=True)
    
    # Deuxième ligne de graphiques
    col3_graph, col4_graph = st.columns(2)
    
    with col3_graph:
        # Distribution par type
        type_data = df.groupby('type')['montant'].sum().reset_index()
        
        fig_pie = px.pie(
            type_data, 
            values='montant', 
            names='type',
            title="🥧 Répartition par Type de Transaction",
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col4_graph:
        # Top transactions
        top_transactions = df.nlargest(5, 'montant')[['date', 'type', 'montant', 'description']]
        fig_top = px.bar(
            top_transactions,
            x='description',
            y='montant',
            color='type',
            title="🏆 Top 5 des Transactions",
            labels={'montant': 'Montant (DH)', 'description': 'Description'},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_top.update_layout(height=400)
        st.plotly_chart(fig_top, use_container_width=True)
    
    # Formulaire pour ajouter des transactions
    st.markdown("---")
    st.markdown("## ➕ Ajouter une nouvelle transaction")
    
    with st.form("add_transaction"):
        col1_form, col2_form, col3_form, col4_form = st.columns(4)
        
        with col1_form:
            date_trans = st.date_input("Date", datetime.now())
        with col2_form:
            montant_trans = st.number_input("Montant (DH)", min_value=0.0, step=1000.0)
        with col3_form:
            type_trans = st.selectbox("Type", ["Vente", "Location"])
        with col4_form:
            desc_trans = st.text_input("Description")
        
        submitted = st.form_submit_button("💾 Ajouter la transaction")
        
        if submitted:
            if montant_trans > 0:
                if ajouter_transaction(date_trans, montant_trans, type_trans, desc_trans):
                    st.success("✅ Transaction ajoutée avec succès!")
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de l'ajout")
            else:
                st.warning("⚠️ Le montant doit être supérieur à 0")

# ==================== INTERFACE PRINCIPALE STREAMLIT ====================
def main():
    st.set_page_config(
        page_title="Gestion Immobilière",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    

    
    # Gestion de l'état de connexion
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
    
    # Sidebar pour la navigation
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/real-estate.png", width=80)
        st.title("🏢 Gestion Immobilière")
        st.markdown("---")
        
        if not st.session_state.logged_in:
            st.info("🔐 Veuillez vous connecter ou créer un compte")
        else:
            st.success(f"👋 Bonjour, {st.session_state.username}")
            st.markdown("---")
            if st.button("🚪 Se déconnecter", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.rerun()
    
    # Page d'authentification
    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align: center;'>🏢 Plateforme de Gestion Immobilière</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>La solution complète pour gérer vos biens immobiliers</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["🔐 Se connecter", "📝 Créer un compte"])
        
        with tab1:
            st.markdown("### Connexion à votre compte")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                login_username = st.text_input("Nom d'utilisateur", key="login_user")
                login_password = st.text_input("Mot de passe", type="password", key="login_pass")
                
                if st.button("Se connecter", use_container_width=True):
                    if verifier_login(login_username, login_password):
                        st.session_state.logged_in = True
                        st.session_state.username = login_username
                        st.success("✅ Connexion réussie!")
                        st.rerun()
                    else:
                        st.error("❌ Nom d'utilisateur ou mot de passe incorrect")
        
        with tab2:
            st.markdown("### Création d'un nouveau compte")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                new_username = st.text_input("Choisir un nom d'utilisateur", key="new_user")
                new_password = st.text_input("Choisir un mot de passe", type="password", key="new_pass")
                confirm_password = st.text_input("Confirmer le mot de passe", type="password", key="confirm_pass")
                
                if st.button("Créer mon compte", use_container_width=True):
                    if not new_username or not new_password:
                        st.warning("⚠️ Veuillez remplir tous les champs")
                    elif new_password != confirm_password:
                        st.warning("⚠️ Les mots de passe ne correspondent pas")
                    elif len(new_password) < 4:
                        st.warning("⚠️ Le mot de passe doit contenir au moins 4 caractères")
                    else:
                        success, message = creer_compte(new_username, new_password)
                        if success:
                            st.success(f"✅ {message} Vous pouvez maintenant vous connecter!")
                        else:
                            st.error(f"❌ {message}")
    
    else:
        # Dashboard après connexion
        show_dashboard()

# ==================== POINT D'ENTRÉE ====================
if __name__ == "__main__":
    main()
