from services.llm.llm import chat

def enhance_query(user_query: str) -> str:
    prompt = f"""
          You are a query optimization expert for a RAG system that indexes GitHub repositories. Transform user queries about code and development topics to improve retrieval from documentation, README files, issues, pull requests, and source code comments.
          Enhance queries by adding 5-8 relevant technical terms including programming terminology, framework names, library references, error messages, command names, and configuration terms that developers commonly use. Consider that GitHub repositories contain diverse content types with varied writing styles, so include synonyms and related concepts that might appear across documentation, code comments, issues, and wikis.
          Expand the semantic scope to capture both theoretical concepts and practical implementation terms, covering installation, troubleshooting, API usage, deployment, and integration patterns. Ensure the optimized query retrieves relevant information whether it's in technical README files, GitHub discussions, code comments, or project documentation, providing comprehensive coverage of the repository's knowledge base.

          User Query : {user_query}
          """
    
    enhanced_query = chat(prompt)
    return enhanced_query