import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const detectSymbols = async (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await axios.post(`${API_URL}/detect`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress,
  });

  return res.data; // { filename, width, height, count, detections }
};

export const checkHealth = async () => {
  const res = await axios.get(`${API_URL}/health`);
  return res.data; // { status, model_loaded }
};
