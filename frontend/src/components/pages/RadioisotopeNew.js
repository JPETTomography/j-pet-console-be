import Page from "../partials/Page";
import ButtonBack from "../partials/ButtonBack";

import RadioisotopeForm from "../partials/RadioisotopeForm";

const RadioisotopeNew = () => {
  return (
    <Page>
      <ButtonBack path="/radioisotopes">Back to radioisotopes list</ButtonBack>
      <h1>New radioisotope</h1>
      <RadioisotopeForm />
    </Page>
  );
};

export default RadioisotopeNew;
