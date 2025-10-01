import Landing from "./pages/landing";
import LoadingPage from "./pages/Loading";
import ChatPage from "./pages/chat";
import { useState, useEffect } from "react";
// Hi! I'm your CodeRAG AI assistant. I've analyzed your repository and I'm ready to help you understand your codebase. What would you like to know?
export default function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isChating, setIsChating] = useState(false);
  const [indexName, setIndexName] = useState("");
   const [messages, setMessages] = useState([
      {
        id: 1,
        type: 'bot',
        content: "Hi! I'm your CodeRAG AI assistant. I've analyzed your repository and I'm ready to help you understand your codebase. What would you like to know?",
        timestamp: new Date()
      }
    ]);




  const goingOut = () => {
      const userWantsRefresh = window.confirm(
      "Do you want to refresh the page? Unsaved changes may be lost."
    );

    if (userWantsRefresh) {
      window.location.reload();
    } else {
      console.log("User canceled refresh");
    }
   
  }

  useEffect(() => {
    const handleBeforeUnload = (e) => {

      e.returnValue = "Refresh or leaving page cause deletion of files";
      return e.returnValue;
    };

    window.addEventListener("beforeunload", handleBeforeUnload);

    // Cleanup
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, []);



const processRepo = async () => {
  if (!repoUrl) return;
  setIsLoading(true);
  try {
    const url = `${import.meta.env.VITE_SERVER_URL}/process-repo`
    const result = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ github_url: repoUrl })
    });

    const res = await result.json();

    if (result.ok && res.status === "success") {
      console.log("Repo processed");
      setIndexName(res.index_name)
      setIsChating(true); 
    } else {
      console.error("Error processing repo:", res);
      alert("Please try again or contact with the maintainer!!!");
    }
  } catch (error) {
    console.error("Network error:", error);
    alert("Server not reachable!");
  } finally {
    setIsLoading(false);
  }
};


  // const deleteRepo = () => {
  //   if(repoUrl == "") return;
   
  //   try {
  //     // const result = fetch("", {
  //     //   method: "POST",

  //     // })

      
  //   } catch (error) {
      
  //   }
  // }

  const chat = async (query) => {
    const url = `${import.meta.env.VITE_SERVER_URL}/chat-with-codebase`
    console.log("index name : ", indexName, "     query : ", query)
      try {
        const result = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ index_name: indexName, query_text: query })
        })
        const res = await result.json();
        if (result.ok && res.status === "success") {
            console.log("chat responded", res.llm_response);
            return res.llm_response;
          } else {
            console.error("Error processing repo:", res);
            alert("Please try again or contact with the maintainer!!!");
          }
      } catch (error) {
        console.error("Network error:", error);
        alert("Server not reachable!");
      }
  }



  return (
    !isLoading && !isChating ? (
      <Landing processRepo={processRepo} setRepoUrl={setRepoUrl}  repoUrl={repoUrl} />
    ) : isLoading ? (
      <LoadingPage/>
    ) : (
      <ChatPage chat={chat} messages={messages} setMessages={setMessages} goingOut={goingOut} />
    )
  )
}