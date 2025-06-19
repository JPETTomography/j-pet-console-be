import Page from "../partials/Page";
import ButtonBack from "../partials/ButtonBack";

import DetectorForm from "../partials/DetectorForm";

const DetectorNew = () => {
  return (
    <Page>
      <ButtonBack path="/detectors">Back to detectors list</ButtonBack>
      <h1>New detector</h1>
      <DetectorForm />
    </Page>
  );
};

export default DetectorNew;
