const Tag = (props) => {
  const { name, color } = props;

  return (
    <div className="flex items-center gap-3 max-w-max py-1 px-2.5 rounded border bg-white">
      <span
        className="w-4 h-4 rounded"
        style={{ backgroundColor: `#${color}` }}
      ></span>
      <span>{name}</span>
    </div>
  );
};

export default Tag;
