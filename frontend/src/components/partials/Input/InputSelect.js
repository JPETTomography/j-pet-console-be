import InputBase from "./InputBase";

const InputSelect = (props) => {
  const { selectOptions, ...otherProps } = props;

  return (
    <InputBase type="select" selectOptions={selectOptions} {...otherProps} />
  );
};

export default InputSelect;
