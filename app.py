#!/usr/bin/env python3
import locale

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
from flask import Flask, render_template, request, jsonify
from markupsafe import Markup
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
if app.secret_key is None:
    raise ValueError("SECRET_KEY environment variable not set!")

async def fetch_academic_rss(url: str, session_aiohttp: aiohttp.ClientSession) -> List[Dict]:
    try:
        async with session_aiohttp.get(url, timeout=30) as response:
            if response.status == 403:
                print(f"Error: 403 Forbidden for {url}.  The journal's server is blocking requests.")
                return []
            if response.status != 200:
                print(f"Error fetching {url}: Status code {response.status}")
                return []

            xml = await response.text()
            try:
                soup = BeautifulSoup(xml, 'lxml-xml')  # Explicitly try lxml-xml first
            except Exception:
                try:
                    soup = BeautifulSoup(xml, 'xml')
                except Exception:
                    try:
                        soup = BeautifulSoup(xml, 'html.parser')
                    except Exception:
                        print(f"Error parsing XML from {url}")
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
                print(f"No articles found in {url}")
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
    pattern = r'\d+(?:.\d+)?%?|\bp\s*<\s0.\d+|\br\s=\s*0.\d+'
    return re.findall(pattern, text)

async def preprocess_articles(articles: List[Dict]) -> List[Dict]:
    quantitative_articles = [article for article in articles
                             if article['quantitative_data'] and article['abstract']]
    quantitative_articles.sort(key=lambda x: x['importance_score'], reverse=True)
    return quantitative_articles


async def format_articles_for_prompt(articles: List[Dict]) -> str:
    if not articles:
        return "No articles found to summarize."

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

    return formatted_articles

@app.route('/', methods=['GET', 'POST'])
def index():
    journal_dict = {
        "New Media & Society": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=nmsa&type=axatoc&feed=rss",
        "Social Media + Society": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=smsa&type=etoc&feed=rss",
        "Journalism": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=joua&type=axatoc&feed=rss",
        "Communication Research": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=crxa&type=axatoc&feed=rss",
        "International Journal of Press/Politics": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=hijb&type=axatoc&feed=rss",
        "Internet Research": "https://www.emerald.com/insight/rss/1066-2243/latest",
        "Big Data and Society": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=bdsa&type=etoc&feed=rss",
        "Journal of Marketing": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=jmxa&type=etoc&feed=rss",
        "Journal of Communication": "https://academic.oup.com/rss/site_6088/3963.xml"
    }

    if request.method == 'POST':
        selected_journals_str = request.form.get('journals')
        selected_journals = selected_journals_str.split(',') if selected_journals_str else []
        print(f"Selected Journals: {selected_journals}")
        custom_rss_url = request.form.get('custom_rss_url')

        rss_sources = []
        for journal_name in selected_journals:
            journal_name = journal_name.strip()
            if journal_name in journal_dict:
                rss_sources.append(journal_dict[journal_name])

        if custom_rss_url:
            if not custom_rss_url.startswith(('http://', 'https://')):
                return jsonify({'error': f'Invalid URL format: {custom_rss_url}'}), 400
            rss_sources.append(custom_rss_url)

        if len(rss_sources) > 3:
            return jsonify({'error': 'Please select a maximum of 3 journals.'}), 400
        if len(rss_sources) == 0:
            return jsonify({'error': 'Please select at least 1 journal.'}), 400

        async def fetch_and_preprocess():
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120), headers=headers) as session_aiohttp:
                    all_articles = []
                    for url in rss_sources:
                        articles = await fetch_academic_rss(url, session_aiohttp)
                        all_articles.extend(articles)
                        await asyncio.sleep(1)

                    # The articles are already in the correct format, no need to flatten
                    if not all_articles:
                        return jsonify({'error': "No articles found in the provided RSS feeds."}), 200

                    quantitative_articles = await preprocess_articles(all_articles)
                    formatted_articles_str = await format_articles_for_prompt(quantitative_articles)

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
                    if not quantitative_articles:
                        prompt = "No articles with quantitative data were found in the selected journals."
                    else:
                        prompt = prompt.format(articles=formatted_articles_str)

                    summary_data = {
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'journals': {},
                        'total_articles_processed': len(quantitative_articles),
                        'total_journals_processed': len({article['journal'] for article in quantitative_articles})
                    }
                    for article in quantitative_articles:
                        journal = article['journal']
                        if journal not in summary_data['journals']:
                            summary_data['journals'][journal] = {  # Correct initialization
                                'article_count': 0,
                                'article_titles': []
                            }
                        summary_data['journals'][journal]['article_count'] += 1
                        summary_data['journals'][journal]['article_titles'].append(article['title'])

                    return jsonify({'status': 'ready', 'prompt': prompt, 'summary_data': summary_data})

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(fetch_and_preprocess())
        loop.close()

        return result

    return render_template('index.html', journal_dict=journal_dict,
                           subtitle=Markup("- Target: Top Journals in Communication<br>- Focus: Quantitative Studies"))

@app.route('/about')
def about():
    about_text = Markup("""
    <p>Created by <a href="https://emrekizilkaya.com" target="_blank">Emre Kızılkaya</a></p>
    <p>I created this open-source app in a few hours on a Sunday morning while reviewing the latest academic papers during my Ph.D. studies. The app generates AI-driven summaries focused on quantitative findings in the abstracts from a number of top journals in the field of Communication, using their publicly available RSS feeds. You can also analyze any journal in any other field of study by simply typing the link to its RSS feed.</p>
    <p>This application uses a large language model (LLM) API—currently Gemini 2.0 Flash, chosen for its high rate limits and strong performance among free LLMs—to generate concise summaries of recent academic papers. It is designed to help researchers stay up to date with the latest developments.</p>
    <p>Why the focus on quantitative research? Because its results are typically presented in structured formats—such as statistical analyses, tables, and models—allowing for quick access to key empirical insights without losing essential meaning. In contrast, qualitative studies are harder to summarize as they rely more on nuanced interpretations and contextual depth, which usually require full engagement with the text to fully appreciate their insights.</p>

    <p><strong>Your API Key Security:</strong> Your Gemini API key is <strong>not</strong> sent to our servers.  It is used directly within your web browser (client-side) to communicate with the Gemini API.  This ensures your key remains secure and under your control. Keep your API key secret. Do not share it with others or commit it to public code repositories.</p>

    <p><strong>How to Get a Gemini API Key:</strong>  You can obtain a free Gemini API key by following these steps:</p>
    <ol>
        <li>Go to <a href="https://ai.google.dev/" target="_blank">Google AI Studio</a>.</li>
        <li>Click on "Get API Key".</li>
        <li>Follow the instructions to create a new project or use an existing Google Cloud project.</li>
        <li>Once your project is set up, you can generate an API key.</li>
    </ol>

    <p>Open-sourced under the MIT License, you can find all the files for this hobby project at <a href="https://github.com/ekizilkaya/academic-summarizer" target="_blank">GitHub repository</a>.</p>
    <p>For questions or feedback, feel free to contact me at <a href="mailto:emre@journo.com.tr">emre@journo.com.tr</a></p>
    """)
    return render_template('about.html', about_text=about_text)

if __name__ == '__main__':
    app.run(debug=True)
