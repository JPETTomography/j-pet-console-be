// TODO: fetch + design

const MeasurementEnvConditions = (props) => {
  const { measurement } = props;

  return (
    <div>
      Environmental conditions for <strong>{measurement.name}</strong>
    </div>
  );
};

export default MeasurementEnvConditions;
