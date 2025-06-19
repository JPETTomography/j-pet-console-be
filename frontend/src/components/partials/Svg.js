import { ReactSVG } from "react-svg";

const Svg = (props) => {
  const { src, className } = props;

  return (
    <div className={`shrink-0 ${className}`}>
      <ReactSVG src={src} />
    </div>
  );
};

export default Svg;
