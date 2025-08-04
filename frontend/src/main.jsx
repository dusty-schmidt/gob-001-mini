// Filename: main.jsx
// Location: frontend/src/main.jsx

import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import ChatTerminal from "../ChatTerminal.jsx";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ChatTerminal />
  </React.StrictMode>
);
