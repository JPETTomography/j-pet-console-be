import MeasurementHistograms from "../components/partials/MeasurementHistograms";
import MeasurementEnvConditions from "../components/partials/MeasurementEnvConditions";
import MeasurementComments from "../components/partials/MeasurementComments";

const contentMap = {
  histograms: MeasurementHistograms,
  env_conditions: MeasurementEnvConditions,
  comments: MeasurementComments,
};

export const measurementTabs = [
  {
    id: "histograms",
    name: "Monitoring histograms",
    icon: "chart-bar-square.svg",
  },
  {
    id: "env_conditions",
    name: "Environmental conditions",
    icon: "cloud.svg",
  },
  {
    id: "comments",
    name: "Comments",
    icon: "chat-bubble-bottom-center-text.svg",
  },
];

export const measurementContextContent = (context, measurement, setMeasurement) => {
  const Content = contentMap[context];

  return <Content measurement={measurement} setMeasurement={setMeasurement} />;
};
