# Tool - Master project: Extracting eWOM textual content

by Jonas Kropf, 500846781 (student number)

This tool consists of 8 different apps each serving a specific purpose in the overall tool process. This process is seperated into web scraping, database setup, sentiment extraction, topic extraction, and metric computation. The apps are described in detail below and the preferable app option for each step in the process is highlighted.<br><br>
To be able to use these apps the provided conda environment needs to be created and activated with the commands below in the main tool folder:
1. conda env create -f condaEnv.yaml
2. conda activate env-ewomApp

## Web scraping
The aim of the following apps is to automatically collect OCRs as well as sales data online.

### scrapyApp (preferable)
This app consists of 5 different spiders:
+ movieReviews -> collects movie data (product data, OCRs) from metacritic.com
+ gameReviews -> collects game data (product data, OCRs) from metacritic.com
+ albumReviews -> collects album data (product data, OCRs) from metacritic.com
+ movieSales -> collects movie sales data from boxofficemojo.com
+ gameSales -> collects game sales data from vgchartz.com

The spiders will be executed by the following command in the scrapy project folder (scrapyApp/ewom): scrapy crawl <em>spider-name</em> -O <em>file-name</em>.json<br>
This saves a json file with the scraped data in the scrapy project folder (scrapyApp/ewom).

### beautifulsoupApp (alternative)
This app consists of 2 different scripts:
+ metacritic_movies.py -> collects movie data (product data, OCRs) from metacritic.com
+ boxofficemojo_movie-sales.py -> collects movie sales data from boxofficemojo.com

The scripts will be executed by the following command in the main app folder (beautifulsoupApp): python <em>script-name</em><br>
This saves a json file with the scraped data in the main app folder (beautifulsoupApp).

## Database setup
The aim of the following apps is to save the collected data in a database.

### mongoDBApp (preferable)
This app reads the scraped data into a mongoDB database.<br>
<b>Prerequisites:</b>
  + mongoDB installed and running, download: https://www.mongodb.com/try/download/community

The script will be executed by the following command in the main app folder (mongoDBApp): python database_setup.py<br>
To test the query execution time the following command needs to be executed in the main app folder (mongoDBApp): python query_data.py

### postgreSQLApp (alternative)
This app reads the scraped data into a postgreSQL database.<br>
<b>Prerequisites:</b>
  + postgreSQL installed and running, download: https://www.postgresql.org/download/

The script will be executed by the following command in the main app folder (postgreSQLApp): python database_setup.py<br>
To test the query execution time the following command needs to be executed in the main app folder (postgreSQLApp): python query_data.py

## Sentiment extraction
The aim of the following apps is to extract the reviews' sentiment.

### sentiWordNetApp (preferable)
This app reads data from a mongoDB database, extracts the reviews' sentiment, analyses results and saves the reviews' sentiment in the database.<br>
The script will be executed by the following command in the main app folder (sentiWordNetApp): python sentiment_analysis.py<br>
Exisiting sentiment scores will be overridden.

### kMeansApp (alternative)
This app reads data from a mongoDB database, extracts the reviews' sentiment and analyses results.<br>
The script will be executed by the following command in the main app folder (kMeansApp): python sentiment_analysis.py

## Topic extraction
The aim of the following app is to extract the reviews' topics.

### ldaApp
This app reads data from a mongoDB database, analyses different topic models based on the number of topics, analyses results, extracts the reviews' topic contribution, and saves the reviews' topic contribution in the database.<br>
The script will be executed by the following command in the main app folder (ldaApp): python topic_modelling.py<br>
Exisiting review topic contributions will be overridden.

## Metric computation
The aim of the following app is to compute the relevant metrics.

### metricComputation
This app reads data from a mongoDB database, computes product sentiment score, review breadth and topic depth, and does correlation analysis with product sales.<br>
The script will be executed by the following command in the main app folder (metricComputation): python analysis.py