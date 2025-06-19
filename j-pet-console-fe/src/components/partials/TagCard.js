import Tag from "./Tag";

const ExperimentCard = (props) => {
  const { id, name, description, color } = props;

  return (
    <a
      href={`/tags/${id}`}
      className="flex flex-col gap-4 p-4 rounded-lg border border-slate-200 divide-y divide-slate-200 hover:bg-sky-50"
    >
      <div className="grid gap-2">
        <div className="flex justify-between gap-4">
          <h2>{name}</h2>
          <div className="flex gap-4">
            <Tag name={name} color={color} />
          </div>
        </div>
        <div className="flex justify-between gap-4">
          <p>{description}</p>
        </div>
      </div>
    </a>
  );
};

export default ExperimentCard;
