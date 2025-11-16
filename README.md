<div align="center">

# 🧠 CodeRAG AI

### *Chat with Your Codebase Using AI-Powered Intelligence*

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-000000.svg)](https://www.pinecone.io/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph_DB-008CC1.svg)](https://neo4j.com/)
[![Gemini](https://img.shields.io/badge/Gemini-LLM-4285F4.svg)](https://ai.google.dev/)

[🎥 Watch Demo](https://drive.google.com/file/d/1Im3uKlEFYP6dIadV66dBiUt3xHshyjEH/view) • [📸 View Screenshots](#-screenshots) • [🚀 Quick Start](#-quick-start) • [🏗️ Architecture](#-architecture)

---

**Revolutionary RAG system that understands code structure, not just text**

</div>

---

## 🌟 Why CodeRAG AI?

Traditional RAG systems treat code as plain text. **CodeRAG AI is different.**

<table>
<tr>
<td width="50%">

### ❌ Traditional RAG
- 📄 Treats code as text documents
- 🔍 Basic keyword matching
- ❌ Loses code structure
- 💬 Generic responses
- ⚠️ No relationship awareness

</td>
<td width="50%">

### ✅ CodeRAG AI
- 🌳 Parses Abstract Syntax Trees
- 🧬 Semantic code understanding
- ✅ Maintains module dependencies
- 🎯 Context-aware responses
- 🔗 Graph-based relationships

</td>
</tr>
</table>

---

## ✨ Key Features

<div align="center">

| Feature | Description |
|---------|-------------|
| 🌳 **AST Parsing** | Deep syntax tree analysis using Tree-sitter |
| 🔗 **Graph Relationships** | Neo4j stores code structure and dependencies |
| 🚀 **Vector Search** | Lightning-fast semantic retrieval with Pinecone |
| 🤖 **AI-Powered** | Gemini LLM generates intelligent, contextual responses |
| 🎯 **Context-Aware** | Fetches neighboring nodes for complete code context |
| 💡 **Natural Queries** | Ask questions like "Where is the database initialized?" |

</div>

---

## 🏗️ Architecture

### 📥 Repository Indexing Pipeline
```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│  Git Clone  │ ───> │ Tree-sitter  │ ───> │  Generate   │ ───> │    Store     │
│  Repository │      │    Parser    │      │ Embeddings  │      │  Pinecone +  │
│             │      │   (AST)      │      │  & Graph    │      │    Neo4j     │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
```

### 🔍 Query Processing Pipeline
```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│ User Query  │ ───> │   Embed &    │ ───> │   Fetch     │ ───> │    Gemini    │
│   (text)    │      │ Vector Search│      │  Context    │      │  Generates   │
│             │      │  (Pinecone)  │      │  (Neo4j)    │      │   Response   │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
```

### 🔄 Complete Workflow

#### **Phase 1: Repository → Vector & Graph Storage**

1. 📦 **Repository Fetched** - Clone via Git and store temporarily
2. 🌳 **AST Generation** - Parse each file using Tree-sitter language parser
3. 🧬 **Node Embeddings** - Each syntax tree node converted to vector embedding
4. 📊 **Vector Storage** - Store embeddings in Pinecone for semantic search
5. 🔗 **Graph Storage** - Store AST structure in Neo4j for relationship mapping

#### **Phase 2: Query → Intelligent Response**

1. 💬 **User Query** - Natural language question about the codebase
2. 🔍 **Query Embedding** - Convert query to vector representation
3. 🎯 **Similarity Search** - Retrieve top K similar nodes from Pinecone
4. 🔗 **Context Enrichment** - Fetch 5 neighboring nodes per match from Neo4j
5. 🤖 **LLM Processing** - Gemini generates context-aware response
6. ✨ **Intelligent Answer** - Precise, grounded response with code references

---

## 📸 Screenshots

<div align="center">

### 🖥️ Main Interface
<img src="https://drive.google.com/uc?export=view&id=1Xum138FfPhLzAtQiSob1Kp0r_GEOC3Se" width="800" alt="CodeRAG AI Interface">

### 💬 Chat with Codebase
<img src="https://drive.google.com/uc?export=view&id=1ueStwxz3pOzOa-S0nY4SrFSqHuWGqBza" width="800" alt="Chat Interface">

### 🔍 Query Results
<img src="https://drive.google.com/uc?export=view&id=1UFLqPv1ZGAUI32BeEuPAKNmjPrZEeENK" width="800" alt="Query Results">

</div>

---

## 📁 Project Structure
```
RAG-FOR-CODEBASE/
│
├── 📂 client/                          # React.js Frontend
│   ├── 📂 src/
│   │   ├── 📂 assets/                  # Static assets
│   │   ├── 📂 components/              # Reusable UI components
│   │   │   └── markdownLoader.jsx      # Markdown renderer
│   │   ├── 📂 pages/                   # Main application pages
│   │   │   └── App.css                 # Page styles
│   │   ├── App.jsx                     # Main app component
│   │   ├── index.css                   # Global styles
│   │   └── main.jsx                    # Application entry point
│   ├── .env                            # Environment variables
│   ├── .gitignore                      # Git ignore rules
│   ├── eslint.config.js                # ESLint configuration
│   ├── index.html                      # HTML template
│   ├── package.json                    # Dependencies & scripts
│   ├── package-lock.json               # Dependency lock file
│   ├── README.md                       # Client documentation
│   └── vite.config.js                  # Vite configuration
│
├── 📂 server/                          # FastAPI Backend
│   ├── 📂 __pycache__/                 # Python cache files
│   ├── 📂 .env/                        # Virtual environment
│   ├── 📂 data/                        # Temporary data storage
│   ├── 📂 model/                       # ML models
│   ├── 📂 temp/                        # Temporary file storage
│   ├── 📂 template/                    # Response templates
│   │   └── prompt.py                   # LLM prompt templates
│   ├── 📂 utils/                       # Utility modules
│   │   ├── db_connections.py           # Database connections
│   │   ├── embedding.py                # Vector embedding generation
│   │   ├── llm_clone.py                # LLM integration
│   │   ├── parsing.py                  # Code parsing logic
│   │   ├── process.py                  # Processing pipeline
│   │   ├── retrieval.py                # Context retrieval
│   │   └── storage.py                  # Data storage handlers
│   ├── .env                            # Environment variables
│   ├── .env.example                    # Example env file
│   ├── .gitignore                      # Git ignore rules
│   ├── llm.py                          # LLM wrapper
│   ├── main.py                         # FastAPI entry point
│   └── requirements.txt                # Python dependencies
│
├── .gitignore                          # Root git ignore
└── README.md                           # You are here! 📍
```

---

## 🚀 Quick Start

### 📋 Prerequisites

Before you begin, ensure you have the following:

- 🐍 **Python 3.9+** installed
- 📦 **Node.js 18+** and npm
- 🔑 **API Keys** for:
  - [Pinecone](https://www.pinecone.io) - Vector Database
  - [Neo4j Aura](https://neo4j.com) - Graph Database
  - [Google AI Studio](https://ai.google.dev/) - Gemini LLM

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/shivamsahu-tech/coderag-ai.git
cd coderag-ai
```

### 2️⃣ Setup Environment Variables

#### **Client Configuration**

Create `client/.env`:
```env
VITE_SERVER_URL=http://localhost:8000
```

#### **Server Configuration**

Create `server/.env` (refer to `server/.env.example`):
```env
PINECONE_API_KEY=your-pinecone-api-key
NEO4J_URI=your-neo4j-uri
NEO4J_USERNAME=your-neo4j-username
NEO4J_PASSWORD=your-neo4j-password
LLM_API_KEY=your-gemini-api-key
```

### 3️⃣ Install Dependencies

#### **Frontend Setup**
```bash
cd client
npm install
```

#### **Backend Setup**
```bash
cd server
python3 -m venv .env
source .env/bin/activate  # On Windows: .env\Scripts\activate
pip install -r requirements.txt
```

### 4️⃣ Run the Application

#### **Start Backend Server** (Terminal 1)
```bash
cd server
source .env/bin/activate  # On Windows: .env\Scripts\activate
uvicorn main:app --reload
```

✅ Backend running at: **http://localhost:8000**

#### **Start Frontend Client** (Terminal 2)
```bash
cd client
npm run dev
```

✅ Frontend running at: **http://localhost:5173**

### 5️⃣ Start Using CodeRAG AI! 🎉

1. 🌐 Open **http://localhost:5173** in your browser
2. 📝 Paste a GitHub repository URL
3. ⏳ Wait for indexing to complete
4. 💬 Start asking questions about the codebase!

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|-------|-----------|---------|
| 🎨 **Frontend** | React.js + Vite | Modern, fast UI |
| ⚡ **Backend** | FastAPI (Python) | High-performance async API |
| 🧬 **Parser** | Tree-sitter | Multi-language AST parsing |
| 📊 **Vector DB** | Pinecone | Semantic similarity search |
| 🔗 **Graph DB** | Neo4j | Code relationship mapping |
| 🤖 **LLM** | Google Gemini | Context-aware AI responses |
| 📦 **Version Control** | Git | Repository cloning |

</div>

---

## ⚙️ Configuration & Notes

### ⚠️ Important Considerations

<table>
<tr>
<td width="50%">

#### 🔄 **Automatic Index Cleanup**
- Server auto-deletes Pinecone indexes every **15 minutes** when running continuously
- Prevents unnecessary storage costs during development

</td>
<td width="50%">

#### 💾 **Session Persistence**
- If you refresh the page, `index_name` might be lost
- **But you can use it Manually**
  1. Get `index_name` from Pinecone Dashboard
  2. Set it in frontend state
  3. Change `isChatting` to `true`

</td>
</tr>
</table>

---

### 🤝 Want to Contribute?

We welcome contributions! Here's how you can help:

- 🐛 Report bugs
- 💡 Suggest new features
- 🔧 Submit pull requests
- 📖 Improve documentation
- ⭐ Star the repository!

---

## 🎓 Use Cases

<table>
<tr>
<td width="50%">

### 👨‍💻 **For Developers**
- 🔍 Quickly understand unfamiliar codebases
- 📚 Onboard new team members faster
- 🐛 Debug complex issues with context
- 📝 Generate documentation automatically

</td>
<td width="50%">

### 🏢 **For Teams**
- 🤝 Knowledge sharing across teams
- 📊 Code review assistance
- 🔄 Refactoring guidance
- 🎯 Architecture understanding

</td>
</tr>
</table>

---


### 🧪 Example Queries
```
"Where is the database connection initialized?"
"Show me all API endpoints"
"How does authentication work?"
"Find all functions that use the User model"
"What dependencies does this project have?"
```

---

## 🙏 Acknowledgments

Built with amazing open-source tools:

- [Tree-sitter](https://tree-sitter.github.io/) - Incremental parsing system
- [Pinecone](https://www.pinecone.io/) - Vector database
- [Neo4j](https://neo4j.com/) - Graph database
- [Google Gemini](https://ai.google.dev/) - Large language model
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [React](https://reactjs.org/) - UI library

---

##  Author

<div align="center">

### **shsax**

🎓 B.Tech in Information Technology

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/shsax)
[![Portfolio](https://img.shields.io/badge/Portfolio-FF5722?style=for-the-badge&logo=todoist&logoColor=white)](https://shsax.vercel.app)

</div>
