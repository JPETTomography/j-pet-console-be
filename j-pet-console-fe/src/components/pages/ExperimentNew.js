import Page from "../partials/Page";
import ButtonBack from "../partials/ButtonBack";

import ExperimentForm from "../partials/ExperimentForm";

const ExperimentNew = () => {
  return (
    <Page>
      <ButtonBack path="/experiments">Back to experiments list</ButtonBack>
      <h1>New experiment</h1>
      <ExperimentForm />
    </Page>
  );
};

export default ExperimentNew;
