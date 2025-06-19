function badgeVariantStyling(variant) {
  switch (variant) {
    case "draft":
      return "bg-slate-200 border-slate-400";
    case "ongoing":
      return "bg-sky-200 border-sky-300 text-sky-800";
    case "closed":
      return "bg-slate-600 border-slate-600 text-white";
    case "online":
      return "bg-green-100 border-green-500 text-green-700";
    case "offline":
      return "bg-gray-100 border-gray-500 text-gray-700";
    case "damaged":
      return "bg-red-100 border-red-500 text-red-700";
    case "in-repair":
      return "bg-yellow-100 border-yellow-500 text-yellow-700";
    case "commissioned":
      return "bg-blue-100 border-blue-500 text-blue-700";
    case "decommissioned":
      return "bg-purple-100 border-purple-500 text-purple-700";
    default:
      return "bg-white border-slate-600";
  }
}

const Badge = (props) => {
  const { status } = props;

  return (
    <div
      className={`rounded py-0.5 px-2.5 border ${badgeVariantStyling(
        status
      )} capitalize`}
    >
      {status}
    </div>
  );
};

export default Badge;
