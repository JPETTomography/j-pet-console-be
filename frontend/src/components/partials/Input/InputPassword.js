import InputBase from "./InputBase";
import usePasswordToggle from "../../../utils/usePasswordToggle";

const InputPassword = (props) => {
  const { setPassword, required = true, ...otherProps } = props;
  const [InputType, Icon] = usePasswordToggle();

  return (
    <InputBase
      type={InputType}
      name="password"
      setValue={setPassword}
      required={required}
      inputClassName="pr-12"
      {...otherProps}
    >
      {Icon}
    </InputBase>
  );
};

export default InputPassword;
