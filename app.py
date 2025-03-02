#!/usr/bin/env python3
import locale

# Monkey-patch locale.setlocale (Keep this as is from your original code)
_old_setlocale = locale.setlocale
def safe_setlocale(category, loc=None):
    if loc == "":
        loc = "C"
    return _old_setlocale(category, loc)
locale.setlocale = safe_setlocale

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from typing import List, Dict, Tuple
import threading
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_very_secret_key'  # CHANGE THIS TO A STRONG, RANDOM KEY!

# --- Helper functions (from your original script, slightly adapted) ---
async def fetch_academic_rss(url: str, session_aiohttp: aiohttp.ClientSession) -> List[Dict]:
    # ... (The fetch_academic_rss function from your original code,
    # but use the passed session_aiohttp)
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with session_aiohttp.get(url, timeout=30, headers=headers) as response:
            if response.status != 200:
                return []
            xml = await response.text()
            try:
                soup = BeautifulSoup(xml, 'lxml')
            except Exception:
                try:
                    soup = BeautifulSoup(xml, 'xml')
                except Exception:
                    try:
                        soup = BeautifulSoup(xml, 'html.parser')
                    except Exception:
                        return []

            feed_title = None
            channel = soup.find('channel')
            if channel:
                feed_title_elem = channel.find('title')
                if feed_title_elem:
                    feed_title = feed_title_elem.text.strip()
            if not feed_title:
                feed_title_elem = soup.find('title')
                if feed_title_elem:
                    feed_title = feed_title_elem.text.strip()

            articles = soup.find_all(['item', 'entry'])
            if not articles:
                articles = soup.find_all(['article', 'content'])
            if not articles:
                return []

            journal_articles = []
            for article in articles:
                title_elem = article.find(['title', 'dc:title']) or article.title
                title = title_elem.text if title_elem else "No title available"

                description_elem = (
                        article.find(['description', 'summary', 'dc:description', 'abstract']) or article.description)
                abstract = description_elem.text if description_elem else ""

                if abstract and ('<' in abstract and '>' in abstract):
                    abstract_soup = BeautifulSoup(abstract, 'html.parser')
                    abstract = abstract_soup.get_text(separator=' ', strip=True)

                authors = article.find_all(['author', 'dc:creator', 'creator'])
                author_list = [author.text for author in authors if author.text]
                if not author_list and abstract:
                    author_patterns = [
                        r'by\s+([\w\s,\.]+)(?:$$|\d|$)',
                        r'authors?[:;]\s*([\w\s,\.]+)',
                        r'^([\w\s,\.]+?),\s+\d{4}',
                    ]
                    for pattern in author_patterns:
                        matches = re.search(pattern, abstract, re.IGNORECASE)
                        if matches:
                            potential_authors = matches.group(1).strip()
                            if len(potential_authors.split()) < 10:
                                author_list = [potential_authors]
                                break
                authors_text = ", ".join(author_list) if author_list else "Unknown Author"

                pub_date = (article.find(['pubDate', 'published', 'dc:date']) or article.pubDate)
                pub_date = pub_date.text if pub_date else ""

                year = ""
                if pub_date:
                    year_match = re.search(r'(20\d\d)', pub_date)
                    if year_match:
                        year = year_match.group(1)
                if not year and abstract:
                    year_match = re.search(r'(20\d\d)', abstract)
                    if year_match:
                        year = year_match.group(1)

                journal_name = feed_title if feed_title else "Unknown Journal"
                journal_name = re.sub(r'RSS Feed$|Feed$|RSS$', '', journal_name).strip()

                numbers_found = extract_numbers(abstract)
                importance_score = len(numbers_found) * 2
                stat_terms = ['significant', 'correlation', 'regression', 'coefficient', 'p-value',
                              'standard deviation']
                for term in stat_terms:
                    if term in abstract.lower():
                        importance_score += 2
                if len(abstract) > 300 and numbers_found:
                    importance_score += 3

                journal_articles.append({
                    'title': title,
                    'abstract': abstract,
                    'journal': journal_name,
                    'authors': authors_text,
                    'published': pub_date,
                    'year': year,
                    'importance_score': importance_score,
                    'quantitative_data': numbers_found,
                    'source_url': url
                })
            return journal_articles
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def extract_numbers(text: str) -> List[str]:
    pattern = r'\d+(?:\.\d+)?%?|\bp\s*<\s*0\.\d+|\br\s*=\s*0\.\d+'
    return re.findall(pattern, text)

