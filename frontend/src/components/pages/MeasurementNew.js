import Page from "../partials/Page";
import ButtonBack from "../partials/ButtonBack";
import { useParams } from "react-router-dom";

import MeasurementForm from "../partials/MeasurementForm";

const MeasurementNew = () => {
  const { experiment_id } = useParams();

  return (
    <Page>
      <ButtonBack path={`/experiments/${experiment_id}`}>
        Back to experiment
      </ButtonBack>
      <h1>New measurement</h1>
      <MeasurementForm />
    </Page>
  );
};

export default MeasurementNew;
