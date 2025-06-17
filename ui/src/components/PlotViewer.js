import React from 'react';

const PlotViewer = ({ imageUrl }) => {
  return (
    <div>
      <h3>Generated Plot:</h3>
      <img src={imageUrl} alt="Generated Plot" style={{ maxWidth: '600px' }} />
    </div>
  );
};

export default PlotViewer;
