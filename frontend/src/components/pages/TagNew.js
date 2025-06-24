import Page from "../partials/Page";
import ButtonBack from "../partials/ButtonBack";

import TagForm from "../partials/TagForm";

const TagNew = () => {
  return (
    <Page>
      <ButtonBack path="/users">Back to tags list</ButtonBack>
      <h1>New tag</h1>
      <TagForm />
    </Page>
  );
};

export default TagNew;
