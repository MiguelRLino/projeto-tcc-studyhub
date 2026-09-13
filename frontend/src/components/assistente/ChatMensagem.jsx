import { Bot, User } from "lucide-react";

export default function ChatMensagem({ tipo, texto }) {
  const isAluno = tipo === "aluno";

  return (
    <div className={`ia-msg${isAluno ? " ia-msg--aluno" : " ia-msg--ia"}`}>
      <div className="ia-msg-avatar" aria-hidden>
        {isAluno ? <User size={16} /> : <Bot size={16} />}
      </div>
      <div className="ia-msg-bubble">
        <span className="ia-msg-label">{isAluno ? "Você" : "Assistente"}</span>
        <p>{texto}</p>
      </div>
    </div>
  );
}
