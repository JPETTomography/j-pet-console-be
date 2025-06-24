import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Login from "./components/pages/Login";

import UsersList from "./components/pages/UsersList";
import UserNew from "./components/pages/UserNew";
import User from "./components/pages/User";
import UserEdit from "./components/pages/UserEdit";

import ExperimentsList from "./components/pages/ExperimentsList";
import ExperimentNew from "./components/pages/ExperimentNew";
import Experiment from "./components/pages/Experiment";
import ExperimentEdit from "./components/pages/ExperimentEdit";

import DetectorsList from "./components/pages/DetectorsList";
import DetectorNew from "./components/pages/DetectorNew";
import Detector from "./components/pages/Detector";
import DetectorEdit from "./components/pages/DetectorEdit";

import TagsList from "./components/pages/TagsList";
import TagNew from "./components/pages/TagNew";
import Tag from "./components/pages/Tag";
import TagEdit from "./components/pages/TagEdit";

import RadioisotopesList from "./components/pages/RadioisotopesList";
import RadioisotopeNew from "./components/pages/RadioisotopeNew";
import Radioisotope from "./components/pages/Radioisotope";
import RadioisotopeEdit from "./components/pages/RadioisotopeEdit";

import MeasurementNew from "./components/pages/MeasurementNew";
import Measurement from "./components/pages/Measurement";
import MeasurementEdit from "./components/pages/MeasurementEdit";

import NotFound from "./components/pages/NotFound";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />

        <Route path="/users" element={<UsersList />} />
        <Route path="/users/new" element={<UserNew />} />
        <Route path="/users/:user_id" element={<User />} />
        <Route path="/users/:user_id/edit" element={<UserEdit />} />

        <Route path="/experiments" element={<ExperimentsList />} />
        <Route path="/experiments/new" element={<ExperimentNew />} />
        <Route path="/experiments/:experiment_id" element={<Experiment />} />
        <Route
          path="/experiments/:experiment_id/edit"
          element={<ExperimentEdit />}
        />

        <Route
          path="/experiments/:experiment_id/measurements/new"
          element={<MeasurementNew />}
        />
        <Route
          path="/experiments/:experiment_id/measurements/:measurement_id"
          element={<Measurement />}
        />
        <Route
          path="/experiments/:experiment_id/measurements/:measurement_id/edit"
          element={<MeasurementEdit />}
        />

        <Route path="/detectors" element={<DetectorsList />} />
        <Route path="/detectors/new" element={<DetectorNew />} />
        <Route path="/detectors/:detector_id" element={<Detector />} />
        <Route path="/detectors/:detector_id/edit" element={<DetectorEdit />} />

        <Route path="/tags" element={<TagsList />} />
        <Route path="/tags/new" element={<TagNew />} />
        <Route path="/tags/:tag_id" element={<Tag />} />
        <Route path="/tags/:tag_id/edit" element={<TagEdit />} />

        <Route path="/radioisotopes" element={<RadioisotopesList />} />
        <Route path="/radioisotopes/new" element={<RadioisotopeNew />} />
        <Route
          path="/radioisotopes/:radioisotope_id"
          element={<Radioisotope />}
        />
        <Route
          path="/radioisotopes/:radioisotope_id/edit"
          element={<RadioisotopeEdit />}
        />

        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}

export default App;
