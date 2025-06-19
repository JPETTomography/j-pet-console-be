import { formatDate } from "../../utils/formatDate";
import Badge from "./Badge";

import Svg from "./Svg";

const ExperimentCard = (props) => {
  const {
    id,
    name,
    description,
    status,
    location,
    start_date,
    end_date,
    coordinator,
  } = props;

  return (
    <a
      href={`/experiments/${id}`}
      className="flex flex-col gap-4 p-4 rounded-lg border border-slate-200 divide-y divide-slate-200 hover:bg-sky-50"
    >
      <div className="grid gap-2">
        <div className="flex justify-between gap-4">
          <h2>{name}</h2>
          <div className="flex gap-4">
            <Badge status={status} />
          </div>
        </div>
        <div className="flex justify-between gap-4">
          <p>{description}</p>
          <div className="shrink-0 flex items-center gap-2 mb-auto text-sm">
            <Svg src="/icons/calendar-days.svg" className="w-6 h-6" />
            <span>
              {formatDate(start_date)} -{" "}
              {end_date ? formatDate(end_date) : "..."}
            </span>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4 pt-2">
        <div className="flex items-center gap-2 text-sm">
          <Svg src="/icons/map-pin.svg" className="w-6 h-6" />
          {location}
        </div>
        <div className="flex items-center gap-2 text-sm">
          <Svg src="/icons/user-circle.svg" className="w-6 h-6" />
          {coordinator.name}
        </div>
      </div>
    </a>
  );
};

export default ExperimentCard;
