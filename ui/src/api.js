import axios from 'axios';

export const processQuery = async (file, query) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('query', query);

  try {
    const response = await axios.post('http://localhost:5001/process', formData, {
      headers: {
        'Accept': 'application/json'
        // Don't set Content-Type, browser will set it correctly with boundary
      }
    });
    const plotPath = response.data.plot_path;      // e.g. "output/plot.png"
    if (!plotPath) throw new Error("No plot_path in response");

    // Prepend your Flask origin so the browser knows where to fetch it from:
    return `http://localhost:5001/${plotPath}`;
  } catch (error) {
    console.error("Axios POST failed:", error);
    throw error;
  }
};
