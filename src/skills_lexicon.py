"""Dictionnaire de compétences : nom canonique -> variantes (FR + EN)."""
import re
import unicodedata

SKILLS = {
    # --- langages ---
    "python": ["python"], "java": ["java", "j2ee", "jee"], "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript"], "php": ["php"], "c#": ["c#", "csharp"], "c++": ["c++"],
    "c": ["langage c"], "sql": ["sql", "t-sql", "pl/sql", "plsql"], "html": ["html", "html5"],
    "css": ["css", "css3"], "kotlin": ["kotlin"], "swift": ["swift"], "dart": ["dart"],
    "r": ["langage r"], "bash": ["bash", "shell"], "vba": ["vba"], "matlab": ["matlab"],
    # --- web / frameworks ---
    "react": ["react", "reactjs", "react.js"], "angular": ["angular", "angularjs"],
    "vue": ["vue", "vuejs", "vue.js"], "node.js": ["node", "nodejs", "node.js"],
    "express": ["express", "expressjs"], "django": ["django"], "flask": ["flask"],
    "fastapi": ["fastapi"], "spring": ["spring", "spring boot", "springboot"],
    "symfony": ["symfony"], "laravel": ["laravel"], "wordpress": ["wordpress"],
    ".net": [".net", "dotnet", "asp.net"], "bootstrap": ["bootstrap"], "jquery": ["jquery"],
    "tailwind": ["tailwind"], "flutter": ["flutter"], "react native": ["react native"],
    "rest api": ["rest", "api rest", "restful", "api", "apis"], "graphql": ["graphql"],
    "frontend": ["frontend", "front end", "front-end"], "backend": ["backend", "back end", "back-end"],
    "full stack": ["full stack", "fullstack", "full-stack"],
    # --- données / IA ---
    "machine learning": ["machine learning", "apprentissage automatique"],
    "deep learning": ["deep learning", "apprentissage profond"],
    "data science": ["data science", "data scientist", "science des donnees"],
    "big data": ["big data", "hadoop", "spark"], "nlp": ["nlp", "traitement du langage"],
    "tensorflow": ["tensorflow"], "pytorch": ["pytorch"], "scikit-learn": ["scikit-learn", "sklearn"],
    "pandas": ["pandas"], "power bi": ["power bi", "powerbi"], "tableau": ["tableau"],
    "excel": ["excel"], "etl": ["etl"], "data analysis": ["data analysis", "analyse de donnees", "analyse des donnees"],
    "statistiques": ["statistique", "statistiques", "statistical analysis", "statistics"],
    "bi": ["business intelligence"],
    # --- bases de données ---
    "mysql": ["mysql"], "postgresql": ["postgresql", "postgres"], "oracle": ["oracle"],
    "mongodb": ["mongodb", "mongo"], "sql server": ["sql server", "sqlserver"],
    "nosql": ["nosql"], "elasticsearch": ["elasticsearch", "elastic search"], "redis": ["redis"],
    # --- devops / cloud / réseau ---
    "docker": ["docker"], "kubernetes": ["kubernetes", "k8s"], "git": ["git", "github", "gitlab"],
    "ci/cd": ["ci/cd", "jenkins", "devops"], "aws": ["aws"], "azure": ["azure"],
    "google cloud": ["google cloud", "gcp", "big query", "bigquery"], "linux": ["linux", "unix"],
    "windows server": ["windows server", "active directory"], "reseaux": ["reseau", "reseaux", "network", "networking", "lan", "wan"],
    "cisco": ["cisco", "ccna"], "tcp/ip": ["tcp/ip", "dhcp", "dns", "vpn"],
    "virtualisation": ["vmware", "hyper-v", "virtualisation", "virtualization"],
    "securite": ["cybersecurite", "securite informatique", "network security", "cybersecurity", "pentest"],
    "support it": ["help desk", "helpdesk", "support technique", "technical support", "maintenance informatique", "troubleshooting"],
    # --- gestion de projet / méthodes ---
    "scrum": ["scrum"], "agile": ["agile", "kanban"], "uml": ["uml", "merise"],
    "gestion de projet": ["gestion de projet", "project management", "chef de projet"],
    "jira": ["jira"], "business analysis": ["business analyst", "business analysis", "analyse fonctionnelle"],
    "tests": ["tests", "testing", "qa", "selenium", "junit", "pytest", "test automation"],
    # --- design / marketing / contenu ---
    "photoshop": ["photoshop"], "illustrator": ["illustrator"], "figma": ["figma"],
    "ui/ux": ["ui/ux", "ux", "ui design", "ux design", "wireframing", "prototyping"],
    "adobe": ["adobe", "indesign", "premiere", "after effects"], "3d": ["3ds max", "blender", "autocad", "solidworks", "3d modeling"],
    "infographie": ["infographie", "graphic design", "graphisme", "design graphique"],
    "seo": ["seo", "sem", "sea", "referencement"], "marketing digital": ["marketing digital", "digital marketing"],
    "reseaux sociaux": ["community management", "community manager", "social media", "reseaux sociaux"],
    "email marketing": ["email marketing", "emailing", "marketing automation"],
    "google analytics": ["google analytics"], "redaction": ["redaction", "copywriting", "content writing", "content strategy"],
    "etude de marche": ["etude de marche", "market research"],
    # --- gestion / commerce / finance / admin ---
    "comptabilite": ["comptabilite", "accounting", "bookkeeping"], "finance": ["finance", "financial analysis", "audit"],
    "fiscalite": ["fiscalite", "tax", "taxation"], "vente": ["vente", "sales", "prospection", "sales prospecting"],
    "negociation": ["negociation", "negotiation"], "relation client": ["relation client", "service client", "customer service", "customer experience"],
    "achats": ["achats", "procurement", "purchasing", "supply chain", "logistique"],
    "ressources humaines": ["ressources humaines", "recrutement", "human resources", "recruitment"],
    "management": ["management", "team leadership", "leadership"], "sap": ["sap"], "salesforce": ["salesforce", "crm"],
    "erp": ["erp", "odoo"], "secretariat": ["secretariat", "administrative", "executive assistant", "calendar management"],
    "formation": ["formation", "enseignement", "teaching", "training"],
    "communication": ["communication"], "negoce": ["business development", "developpement commercial"],
}


def normalize(text):
    text = unicodedata.normalize("NFKD", str(text).lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text)


def _pattern(alias):
    return re.compile(r"(?<![a-z0-9+#.])" + re.escape(alias) + r"(?![a-z0-9+#])")


_PATTERNS = [(name, [_pattern(normalize(a)) for a in aliases]) for name, aliases in SKILLS.items()]


def extract(text):
    """Liste triée des compétences canoniques trouvées dans un texte (FR ou EN)."""
    t = normalize(text)
    return sorted(name for name, pats in _PATTERNS if any(p.search(t) for p in pats))
