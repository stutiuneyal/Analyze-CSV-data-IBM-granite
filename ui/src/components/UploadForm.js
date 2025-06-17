import React, { useState } from 'react';
import PlotViewer from './PlotViewer';
import { processQuery } from '../api';

const UploadForm = () => {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState('');
  const [imageUrl, setImageUrl] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !query) {
      return alert("Provide both CSV and query");
    }

    try {
      const url = await processQuery(file, query); // e.g. http://localhost:5001/output/plot.png
      // Bust browser cache by appending timestamp
      const cacheBustedUrl = `${url}?t=${Date.now()}`;
      setImageUrl(cacheBustedUrl);
    } catch (err) {
      console.error(err);
      alert('Failed to generate plot.');
    }
  };

  return (
    <div>
      <h2>Ask a question about your CSV</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files[0])}
          required
        />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. Show average salary by department as pie chart"
          required
        />
        <button type="submit">Generate Plot</button>
      </form>
      {imageUrl && <PlotViewer imageUrl={imageUrl} />}
    </div>
  );
};

export default UploadForm;
