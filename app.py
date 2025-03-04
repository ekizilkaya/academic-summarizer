<!DOCTYPE html>
<html>
<head>
    <title>Academic Journal Summarizer</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script> <!-- Add SweetAlert -->
    <style>
        :root {
            --primary: #3f51b5;
            --secondary: #ff4081;
            --accent: #ff4081;
            --light: #f5f7fa;
            --dark: #212121;
            --success: #4caf50;
            --error: #f44336;
            --card-shadow: 0 2px 5px rgba(0,0,0,0.1);
            --transition-speed: 0.3s;
        }

        body {
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }

        /* Header styles */
        .hero-header {
            background-image: linear-gradient(rgba(63, 81, 181, 0.9), rgba(63, 81, 181, 0.8)), url('/api/placeholder/1200/300');
            background-size: cover;
            background-position: center;
            color: white;
            padding: 2rem 0;
            margin-bottom: 1.5rem;
            text-align: center;
            border-bottom: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: relative;
        }

        .hero-header h1 {
            font-weight: 700;
            font-size: 2.2rem;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        @media (max-width: 576px) {
            .hero-header h1 {
                font-size: 1.8rem;
            }
            .hero-header {
                padding: 1.5rem 0;
            }
        }

        .hero-header p {
            font-size: 1.1rem;
            max-width: 90%;
            margin: 0 auto;
            opacity: 0.9;
        }

        /* Card styles */
        .card {
            border: none;
            border-radius: 8px;
            box-shadow: var(--card-shadow);
            margin-bottom: 1.5rem;
            transition: transform var(--transition-speed), box-shadow var(--transition-speed);
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }

        .card-header {
            background-color: var(--primary);
            color: white;
            border-radius: 8px 8px 0 0 !important;
            font-weight: 600;
            font-size: 1.1rem;
            padding: 1rem 1.25rem;
        }

        .card-header i {
            margin-right: 0.5rem;
        }

        .card-body {
            padding: 1.25rem;
        }

        /* Form elements */
        .form-control {
            border-radius: 6px;
            border: 1px solid #ced4da;
            padding: 0.75rem 1rem;
            transition: all var(--transition-speed);
        }

        .form-control:focus {
            border-color: var(--secondary);
            box-shadow: 0 0 0 0.2rem rgba(255, 64, 129, 0.25);
        }

        .form-group label {
            font-weight: 600;
            color: #495057;
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
        }

        /* Journal selection */
        .journal-group {
            margin-bottom: 1.5rem;
        }

        .journal-options {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.75rem;
        }

        .journal-option {
            display: inline-flex;
            align-items: center;
            padding: 0.5rem 0.8rem;
            border-radius: 50px;
            background-color: white;
            border: 2px solid #e9ecef;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: all var(--transition-speed);
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        @media (max-width: 576px) {
            .journal-option {
                padding: 0.4rem 0.6rem;
                font-size: 0.8rem;
            }
        }

        .journal-option:hover {
            border-color: var(--secondary);
            background-color: #f8f9fa;
        }

        .journal-option.active {
            background-color: var(--secondary);
            border-color: var(--secondary);
            color: white;
            box-shadow: 0 2px 5px rgba(255, 64, 129, 0.3);
        }

        .journal-option i {
            margin-right: 0.5rem;
            font-size: 0.8rem;
        }

        /* Button styles */
        .btn-primary {
            background-color: var(--secondary);
            border-color: var(--secondary);
            border-radius: 6px;
            padding: 0.6rem 1.5rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 5px rgba(255, 64, 129, 0.3);
            transition: all var(--transition-speed);
            width: 100%;
        }

        .btn-primary:hover {
            background-color: #f50057;
            border-color: #f50057;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(255, 64, 129, 0.4);
        }

        .btn-primary:active {
            transform: translateY(0);
        }

        /* Spinner styles */
        .spinner-container {
            display: none; /* Initially hidden */
            margin: 2rem auto;
            text-align: center;
        }

        .spinner-text {
            margin-top: 1rem;
            font-weight: 500;
            color: var(--primary);
        }
       .loading-spinner { /* Add a loading spinner */
          border: 4px solid rgba(0, 0, 0, 0.1);
          border-left-color: #0d6efd; /* Or your preferred color */
          border-radius: 50%;
          width: 40px;
          height: 40px;
          animation: spin 1s linear infinite;
          display: inline-block;
          margin-right: 5px;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        /* Results section */
        .results-card {
             margin-top: 20px; white-space: pre-wrap;
            display: none; /* Initially hidden */
        }


        .results-content {
            overflow-wrap: break-word;
            word-wrap: break-word;
            white-space: pre-wrap;
            padding: 1.25rem;
            background-color: white;
              margin-top: 20px; white-space: pre-wrap; /* Preserve formatting */
        }

        .results-content pre {
            display: block;
            width: 100%;
            white-space: pre-wrap;
            word-break: break-word;
            overflow-wrap: break-word;
            font-family: 'Roboto Mono', monospace;
            font-size: 0.9rem;
            line-height: 1.5;
            color: #333;
        }

        @media (max-width: 576px) {
            .results-content pre {
                font-size: 0.8rem;
            }
        }

        /* Copy button styling */
        .copy-button {
            display: none;
            margin-top: 1rem;
            border-radius: 6px;
            background-color: var(--light);
            color: var(--dark);
            transition: all var(--transition-speed);
            width: 100%;
        }

        .copy-button:hover {
            background-color: var(--primary);
            color: white;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }

        /* Footer styles */
        .footer {
            text-align: center;
            padding: 1.5rem 0;
            margin-top: 2rem;
            color: #6c757d;
        }

        .footer a {
            color: var(--primary);
            text-decoration: none;
            transition: color var(--transition-speed);
        }

        .footer a:hover {
            color: var(--secondary);
            text-decoration: underline;
        }

        /* Container adjustments for mobile */
        .container-fluid {
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 1200px;
            margin: 0 auto;
        }

        @media (min-width: 768px) {
            .container-fluid {
                padding-left: 2rem;
                padding-right: 2rem;
            }
        }
          .pink-text { color: #ff4081; } /* Bootstrap's pink */

    </style>
</head>
<body>
    <!-- Hero Header -->
    <header class="hero-header">
        <div class="container-fluid">
            <h1>Academic Journal Summarizer</h1>
            <p>{{ subtitle | safe }}</p>
        </div>
    </header>

    <div class="container-fluid">
        <div class="row">
            <div class="col-lg-10 offset-lg-1">
                <!-- API Key Card -->
                <div class="card fade-in">
                    <div class="card-header">
                         <i class="fas fa-key"></i> AI-Powered Search
                    </div>
                    <div class="card-body">
                       <form id="analysisForm">
                            <div class="form-group">
                                 <label for="api_key">Gemini API Key <a href="/about" class="pink-text" style="text-decoration: none;" target="_blank">How?</a></label>
                                <input type="password" class="form-control" id="api_key" name="api_key" required>
                                <small class="form-text text-muted">Your API key is used client-side and is not stored on the server.</small>
                            </div>

                            <!-- Journal Selection Card -->
                            <div class="form-group journal-group">
                                <label><i class="fas fa-book"></i> Select Journals (up to 3):</label>
                                <div id="journal-options" class="journal-options">
                                    {% for journal, url in journal_dict.items() %}
                                    <div class="journal-option" data-value="{{ journal }}">
                                        <i class="fas fa-journal-whills"></i> {{ journal }}
                                    </div>
                                    {% endfor %}
                                </div>
                                <!-- Hidden input to store selected journals -->
                                <input type="hidden" name="journals" id="selected-journals">
                            </div>

                            <div class="form-group">
                                <label for="custom_rss_url"><i class="fas fa-rss"></i> Custom RSS URL (Optional):</label>
                                <input type="text" class="form-control" id="custom_rss_url" name="custom_rss_url"
                                    placeholder="https://example.com/journal/rss">
                            </div>

                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-search"></i> Analyze Feed Contents
                            </button>
                        </form>
                    </div>
                </div>

               <!-- Loading Spinner -->
                <div class="spinner-container" id="spinner-container">
                    <span class="loading-spinner"></span>
                    <p class="spinner-text">Analyzing academic journals... Please wait.</p>
                </div>

                <!-- Results Card -->
                <div class="card results-card" id="results-card">
                    <div class="card-header">
                        <i class="fas fa-chart-bar"></i> Analysis Results
                    </div>
                    <div class="card-body">
                        <!-- Results content -->
                        <div class="results-content" id="result"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer with About link -->
    <footer class="footer">
        <div class="container-fluid">
            <a href="/about"><i class="fas fa-info-circle"></i> About</a>
        </div>
    </footer>
<script>
    document.getElementById('analysisForm').addEventListener('submit', async function(event) {
        event.preventDefault();

        const apiKey = document.getElementById('api_key').value;
        const selectedJournals = Array.from(document.querySelectorAll('.journal-option.active')).map(el => el.dataset.value);
        const customRssUrl = document.getElementById('custom_rss_url').value;
          const selectedJournalsInput = document.getElementById('selected-journals');


        if (!apiKey) {
             Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Please enter your Gemini API key."
            });
            return;
        }

        if (selectedJournals.length === 0 && !customRssUrl) {
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Please select at least one journal or provide a custom RSS URL."
              });

            return;
        }

        if (selectedJournals.length > 3) {
          Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Please select a maximum of 3 journals."
              });
          return;
        }

        // Store API key in sessionStorage
        sessionStorage.setItem('gemini_api_key', apiKey);

        // Construct FormData for the backend request (no API key here)
        const formData = new FormData();
        formData.append('journals', selectedJournals.join(','));

        if (customRssUrl) {
            formData.append('custom_rss_url', customRssUrl);
        }


        // Show loading indicator

        document.getElementById('spinner-container').style.display = 'block';
        document.getElementById('results-card').style.display = 'none'; // Hide previous results
        document.getElementById('result').innerHTML = ''; // Clear previous results


        try {
            // Step 1:  Get the prompt from the backend
            const backendResponse = await fetch('/', {
                method: 'POST',
                body: formData
            });

            if (!backendResponse.ok) {
                const errorData = await backendResponse.json();
                throw new Error(errorData.error || 'Backend error');
            }

            const { prompt, summary_data } = await backendResponse.json();

          // Step 2: Make the Gemini API request (client-side)
          const geminiResponse = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                  contents: [{ parts: [{ text: prompt }] }],
                  generationConfig: { maxOutputTokens: 16384, temperature: 0.2 }
              })
          });

          if (!geminiResponse.ok) {
              const errorText = await geminiResponse.text();
              throw new Error(`Gemini API Error (${geminiResponse.status}): ${errorText}`);
          }

          const geminiData = await geminiResponse.json();
           let summaryText;
          try {
            summaryText = geminiData.candidates[0].content.parts[0].text.trim();
          } catch (error) {
            console.log(geminiData)
            throw new Error(`Failed to parse Gemini API response`)
          }

            // Step 3:  Display formatted results

           document.getElementById('result').innerHTML = formatSummary(summaryText);
            document.getElementById('results-card').style.display = 'block';


        } catch (error) {
            console.error('Error:', error);
             Swal.fire({
              icon: "error",
              title: "Oops...",
              text: error
            });

        } finally {
            // Hide loading indicator
            document.getElementById('spinner-container').style.display = 'none';
        }
    });
     // Journal selection logic with improved animation
    const journalOptions = document.querySelectorAll('.journal-option');
    let selectedJournals = [];
     const selectedJournalsInput = document.getElementById('selected-journals');


    journalOptions.forEach(option => {
        option.addEventListener('click', () => {
            const journal = option.dataset.value;
            if (selectedJournals.includes(journal)) {
                selectedJournals = selectedJournals.filter(j => j !== journal);
                option.classList.remove('active');
                // Remove icon animation
                const icon = option.querySelector('i');
                icon.className = 'fas fa-journal-whills';

            } else {
                if (selectedJournals.length < 3) {
                    selectedJournals.push(journal);
                    option.classList.add('active');
                     // Add icon animation for selection
                    const icon = option.querySelector('i');
                    icon.className = 'fas fa-check';
                }
            }
              selectedJournalsInput.value = selectedJournals.join(',');
        });
    });

     // Helper function to format the summary text
    function formatSummary(summaryText) {
        const lines = summaryText.split('\n');
        let formattedHtml = '';
        let currentJournal = '';

        for (const line of lines) {
            if (line.startsWith('**')) {
                // Journal header
                if (currentJournal !== '') {
                    formattedHtml += '</div>'; // Close previous journal div
                }
                currentJournal = line.replace(/\*/g, '').trim();
                formattedHtml += `<div class="journal-header"><strong>${currentJournal}</strong></div><div class="journal-articles">`;
            } else if (line.trim().match(/^\d+\./)) {
               // Article entry, including the full line
                formattedHtml += `<div class="article">${line.trim()}</div>`;
            }  else if (line.trim() !== '') {
                // Other lines (within an article),  ensure they are paragraphs.
                formattedHtml += `<p>${line.trim()}</p>`;
            }
        }
        // Close any open journal div
        if (currentJournal !== '') {
            formattedHtml += '</div>';
        }

        return formattedHtml;
    }
</script>
</body>
</html>