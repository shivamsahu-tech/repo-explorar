import Landing from "./pages/landing";
import LoadingPage from "./pages/Loading";
import ChatPage from "./pages/chat";
import { useState, useEffect } from "react";
// Hi! I'm your CodeRAG AI assistant. I've analyzed your repository and I'm ready to help you understand your codebase. What would you like to know?
export default function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isChating, setIsChating] = useState(true);
  const [indexName, setIndexName] = useState("");
   const [messages, setMessages] = useState([
      {
        id: 1,
        type: 'bot',
        content:  `
This codebase provides a structured way to manage global state in a React application using Redux Toolkit. It establishes a custom pattern for defining state, reducers, and making the Redux \`dispatch\` function globally accessible.

Here's a breakdown:

1.  **State and Reducer Generation (\`generater.ts\`, \`store.ts\`):**
    *   The \`generater.ts\` file (\`src/generater.ts\`) is central to defining your application's global state and the functions that modify it. It declares \`localStates\` and \`localReducers\` which are intended to be populated dynamically or via other parts of the system.
    *   The \`store.ts\` file (\`src/store.ts\`) then uses these \`localStates\` and \`localReducers\` to create a Redux store via \`@reduxjs/toolkit\`'s \`configureStore\` and \`createSlice\` functions. The \`useStore\` hook in this file provides access to the configured Redux store and its actions.

2.  **Global Dispatch Access (\`generater.ts\`, \`Dispatch.tsx\`):**
    *   \`generater.ts\` also contains a \`setDispatch\` function. This function is used to store the Redux \`dispatch\` function in a globally accessible variable within the module.
    *   The \`Dispatch.tsx\` component (\`src/Dispatch.tsx\`) is a lightweight React component whose sole purpose is to retrieve the Redux \`dispatch\` function using the \`useDispatch\` hook and then call \`setDispatch\` from \`generater.ts\` to make it globally available. It renders \`null\` because it doesn't need to display any UI.

3.  **Application Wrapper (\`Handler.tsx\`):**
    *   The \`Handler.tsx\` component (\`src/Handler.tsx\`) serves as the primary wrapper for your application's components that need access to the Redux store.
    *   It uses the \`useStore\` hook to get the Redux store and then wraps its children with <Provider store={store}> from \`react-redux\`, making the store available to all nested components.
    *   Crucially, it renders the <Dispatch /> component inside the \`Provider\`, ensuring that the global \`dispatch\` function is initialized as soon as the application starts.

4.  **Public API (\`index.ts\`):**
    *   The \`index.ts\` file (\`src/index.ts\`) acts as the public interface for this state management setup, exporting \`Handler\` (the main Redux provider component) and likely \`State\` (which would be used to interact with the dynamically defined state).

In essence, this code provides a highly customizable and potentially dynamic Redux setup, making it easy to define state slices and offering a convenient way to dispatch actions from any part of your application, even outside of React components, by making the \`dispatch\` function globally accessible.
` ,
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


  const deleteRepo = () => {
    if(repoUrl == "") return;
   
    try {
      // const result = fetch("", {
      //   method: "POST",

      // })

      
    } catch (error) {
      
    }
  }

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