import { format } from "date-fns";

export const formatDate = (date, f = "LLL d, yyyy") => {
  return format(date, f);
};
