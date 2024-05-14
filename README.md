## Projet de Scrapping Immobilier avec Bright Data
Ce projet consiste à extraire des données immobilières à partir d'un site web en utilisant des techniques de web scraping.En utilisant Bright Data pour le scraping web et diverses technologies pour le traitement des données.

# Prérequis
- **Python 3.x**
- **Playwright**
- **BeautifulSoup**
- **OpenAI**
- **Kafka**
- **Bright Data (Bright Data propose une solution complète pour le scraping à grande échelle, en offrant des fonctionnalités avancées pour permettre aux entreprises d'extraire des données à partir du Web de manière efficace, éthique et conforme à la législation.)**

## Fonctionnalités

- **Extraction de données** : Le script extrait les détails des propriétés immobilières, y compris les adresses, les prix, le nombre de chambres, les images, les plans d'étage, etc.
- **Utilisation de l'IA** : Le script utilise l'API de OpenAI pour générer des descriptions détaillées des propriétés à partir des données brutes.
- **Streaming de données** : Les données extraites sont envoyées en continu à un broker Kafka pour être consommées par d'autres systèmes.


# Utilisation

- **Installez toutes les dépendances requises en exécutant pip install -r requirements.txt.**
- **Assurez-vous d'avoir un compte Bright Data actif et configurez vos identifiants dans le script.**
- **Exécutez le script principal main.py.**

# Configuration

- **SBR_WS_CDP : L'URL de connexion au service de scraping browser de Bright Data.**
- **BASE_URL : L'URL de base du site Web à scraper.**
- **LOCATION : L'emplacement des propriétés immobilières à rechercher.**
