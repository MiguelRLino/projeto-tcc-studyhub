import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

export default function AuthInput({
  id,
  label,
  type = "text",
  icon: Icon,
  autoComplete,
  value,
  onChange,
  placeholder,
  required,
  minLength,
  maxLength,
  permitirAlternarVisibilidade = false,
}) {
  const [visivel, setVisivel] = useState(false);
  const tipoCampo =
    permitirAlternarVisibilidade && type === "password"
      ? visivel
        ? "text"
        : "password"
      : type;

  return (
    <div className="auth-field">
      <label htmlFor={id} className="auth-label">
        {label}
      </label>
      <div className="auth-input-wrap">
        {Icon ? (
          <span className="auth-input-icon" aria-hidden>
            <Icon size={18} strokeWidth={2} />
          </span>
        ) : null}
        <input
          id={id}
          name={id}
          className="auth-input"
          type={tipoCampo}
          autoComplete={autoComplete}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          minLength={minLength}
          maxLength={maxLength}
        />
        {permitirAlternarVisibilidade && type === "password" ? (
          <button
            type="button"
            className="auth-input-toggle"
            onClick={() => setVisivel((v) => !v)}
            aria-label={visivel ? "Ocultar senha" : "Mostrar senha"}
          >
            {visivel ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        ) : null}
      </div>
    </div>
  );
}
