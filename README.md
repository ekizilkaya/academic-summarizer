# Academic Journal Summarizer 📚🤖

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![aiohttp](https://img.shields.io/badge/aiohttp-%232196f3.svg?style=for-the-badge&logo=aiohttp&logoColor=white)](https://docs.aiohttp.org/)
[![Beautiful Soup](https://img.shields.io/badge/beautifulsoup4-%23444444.svg?style=for-the-badge&logo=beautifulsoup&logoColor=white)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

**Quickly analyze and summarize academic journal RSS feeds, focusing on quantitative findings.**

- **Target:** Top Journals in Communication
- **Focus:** Quantitative Studies

This application uses a large language model (LLM) API—currently Gemini 2.0 Flash, chosen for its high rate limits and strong performance among free LLMs—to generate concise summaries of recent academic papers, with a focus on quantitative findings. It is designed to help researchers stay up to date with the latest developments, particularly in quantitative research.

## Features ✨

*   **Automated RSS Feed Processing:** Fetches and parses articles from multiple RSS feeds simultaneously.
*   **Quantitative Data Extraction:** Identifies and extracts numerical findings (percentages, statistics, p-values, etc.) from article abstracts.
*   **AI-Powered Summarization:** Uses the  Gemini API to generate concise summaries, focusing on the quantitative aspects of each article.
*   **Journal-Specific Summaries:** Organizes summaries by journal, highlighting the top 3 most important articles (based on quantitative content) from each.
*   **Asynchronous Processing:** Uses `asyncio` and `aiohttp` for efficient and non-blocking handling of multiple requests.
*   **User-Friendly Web Interface:** Provides a simple and intuitive interface built with Flask.
*   **Custom RSS Feed Support:** Allows users to add RSS feeds from journals not included in the default list.
*   **Error Handling:** Robust error handling for API issues, network problems, and invalid RSS feeds.
*   **About Page:** Includes information about the app, its creator, and the rationale behind the focus on quantitative research.

## Why Quantitative Focus? 🎯

Quantitative research results are typically presented in structured formats (statistical analyses, tables, models). This allows for quick access to key empirical insights without losing essential meaning. Qualitative studies, relying on nuanced interpretations and contextual depth, require full engagement with the text to fully appreciate their insights.

## Prerequisites 🛠️

*   **Python 3.7+:** Ensure you have Python 3.7 or a later version installed.
*   **Gemini API Key:** Obtain an API key from [Google AI Studio](https://aistudio.google.com/).  This is *required* to use the summarization feature.
*   **Required Libraries:** Install the necessary Python libraries:

    ```bash
    pip install -r requirements.txt
    ```
    (You should have a `requirements.txt` file in your project. If not, create one with `pip freeze > requirements.txt`).

## Getting Started 🚀

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/ekizilkaya/academic-summarizer.git
    cd academic-summarizer
    ```

2.  **Set up your Gemini API Key:**

    *   **Recommended: Use Environment Variables:**  This is the most secure way.
        *   **Windows:**
            ```bash
            setx GEMINI_API_KEY "your_actual_api_key_here"
            ```
        *   **macOS/Linux:**
            ```bash
            export GEMINI_API_KEY="your_actual_api_key_here"
            ```
            Add this line to your `~/.bashrc`, `~/.zshrc`, or similar file to make it permanent.

        The application will automatically try to use the `GEMINI_API_KEY` environment variable if the user doesn't enter a key in the web interface.

3.  **Run the Application:**

    ```bash
    python app.py
    ```

4.  **Access the Web Interface:** Open your web browser and go to `http://127.0.0.1:5000/`.

5.  **Use the Application:**
    *   Enter your Gemini API key in the provided field (if you didn't set it as an environment variable).
    *   Select up to 3 journals from the list.
    *   Optionally, add a custom RSS URL.
    *   Click "Analyze Feed Contents".
    *   Wait for the analysis to complete (a spinner will indicate progress).
    *   View the summaries in the results area.
    *   You can change and customize everything as you have all the codes and files, including the HTML templates.

## Included Journals 📰

The application includes pre-configured RSS feeds for several top journals in the field of Communication:

*   New Media & Society
*   Social Media + Society
*   Journalism
*   Communication Methods and Measures
*   Communication Research
*   International Journal of Press/Politics
*   Internet Research
*   Big Data and Society
*   Media, Culture & Society
*   International Journal of Communication

You can easily add more by providing their RSS feed URLs.

## Contributing 🤝

Contributions are welcome! Feel free to open issues or submit pull requests.

## License 📝

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.  (You should create a `LICENSE` file in your repository containing the MIT License text.)

## Contact 📧

For questions or feedback, contact Emre Kızılkaya at [emre@journo.com.tr](mailto:emre@journo.com.tr).