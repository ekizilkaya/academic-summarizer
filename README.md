# Academic Journal Summarizer 📚🤖

**Try it out now! [https://academic-summarizer.emrekizilkaya.com/](https://academic-summarizer.emrekizilkaya.com/)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![aiohttp](https://img.shields.io/badge/aiohttp-%232196f3.svg?style=for-the-badge&logo=aiohttp&logoColor=white)](https://docs.aiohttp.org/)
[![Beautiful Soup](https://img.shields.io/badge/beautifulsoup4-%23444444.svg?style=for-the-badge&logo=beautifulsoup&logoColor=white)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

**Quickly analyze and summarize academic journal RSS feeds, focusing on quantitative findings.**

*   **Target:** Top Journals in Communication (default), *but extensible to any field!*
*   **Focus:** Quantitative Studies

This application uses the Gemini 2.0 Flash LLM (via API) to generate concise summaries of recent academic papers, with a strong emphasis on extracting and highlighting quantitative results. It's designed to help researchers (especially in Communication, but adaptable to other fields) stay up-to-date with the latest research, *efficiently*.

## Features ✨

*   **Automated RSS Feed Processing:** Fetches and parses articles from multiple RSS feeds simultaneously.
*   **Quantitative Data Extraction:**  Intelligently identifies and extracts numerical findings (percentages, statistics, p-values, effect sizes, etc.) from article abstracts.  This is the *core* of the summarization process.
*   **AI-Powered Summarization:** Leverages the Gemini API to create concise, informative summaries, *prioritizing* the quantitative aspects of each study.
*   **Journal-Specific Summaries:** Organizes summaries by journal, highlighting the top 3 most *quantitatively significant* articles (based on an importance score) from each.
*   **Asynchronous Processing:** Uses `asyncio` and `aiohttp` for *fast* and *efficient* handling of multiple requests, even with slow or unreliable feeds.
*   **User-Friendly Web Interface:** Provides a simple and intuitive interface built with Flask, including interactive journal selection.
*   **Custom RSS Feed Support:**  Go beyond the default list! Analyze *any* RSS feed from *any* journal by providing its URL.
*   **"Surprise Me" Feature:**  Explore outside your usual field! This option randomly selects journals from a curated list across various disciplines (Psychology, Computer Science, Physics, and more!).
*   **Error Handling:** Includes robust error handling for API issues, network problems, and invalid or inaccessible RSS feeds.  Provides informative error messages to the user.
*   **About Page:** Explains the project's purpose, creator, the focus on quantitative research, and API key security.
* **Copy-to-Clipboard:** Each section can be easily copied

## Why Quantitative Focus? 🎯

Quantitative research presents results in structured, easily extractable formats (statistics, tables, models). This allows for quick access to key *empirical* insights with machine learning. Qualitative studies, while equally valuable, often require deeper reading by a human to grasp their nuanced interpretations. This summarizer prioritizes the readily quantifiable to maximize information gain in minimal time.

## Prerequisites 🛠️

*   **Python 3.7+:** Ensure you have Python 3.7 or later installed.
*   **Gemini API Key:**  Obtain a free API key from [Google AI Studio](https://aistudio.google.com/).  This is *essential* for the summarization feature.
*   **Required Libraries:** Install the necessary Python libraries (specified in `requirements.txt`):

    ```bash
    pip install -r requirements.txt
    ```

## Getting Started 🚀

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/ekizilkaya/academic-summarizer.git
    cd academic-summarizer
    ```

2.  **Set up your Gemini API Key (Securely!):**

    *   **Highly Recommended: Use Environment Variables:**  This is the best practice for security.
        *   **Windows:**
            ```bash
            setx GEMINI_API_KEY "your_actual_api_key_here"
            ```
        *   **macOS/Linux:**
            ```bash
            export GEMINI_API_KEY="your_actual_api_key_here"
            ```
            (Add the `export` line to your `~/.bashrc`, `~/.zshrc`, or equivalent to make it permanent.)

        The app prioritizes the `GEMINI_API_KEY` environment variable if it's set, falling back to user input in the web interface.  *Never hardcode your API key directly into the code.*

3.  **Run the Application:**

    ```bash
    python app.py
    ```

4.  **Access the Web Interface:** Open your web browser and go to `http://127.0.0.1:5000/`.

5.  **Using the Application:**

    *   If you haven't set the `GEMINI_API_KEY` environment variable, enter your Gemini API key in the provided field.  *Your key is only used within your browser; it's never sent to the server.*
    *   Select up to 3 journals from the Communication journal list.
    *   (Optional) Add a custom RSS URL for *any* journal.
    *   (Optional) Click "Surprise Me!" to analyze a random selection of journals from other fields.
    *   Click "Analyze Feed Contents".
    *   A spinner indicates progress.  The analysis can take a few seconds, depending on the number of feeds and the Gemini API response time.
    *   View the concise, quantitatively-focused summaries.  Each journal's top 3 articles (or fewer if less are available) are clearly presented.
    * The summarized text can easily be copied.

## Included Journals 📰

The app includes pre-configured RSS feeds for several top Communication journals. The "Surprise Me" feature draws from a broader list, including top journals in:

*   Sociology
*   Psychology
*   Anthropology
*   Archaeology
*   Law
*   Computer Science
*   Physics
*   Cognitive Sciences
*   History
*   ...and more!

You can *easily* extend this by adding RSS feed URLs, either through the custom URL input or by modifying the `journal_dict` and `surprise_me_journals` dictionaries in the code.

## Contributing 🤝

Contributions are very welcome!  Please feel free to:

*   Open issues to report bugs or suggest features.
*   Submit pull requests with improvements (code, documentation, etc.).  Follow good coding practices (clear variable names, comments, error handling).
*   **Support the Project:** You can support the continued web hosting and development of this open-source application by donating here: [https://buymeacoffee.com/ekizilkaya](https://buymeacoffee.com/ekizilkaya)  Every contribution helps keep this tool available online and improving!

## License 📝

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Contact 📧

For questions or feedback, contact Emre Kızılkaya at [emre@journo.com.tr](mailto:emre@journo.com.tr).