async def preprocess_articles(articles: List[Dict]) -> List[Dict]:
    # ... (Your preprocess_articles function - no changes needed)
    quantitative_articles = [article for article in articles
                             if article['quantitative_data'] and article['abstract']]
    quantitative_articles.sort(key=lambda x: x['importance_score'], reverse=True)
    return quantitative_articles


async def summarize_articles(articles: List[Dict], api_key: str) -> Tuple[str, Dict]:
    # ... (Your summarize_articles function, but use the passed api_key)
    if not articles:
        return "No articles found to summarize.", {}

    articles_by_journal = {}
    for article in articles:
        journal = article['journal']
        articles_by_journal.setdefault(journal, []).append(article)

    articles_by_journal = {journal: arts for journal, arts in articles_by_journal.items()
                           if any(article['quantitative_data'] for article in arts)}

    for journal in articles_by_journal:
        articles_by_journal[journal].sort(key=lambda x: x['importance_score'], reverse=True)
        articles_by_journal[journal] = articles_by_journal[journal][:3]

    formatted_articles = ""
    for journal, journal_articles in articles_by_journal.items():
        formatted_articles += f"\n{journal}\n"
        for article in journal_articles:
            formatted_articles += f"\nTitle: {article['title']}\n"
            formatted_articles += f"Authors: {article['authors']}\n"
            formatted_articles += f"Year: {article.get('year', 'Unknown')}\n"
            formatted_articles += f"Abstract: {article['abstract']}\n"
            formatted_articles += f"Quantitative data found: {', '.join(article['quantitative_data'])}\n"
            formatted_articles += f"Published: {article['published']}\n"
            formatted_articles += "-" * 50 + "\n"

    prompt = """
    Analyze these academic articles and create a detailed summary following these rules:

    1. Include the top 3 most important articles from EACH journal provided (or fewer if less than 3 are available)
    2. For each article:
       - Focus primarily on quantitative findings (numbers, percentages, statistical values)
       - Extract the exact numerical results and their context
       - Include a brief conclusion about what these numbers mean (1-2 sentences)

    Format the output exactly as follows:

    **JOURNAL NAME**
    -------------
    1. "Article Title" by Author Names (Year)
       Key findings: [Specific numerical findings with exact numbers, percentages, p-values]
       [Include 1-2 sentences explaining what these numbers mean as a conclusion]

    2. [Next article...]
    3. [Next article...]

    Important: Include EVERY journal provided, even if it only has 1-2 articles with quantitative data.
    If a journal has fewer than 3 articles with quantitative data, explicitly state: "This journal did not contain a third article with substantial quantitative findings."

    Articles to analyze:
    {articles}
    """

    summary = await gemini_api_call(prompt.format(articles=formatted_articles), api_key, max_tokens=16384)


    summary_data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'journals': {},
        'total_articles_processed': len(articles),
        'total_journals_processed': len(articles_by_journal)
    }

    for journal, arts in articles_by_journal.items():
        summary_data['journals'][journal] = {
            'article_count': len(arts),
            'article_titles': [a['title'] for a in arts]
        }

    return summary, summary_data

async def gemini_api_call(prompt: str, api_key: str, max_tokens: int = 8192) -> str:
   # ... (Your gemini_api_call function, but use passed api_key)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.2
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                response_text = await response.text()
                raise Exception(f"API Error ({response.status}): {response_text}")
            response_data = await response.json()
            try:
                return response_data['candidates'][0]['content']['parts'][0]['text'].strip()
            except KeyError:
                error_message = response_data.get('error', {}).get('message', 'Unknown API error')
                raise Exception(f"Failed to parse API response: {error_message}")

# --- Flask Routes ---

