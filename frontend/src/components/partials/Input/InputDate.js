import InputBase from "./InputBase";
import { formatDate } from "../../../utils/formatDate";

const InputDate = (props) => {
  const { value, ...otherProps } = props;

  const date = !!value ? formatDate(value, "yyyy-MM-dd") : "";

  return <InputBase type="date" value={date} {...otherProps} />;
};

export default InputDate;
