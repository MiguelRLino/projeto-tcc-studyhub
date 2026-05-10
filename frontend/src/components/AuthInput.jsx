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
}) {
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
          type={type}
          autoComplete={autoComplete}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          minLength={minLength}
          maxLength={maxLength}
        />
      </div>
    </div>
  );
}
