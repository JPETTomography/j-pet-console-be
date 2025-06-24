const InputBase = (props) => {
  const {
    type,
    name,
    value,
    setValue,
    error,
    hint,
    required = false,
    selectOptions,
    inputClassName = "",
    children,
    ...otherProps
  } = props;

  const inputOptions = {
    id: name,
    name: name,
    value: value,
    required: required,
    onChange: (e) => setValue(e.target.value),
    className: `w-full px-2 py-3 rounded border border-slate-300 group-hover/input:border-sky-700 focus:outline-sky-700 text-slate-800 ${
      error &&
      "!border-rose-700 group-hover/input:!border-rose-700 focus:!outline-rose-700"
    } ${inputClassName}`,
    ...otherProps,
  };

  return (
    <div className="grid gap-2 focus-within:text-sky-700 group/input">
      <label
        htmlFor={name}
        className={`max-w-max hover:text-sky-700 ${
          error && "!text-rose-700"
        } first-letter:uppercase`}
      >
        {name}
      </label>
      <div className="relative">
        {type === "select" ? (
          <select {...inputOptions}>
            {selectOptions.map((option) => {
              return (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              );
            })}
          </select>
        ) : type === "textarea" ? (
          <textarea {...inputOptions}></textarea>
        ) : (
          <input type={type} {...inputOptions} />
        )}
        {children}
      </div>
      {hint && <p className="text-slate-600">{hint}</p>}
      {error && <p className="text-rose-700">{error}</p>}
    </div>
  );
};

export default InputBase;
