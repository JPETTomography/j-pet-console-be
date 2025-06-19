import Svg from "../partials/Svg";

const ButtonBack = (props) => {
  const { path, children } = props;

  return (
    <a href={path} className="link-primary">
      <Svg src="/icons/arrow-left.svg" className="w-5 h-5" />
      {children || "Back"}
    </a>
  );
};

export default ButtonBack;
