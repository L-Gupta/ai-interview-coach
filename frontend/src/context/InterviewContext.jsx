import React, { createContext, useState, useContext } from "react";

const InterviewContext = createContext();

export const InterviewProvider = ({ children }) => {
  const [resumeId, setResumeId] = useState("");
  const [role, setRole] = useState("");
  const [conversation, setConversation] = useState([]); // [{question, answer}]
  const [currentQuestion, setCurrentQuestion] = useState("");

  return (
    <InterviewContext.Provider
      value={{
        resumeId,
        setResumeId,
        role,
        setRole,
        conversation,
        setConversation,
        currentQuestion,
        setCurrentQuestion,
      }}
    >
      {children}
    </InterviewContext.Provider>
  );
};

export const useInterview = () => useContext(InterviewContext);
