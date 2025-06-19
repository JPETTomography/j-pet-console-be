import Svg from "../partials/Svg";

const ButtonNew = (props) => {
  const { path, children } = props;

  return (
    <a href={path} className="btn-primary">
      <Svg src="/icons/plus.svg" className="w-5 h-5" />
      {children || "Add new"}
    </a>
  );
};

export default ButtonNew;
