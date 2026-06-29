<div align="center">

# AI Teaching Assistant

### Semantic Search Engine for Deep Learning Lectures

An AI-powered assistant built with Retrieval-Augmented Generation that helps students find the exact concept explained in a lecture video and jump to the right timestamp instantly.

[![Live Demo](https://img.shields.io/badge/Live_Demo-Visit_App-4F46E5?style=for-the-badge)](https://deeplearning-rag-assistant.vercel.app/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/daivagnaa/AI-Teaching-Assistant---RAG-Based)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![Gemini](https://img.shields.io/badge/Gemini_API-Powered-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

---

Stop scrubbing through hours of lectures. Ask a question, get the exact timestamp.

[Live Demo](https://deeplearning-rag-assistant.vercel.app/) · [Report Bug](https://github.com/daivagnaa/AI-Teaching-Assistant---RAG-Based/issues) · [Request Feature](https://github.com/daivagnaa/AI-Teaching-Assistant---RAG-Based/issues)

</div>

---

## Overview

This project turns long lecture videos into an interactive learning experience. Instead of manually searching through hours of content, a student can ask a natural-language question and receive the most relevant lecture moments with context and timestamps.

## Why this project exists

Students often lose valuable time trying to locate a specific explanation inside a long video. Traditional keyword search is limited because it does not understand the meaning behind the question. This application uses semantic search to retrieve relevant transcript segments and present them in a more helpful, conversational format.

## Key Features

- Semantic search over lecture transcripts
- Exact timestamped answers for relevant segments
- AI-generated summaries for each result
- Multi-video retrieval across the course playlist
- Graceful handling of off-topic or vague questions
- Responsive interface for desktop and mobile devices

## Architecture

<div align="center">

<img src="static/images/Workflow.png" alt="RAG Pipeline Workflow" width="100%"/>

</div>

## How the RAG pipeline works

1. Preprocessing
   - Videos are downloaded and transcribed with Whisper
   - Transcripts are split into overlapping chunks with timestamps

2. Embedding
   - Each chunk is converted into a vector using Gemini embeddings
   - Similarity search is performed against the stored embedding index

3. Retrieval and generation
   - A user query is embedded and matched against the stored chunks
   - The most relevant passages are sent to Gemini for ranking and summarization

## Tech Stack

- Backend: Python, Flask
- AI / LLM: Gemini 2.5 Flash, Gemini Embedding API
- Embeddings: Gemini Embedding 001
- Similarity search: cosine similarity with scikit-learn
- Frontend: HTML, CSS, JavaScript
- Deployment: Vercel
- Speech-to-text: OpenAI Whisper

## Project Structure

```text
AI-Teaching-Assistant/
│
├── app.py                    # Flask application and API routes
├── rag.py                    # Core RAG pipeline
├── video_link.py             # YouTube video URL mappings
├── merge_chunks.py           # Transcript chunk merging utility
│
├── templates/
│   ├── landing.html          # Landing page
│   └── index.html            # Main search interface
│
├── static/
│   ├── css/style.css         # Styling
│   ├── js/script.js          # Frontend logic
│   └── images/               # Assets
│
├── Embeddings/
│   └── gemini_embeddings.pkl # Pre-computed embeddings
│
├── 0. Pre Processing/        # Video download and preprocessing
├── 1. Speech to Text/        # Whisper transcription pipeline
├── 2. Text To Vector/        # Embedding generation scripts
├── 3. Query To Vector/       # Query embedding experiments
├── 4. Rag Setup/             # RAG pipeline development
│
├── requirements.txt          # Python dependencies
├── vercel.json               # Vercel deployment configuration
└── .vercelignore             # Files excluded from deployment
```

## Getting Started

### Prerequisites

- Python 3.10 or newer
- A Google Gemini API key

### Installation

1. Clone the repository

   ```bash
   git clone https://github.com/daivagnaa/AI-Teaching-Assistant---RAG-Based.git
   cd AI-Teaching-Assistant---RAG-Based
   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables

   Create a .env file in the root directory:

   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. Run the application

   ```bash
   python app.py
   ```

5. Open the app in your browser

   Navigate to http://localhost:5000

## Example Questions

You can ask questions such as:

- What is backpropagation?
- How does a perceptron learn?
- What is the difference between machine learning and deep learning?
- Explain the intuition behind a multi-layer perceptron

## Roadmap

- [x] Semantic search across 17 lecture videos
- [x] Timestamped results with AI-generated descriptions
- [x] Responsive design for mobile and desktop
- [x] Deployment on Vercel
- [ ] Search history
- [ ] Bookmarks
- [ ] Improved citation and highlight support

## Developer

Connect with the project maintainer:

[![Email](https://img.shields.io/badge/Email-devparmar1895%40gmail.com-D14836?logo=gmail&logoColor=white)](mailto:devparmar1895@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Daivagna%20Parmar-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/daivagna-parmar-949315316)
[![GitHub](https://img.shields.io/badge/GitHub-daivagnaa-181717?logo=github&logoColor=white)](https://github.com/daivagnaa)
[![YouTube](https://img.shields.io/badge/YouTube-CampusX-FF0000?logo=youtube&logoColor=white)](https://www.youtube.com/@campusx-official)

## License

This project is open source and intended for educational and learning purposes.

## Acknowledgments

The lecture transcripts used in this project are sourced from the 100 Days of Deep Learning playlist by CampusX.

If you found this project useful, consider giving it a star on GitHub.
