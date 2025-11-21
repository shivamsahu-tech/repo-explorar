<div align="center">

# 🧠 CodeRAG AI

### *Chat with Your Codebase Using AI-Powered Dependency Graphs*

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph_DB-008CC1.svg)](https://neo4j.com/)
[![Gemini](https://img.shields.io/badge/Gemini-LLM-4285F4.svg)](https://ai.google.dev/)

[🌐 Live Demo](https://code-rag.vercel.app) • [📸 View Screenshots](#-screenshots) • [🚀 Quick Start](#-quick-start) • [🏗️ Architecture](#-architecture)

---

**Revolutionary RAG system that builds dependency graphs using Tree-sitter for context-aware code understanding**

</div>

---

## 🌟 Why CodeRAG AI?

Traditional RAG systems break code context with random chunking. **CodeRAG AI is different.**

<table>
<tr>
<td width="50%">

### ❌ Traditional RAG
- 📄 Random chunking breaks meaning
- 🔍 Loses code dependencies
- ❌ No function/class relationships
- 💬 Generic, context-free responses
- ⚠️ Ignores import dependencies

</td>
<td width="50%">

### ✅ CodeRAG AI
- 🌳 Context-rich AST-based chunking
- 🧬 Full dependency graph tracking
- ✅ Function, class, import resolution
- 🎯 Context-aware with relationships
- 🔗 Inter-file dependency mapping

</td>
</tr>
</table>

---

## ✨ Key Features

<div align="center">

| Feature | Description |
|---------|-------------|
| 🌳 **Tree-sitter Parsing** | Context-rich chunking that preserves code structure |
| 🔗 **Dependency Graphs** | Complete function, class, and import relationship mapping |
| 🗄️ **Neo4j Storage** | Graph database with vector embeddings for semantic search |
| 🤖 **Gemini-Powered** | AI responses with full codebase context |
| 🔄 **Session Management** | Create new sessions or rejoin existing conversations |
| 🎯 **Smart Context** | Retrieves code with all dependencies intact |
| 💡 **Natural Queries** | Ask "define loginController" - automatically enhanced |
| 📊 **Multi-Language** | Supports multiple programming languages via Tree-sitter |
| 🔐 **Persistent Sessions** | Use session IDs to continue conversations anytime |

</div>

---

## 🏗️ Architecture

### Core Innovation: Dependency Graph Construction
```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Git Clone     │ ───> │  Tree-sitter     │ ───> │  Extract Nodes  │
│   Repository    │      │  AST Parser      │      │  & Chunks       │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                                            │
                    ┌───────────────────────────────────────┘
                    ▼
        ┌─────────────────────────┐
        │  Build Dependency Graph │
        │  • Function calls       │
        │  • Class calls          │
        │  • Import resolution    │
        │  • Sibling relationships│
        └─────────────────────────┘
                    │
        ┌───────────┴────────────┐
        ▼                        ▼
┌───────────────┐        ┌──────────────┐
│ Generate      │        │ Store in     │
│ Embeddings    │        │ Neo4j with   │
│ (Gemini)      │        │ Session ID   │
└───────────────┘        └──────────────┘
```

### 📥 Ingestion Pipeline

1. **Repository Cloning** - Clone via Git with unique session ID
2. **File Walking** - Extract language from extension, process code files
3. **AST Generation** - Tree-sitter parses code into Abstract Syntax Trees
4. **Import Extraction** - Capture all imports for inter-file dependencies
5. **Chunk Creation** - DFS traversal with MIN_CHUNK_SIZE threshold
   - Node ID: `{file_path}:{start_line}:{node_type}`
   - Extract: name, calls, siblings, parent relationships
6. **Call Resolution** - Match function/class calls to actual definitions
7. **Import Resolution** - Link imports to their source definitions
8. **Document Handling** - Process README, docs with recursive chunking
9. **Graph Storage** - Store in Neo4j with embeddings and session ID

### 🔍 Retrieval Pipeline

1. **User Query** - Natural language question with session ID
2. **Query Enhancement** - LLM expands "define loginController" to full context
3. **Vector Embedding** - Convert enhanced query to vector (Gemini)
4. **Top-K Retrieval** - Find most similar chunks from Neo4j
5. **Dependency Fetching** - Retrieve all related nodes (calls, imports, siblings)
6. **Context Assembly** - Concatenate code with dependencies
7. **LLM Response** - Gemini generates answer with full context
8. **Return Result** - Send back to client with session preserved

---

## 🎯 Session Management

### 🆕 Create New Session
- Paste any GitHub repository URL
- System generates unique session ID
- Index repository and build dependency graph
- Start chatting immediately

### 🔄 Join Existing Session
- Use session ID from previous conversations
- Instantly access same codebase context
- Continue conversations anytime
- Share session IDs with team members

**Live Application:** [code-rag.vercel.app](https://code-rag.vercel.app)

---

## 📊 Dependency Graph Structure

### Chunk Node Schema
```json
{
  "id": "file.py:42:function_definition",
  "name": "loginController",
  "code_str": "def loginController(req, res): ...",
  "ast_type": "function_definition",
  "file": "src/controllers/auth.py",
  "language": "python",
  "start_line": 42,
  "end_line": 58,
  "size": 245,
  "relationships": {
    "belongs_to": ["file.py:10:class_declaration"],
    "parent": ["file.py:5:module"],
    "sibling": ["file.py:60:function_definition"],
    "function_call": ["utils.py:15:function_definition"],
    "class_call": ["models.py:20:class_declaration"],
    "imports_from": ["auth_service.py:5:function_definition"]
  },
  "metadata": {
    "depth": 2,
    "calls": ["validateUser", "generateToken"],
    "type_references": ["User", "AuthService"],
    "is_definition": true,
    "definition_type": "function"
  }
}
```

### Why Dependency Graphs Matter

**Problem:** Traditional RAG loses context
```python
# Random chunk breaks meaning
def process_payment(order):
    validator = OrderValidator()  # What is OrderValidator?
    if validator.check(order):     # check() definition lost
        return payment_gateway.charge()  # No import context
```

**Solution:** CodeRAG preserves everything
- `OrderValidator` → Links to class definition
- `check()` → Links to method implementation  
- `payment_gateway` → Resolves import source
- Siblings → Related functions in same file

---

## 📸 Screenshots

<div align="center">

### 🖥️ Session Selection
<img src="https://drive.google.com/file/d/1kKo6yMc2pFehNXI93tLOupqFd_AL2hxI/view?usp=drive_link" width="800" alt="Session Management">

*Choose to create new session or join existing conversation*

### 💬 Context-Aware Chat
<img src="https://drive.google.com/file/d/1kKo6yMc2pFehNXI93tLOupqFd_AL2hxI/view?usp=drive_link" width="800" alt="Chat Interface">

*Natural conversation with full dependency context*

### 🔍 Neo4j Dependency Graph
<img src="https://drive.google.com/file/d/1kKo6yMc2pFehNXI93tLOupqFd_AL2hxI/view?usp=drive_link" width="800" alt="Graph Visualization">

*Visual representation of code relationships*

</div>

---

## 🚀 Quick Start

### 📋 Prerequisites

- 🐍 **Python 3.9+**
- 📦 **Node.js 18+** and npm
- 🔑 **API Keys:**
  - [Neo4j Aura](https://neo4j.com) - Graph Database
  - [Google AI Studio](https://ai.google.dev/) - Gemini LLM & Embeddings

### 1️⃣ Clone Repository
```bash
git clone https://github.com/shivamsahu-tech/coderag-ai.git
cd coderag-ai
```

### 2️⃣ Environment Configuration

**Client** (`client/.env`):
```env
VITE_SERVER_URL=http://localhost:8000
```

**Server** (`server/.env`):
```env
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
LLM_API_KEY=your-gemini-api-key
EMBEDDING_API_KEY=your-gemini-api-key
```

### 3️⃣ Install Dependencies

**Frontend:**
```bash
cd client
npm install
```

**Backend:**
```bash
cd server
python3 -m venv .env
source .env/bin/activate  # Windows: .env\Scripts\activate
pip install -r requirements.txt
```

### 4️⃣ Run Application

**Backend** (Terminal 1):
```bash
cd server
source .env/bin/activate
uvicorn main:app --reload
```
✅ Running at: **http://localhost:8000**

**Frontend** (Terminal 2):
```bash
cd client
npm run dev
```
✅ Running at: **http://localhost:5173**

### 5️⃣ Start Using! 🎉

1. Open **http://localhost:5173**
2. **New Session:** Paste GitHub URL → Wait for indexing
3. **Join Session:** Enter existing session ID
4. Ask questions about the codebase!

---

## 🛠️ Technical Deep Dive

### Tree-sitter Chunking Strategy

**MIN_CHUNK_SIZE** determines granularity based on:
- ✅ LLM token limits (directly proportional)
- ✅ Embedding dimensions (directly proportional)  
- ✅ Graph density (inversely proportional)

**Node ID Format:** `{file_path}:{start_line}:{node_type}`

**Example:** `src/auth.py:42:function_definition`

### Call Resolution Algorithm

1. Extract calls from AST nodes (e.g., `foo()`)
2. Traverse all chunks to find matching definitions
3. Link caller → callee with `function_call` relationship
4. Store resolved node IDs in relationship fields

### Import Resolution

1. Parse `imports_from` field (e.g., `from auth import login`)
2. Identify source file from import path
3. Search source file chunks for matching module
4. Create `imports_from` relationship edge

---

## 💡 Use Cases

<table>
<tr>
<td width="50%">

### 👨‍💻 **For Developers**
- 🔍 Understand unfamiliar codebases instantly
- 📚 Onboard new team members 10x faster
- 🐛 Debug with full dependency context
- 📝 Auto-generate documentation

</td>
<td width="50%">

### 🏢 **For Teams**
- 🤝 Share session IDs for collaboration
- 📊 Code review with context awareness
- 🔄 Refactoring impact analysis
- 🎯 Architecture exploration

</td>
</tr>
</table>

---

### 🧪 Example Queries
```
"Define loginController"
→ Enhanced: "Explain loginController function, its purpose, related 
   functions, and how it handles authentication"

"Where is the database initialized?"
"Show all functions that call validateUser"
"What does the UserService class do?"
"How are imports structured in this project?"
"Find all API endpoints"
```

---



<div align="center">

### **shsax**

🎓 B.Tech in Information Technology

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/shsax)
[![Portfolio](https://img.shields.io/badge/Portfolio-FF5722?style=for-the-badge&logo=todoist&logoColor=white)](https://shsax.vercel.app)


**Live Demo:** [code-rag.vercel.app](https://code-rag.vercel.app)

</div>

---

<div align="center">

### 🌟 If you find CodeRAG AI helpful, please star the repository! 🌟

</div>