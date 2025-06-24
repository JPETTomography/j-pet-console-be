const Form = (props) => {
  const { onSubmit, children } = props;

  return (
    <form
      noValidate
      onSubmit={onSubmit}
      className="flex flex-col gap-5 max-w-3xl"
    >
      {children}
    </form>
  );
};

export default Form;
