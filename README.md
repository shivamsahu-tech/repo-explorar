CodeRAG AI

A rag application, that let the users to chat with there codebase. As expectedly codebases are different then general documents due to there moduler interconnectivity, that why this stores both the Syntaxt Tree of whole codebase and the chunks in database.


Technical Details:
	Whole work can be categorized in 2 part
1. Repo to pinecone: first the repository fetched with git, and stored temporarily, now traverse with each file, and create Syntax tree for each file code, using tree-stter-language-pack parser, then store code of each node in syntax tree in pinecone database, and store whole tree in neo4j graph database.
2. Resule Retreival: when user hit a query, first it generate embedding of that query and find top k vector in pinecone that basically provide top k nodes in that tree, now we traverse top 5 neighbours of that node and extract those node’s code. Use these codes as a context and send to the llm with the user query, in response Gemini LLM provide accurate result that hit the user query.




Here are some videos or images
Video : https://drive.google.com/file/d/1Im3uKlEFYP6dIadV66dBiUt3xHshyjEH/view
Screen shots : 
https://drive.google.com/file/d/1Xum138FfPhLzAtQiSob1Kp0r_GEOC3Se/view
https://drive.google.com/file/d/1ueStwxz3pOzOa-S0nY4SrFSqHuWGqBza/view
https://drive.google.com/file/d/1UFLqPv1ZGAUI32BeEuPAKNmjPrZEeENK/view




Running the Project locally
This repo is devided in 2 sub folder, client and server, where client is a react application and server written in python fast api.

Steps to run
1 fork the repo
Craete sserver/.env and client/.env and put the keys that is given in .env.example file in both folder
 For pinecone : pinecone.com
 For neo4j : neo4j.com
LLM Key : google ai studeio.

NOte : clinet/.env required only server url, that is by default http://localhost:8000


To run the client, use
	Cd client
Npm install
Npm run dev


To run the server:
	Python3 -m venv .venv
Source .venv/bin/activate
Pip3 install -m requirements.txt
Uvicorn main:app –reload



Now your frontend will be serving at port loclahost:5173

Note: there are some internal setting, like if server is up, continuously then it delete the indexes in 15 minutes, refreshing the page lost the index_name, if you lost the index name, then also you can change it by putting index_name (get on pinecone website) in index_name state and changing isChatting state to True, also let you chat with llm by passing the first page.





