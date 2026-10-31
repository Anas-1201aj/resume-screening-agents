# AI-Powered Resume Screening & Job Description Matching Agents

An intelligent, multi-agent recruitment automation system designed to streamline the hiring process through AI-powered resume analysis, semantic search, and automated job-description matching.

The system uses specialized AI agents to process candidate resumes, extract relevant information, generate semantic embeddings, and evaluate candidate suitability against job requirements. It follows an event-driven architecture to enable asynchronous communication and scalable processing.

## 🚀 Key Features

- **Automated Resume Processing:** Extracts text and relevant information from uploaded PDF resumes.
- **OCR Support:** Uses Optical Character Recognition to process scanned resumes and image-based documents.
- **Semantic Embeddings:** Converts resume content into numerical vector representations using Sentence Transformers.
- **Vector Database Integration:** Stores and retrieves resume embeddings using Qdrant for semantic similarity search.
- **AI-Powered Job Matching:** Compares candidate resumes with job descriptions to identify relevant skills and experience.
- **Event-Driven Architecture:** Uses NATS JetStream for asynchronous communication between agents.
- **Automated Candidate Shortlisting:** Evaluates matching scores and updates candidate application statuses.
- **Cloud Storage Integration:** Retrieves candidate resumes from AWS S3.
- **MongoDB Integration:** Reads and updates candidate application and job-related information.

## 🧠 AI Agents Architecture

The system consists of specialized agents, each responsible for a particular stage of the recruitment workflow.

### 1. Resume Indexing Agent

Responsible for processing and indexing candidate resumes.

**Responsibilities:**
- Monitors new candidate applications.
- Retrieves uploaded PDF resumes from AWS S3.
- Extracts text using PyMuPDF.
- Applies OCR using Tesseract for scanned documents.
- Generates semantic embeddings using Sentence Transformers.
- Stores embeddings in the Qdrant vector database.
- Updates resume processing status in MongoDB.

**Output:**
- Extracted resume text.
- Generated vector embeddings.
- Indexed resume records.
- Updated application processing status.

### 2. JD Matching Agent

Responsible for matching candidate resumes against job descriptions.

**Responsibilities:**
- Retrieves job descriptions and candidate information from MongoDB.
- Cleans and preprocesses job description HTML content.
- Generates semantic representations for job requirements.
- Performs similarity searches against indexed resume vectors in Qdrant.
- Calculates matching scores.
- Evaluates candidates based on relevance and matching thresholds.
- Updates application status to selected or rejected based on configured criteria.

**Output:**
- Candidate matching scores.
- Relevant candidate recommendations.
- Automated shortlisting decisions.
- Updated application statuses.

## 🔄 System Workflow

1. A candidate applies for a job and uploads a resume.
2. The application information is stored in MongoDB.
3. An event is published to NATS JetStream.
4. The Resume Indexing Agent receives the event.
5. The agent downloads the resume from AWS S3.
6. Resume text is extracted using PyMuPDF and Tesseract OCR.
7. Sentence Transformers generate semantic embeddings.
8. Embeddings are stored in the Qdrant vector database.
9. The JD Matching Agent receives a matching request.
10. The agent retrieves the job description and searches relevant resume embeddings.
11. Candidate matching scores are calculated.
12. The application status and matching information are updated in MongoDB.

## 🏗️ Architecture Overview

```text
                Candidate Application
                         |
                         v
                    MongoDB
                         |
                         v
                   NATS JetStream
                         |
                         v
              Resume Indexing Agent
                         |
              +----------+----------+
              |                     |
              v                     v
          AWS S3              PDF / OCR
                                    |
                                    v
                          Text Extraction
                                    |
                                    v
                         Sentence Transformers
                                    |
                                    v
                              Qdrant
                                    |
                                    v
                         JD Matching Agent
                                    |
                         Job Description
                                    |
                                    v
                         Semantic Matching
                                    |
                                    v
                         Matching Scores
                                    |
                                    v
                               MongoDB
                                    |
                                    v
                        Candidate Shortlisting
```

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| AI / NLP | Sentence Transformers, NLP |
| Embedding Model | all-MiniLM-L6-v2 |
| Vector Database | Qdrant |
| Database | MongoDB |
| Message Streaming | NATS JetStream |
| Cloud Storage | AWS S3 |
| PDF Processing | PyMuPDF |
| OCR | Tesseract |
| HTML Processing | BeautifulSoup |
| Architecture | Event-Driven, Multi-Agent System |

## 🧩 Important Technical Details

### Embedding Model

The system uses:

`sentence-transformers/all-MiniLM-L6-v2`

- Converts textual information into 384-dimensional vectors.
- Enables semantic similarity comparisons.
- Helps identify relevant candidates beyond simple keyword matching.

### Qdrant Configuration

- Collection: `resumes`
- Vector Size: `384`
- Distance Metric: `Cosine`

### NATS JetStream Events

The agents communicate through asynchronous event-driven messaging.

Important event subjects include:

- `resume.new`
- `resume.batch.process`
- `resume.processed`
- `jd.match.job`
- `jd.match.all`
- `agent.ready`

This approach helps separate agent responsibilities and supports independent processing.

## 📁 Project Structure

```text
astranyx-langchain-agents/
│
├── agents/
│   ├── resume_indexing_agent/
│   │   └── ...
│   │
│   └── jd_matching_agent/
│       └── ...
│
├── config/
│   └── ...
│
├── utils/
│   └── ...
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

*Note: Update the folder structure above to match your actual repository.*

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git

cd YOUR_REPOSITORY
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory.

```env
MONGODB_URI=your_mongodb_connection_string

AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=eu-north-1
AWS_S3_BUCKET=your_bucket_name

QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

NATS_URL=nats://localhost:4222
```

Never commit your `.env` file or expose AWS credentials, database connection strings, or API keys.

### 5. Start Required Services

Make sure the following services are running:

- MongoDB
- Qdrant
- NATS JetStream

### 6. Run the Agents

Run the respective agent entry-point scripts according to your repository configuration.

```bash
python path/to/resume_indexing_agent.py
```

```bash
python path/to/jd_matching_agent.py
```

*Replace the example paths with the actual entry-point filenames in your repository.*

## 🔐 Security Considerations

- Credentials and sensitive configuration are managed through environment variables.
- Candidate resumes are retrieved from private cloud storage.
- Application data is managed through MongoDB.
- Agent communication is handled through dedicated messaging subjects.
- Access to candidate information should be restricted according to application authorization policies.

## 🎯 Project Goals

The primary objective is to automate repetitive recruitment activities and improve candidate-job matching through semantic AI techniques.

The multi-agent architecture makes it possible to separate resume processing, indexing, and candidate matching into independent responsibilities, making the system easier to maintain and extend.

## 🔮 Future Enhancements

- AI-powered interview scheduling and interview-taking agents.
- Automated candidate interview evaluation.
- Advanced skill extraction and experience analysis.
- Improved candidate ranking and recommendation algorithms.
- Agent monitoring and performance analytics.
- Additional notification agents for candidate updates.

## 👨‍💻 Author

**Anas Javed**

GitHub: [Anas-1201aj](https://github.com/Anas-1201aj)

---

⭐ If you find this project interesting, consider giving the repository a star!
