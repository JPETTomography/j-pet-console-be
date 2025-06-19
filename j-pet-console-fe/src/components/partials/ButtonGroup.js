const ButtonGroup = (props) => {
  const { className, children } = props;

  return <div className={`button-group ${className}`}>{children}</div>;
};

export default ButtonGroup;
