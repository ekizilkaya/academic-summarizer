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
        "Media, Culture & Society": "https://journals.sagepub.com/action/showFeed?ui=0&mi=ehikzz&ai=2b4&jc=mcsa&type=axatoc&feed=rss",
        "International Journal of Communication": "https://ijoc.org/index.php/ijoc/gateway/plugin/WebFeedGatewayPlugin/rss2"
    }

    if request.method == 'POST':
        selected_journals_str = request.form.get('journals')
        selected_journals = selected_journals_str.split(',') if selected_journals_str else []
        print(f"Selected Journals: {selected_journals}")  # Keep this for debugging
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
                        await asyncio.sleep(1)  # Add a 1-second delay

                    flattened_articles = [item for sublist in all_articles for item in sublist]
                    if not flattened_articles:
                        return jsonify({'error': "No articles found in the provided RSS feeds."}), 200

                    quantitative_articles = await preprocess_articles(flattened_articles)
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

                    # Corrected summary_data initialization and population
                    summary_data = {
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'journals': {},
                        'total_articles_processed': len(quantitative_articles),
                        'total_journals_processed': len({article['journal'] for article in quantitative_articles})
                    }
                    for article in quantitative_articles:
                        journal = article['journal']
                        if journal not in summary_data['journals']:
                            summary_data['journals'][journal] = {
                                'article_count': 0,
                                'article_titles': []  # Initialize as an empty list
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