@app.route('/', methods=['GET'])
def index():
    journal_dict = {
        "New Media & Society": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=nmsa&type=axatoc&feed=rss",
        "Social Media + Society": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=smsa&type=etoc&feed=rss",
        "Journalism": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=joua&type=axatoc&feed=rss",
        "Communication Methods and Measures": "https://www.tandfonline.com/feed/rss/hcms20",
        "Communication Research": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=crxa&type=axatoc&feed=rss",
        "International Journal of Press/Politics": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=hijb&type=axatoc&feed=rss",
        "Internet Research": "https://www.emerald.com/insight/rss/1066-2243/latest",
        "Big Data and Society": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=bdsa&type=etoc&feed=rss",
        "Media, Culture & Society": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=mcsa&type=axatoc&feed=rss",
        "International Journal of Communication": "https://ijoc.org/index.php/ijoc/gateway/plugin/WebFeedGatewayPlugin/rss2"
    }
    return render_template('index.html', journal_dict=journal_dict)


@app.route('/analyze', methods=['POST'])
def analyze():
    api_key = request.form.get('api_key')
    selected_journals = request.form.getlist('journals')  # Use getlist for checkboxes
    custom_rss_url = request.form.get('custom_rss_url')

    if not api_key:
        return jsonify({'error': 'Please enter your Gemini API key'}), 400

    rss_sources = []
    journal_dict = {
       "New Media & Society": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=nmsa&type=axatoc&feed=rss",
        "Social Media + Society": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=smsa&type=etoc&feed=rss",
        "Journalism": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=joua&type=axatoc&feed=rss",
        "Communication Methods and Measures": "https://www.tandfonline.com/feed/rss/hcms20",
        "Communication Research": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=crxa&type=axatoc&feed=rss",
        "International Journal of Press/Politics": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=hijb&type=axatoc&feed=rss",
        "Internet Research": "https://www.emerald.com/insight/rss/1066-2243/latest",
        "Big Data and Society": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=bdsa&type=etoc&feed=rss",
        "Media, Culture & Society": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=mcsa&type=axatoc&feed=rss",
        "International Journal of Communication": "https://ijoc.org/index.php/ijoc/gateway/plugin/WebFeedGatewayPlugin/rss2"
    }
    for journal_name in selected_journals:
        if journal_name in journal_dict:
            rss_sources.append(journal_dict[journal_name])

    if custom_rss_url:
        if not custom_rss_url.startswith(('http://', 'https://')):
             return jsonify({'error': f'Invalid URL format: {custom_rss_url}'}), 400
        rss_sources.append(custom_rss_url)

    if not rss_sources:
        return jsonify({'error': 'Please select at least one journal or enter a custom RSS URL'}), 400

    # Store data in session (important for background task)
    session['api_key'] = api_key
    session['rss_sources'] = rss_sources

    # Start background task
    thread = threading.Thread(target=run_analysis, args=(app,))  #Pass the app context
    thread.start()

    return jsonify({'message': 'Analysis started.  Check back later for results.'}), 202

@app.route('/results')
def results():
    # Check if results are available in the session
    if 'result' in session:
        result = session.pop('result')  # Retrieve and remove from session
        return render_template('results.html', result=result)
    else:
        return "Results not available yet.  Please wait."

def run_analysis(app): # Background task function
    with app.app_context(): # Create an application context.
        try:
            api_key = session['api_key'] # Retrieve data from session
            rss_sources = session['rss_sources']
            loop = asyncio.new_event_loop() # Create a *new* event loop
            asyncio.set_event_loop(loop)

            async def do_analysis():
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as session_aiohttp:
                    tasks = [fetch_academic_rss(url, session_aiohttp) for url in rss_sources]
                    all_articles = await asyncio.gather(*tasks)
                    flattened_articles = [item for sublist in all_articles for item in sublist]

                    if not flattened_articles:
                        return "No articles found in the provided RSS feeds."

                    quantitative_articles = await preprocess_articles(flattened_articles)
                    if not quantitative_articles:
                        return "No articles with quantitative data found."

                    summary, _ = await summarize_articles(quantitative_articles, api_key)
                    return summary
            result = loop.run_until_complete(do_analysis())
            loop.close()
            session['result'] = result

        except Exception as e:
            session['result'] = f"Error: {str(e)}"