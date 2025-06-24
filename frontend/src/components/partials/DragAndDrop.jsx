import React, { useEffect, useState } from "react";
import { AiOutlineCheckCircle, AiOutlineCloudUpload } from "react-icons/ai";
import { MdClear } from "react-icons/md";
import "./drag-drop.css";

const MAX_SIZE_MB = 5;
const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];

const BE_URL = process.env.REACT_APP_API_SOURCE;

const DragAndDrop = ({
  onFilesSelected,
  width,
  height,
  existingPictures = [],
  onRemoveExistingPicture,
}) => {
  const [files, setFiles] = useState([]);

  useEffect(() => {
    onFilesSelected(files);
  }, [files, onFilesSelected]);

  const isValidFile = (file) => {
    return (
      file.size <= MAX_SIZE_MB * 1024 * 1024 &&
      ALLOWED_TYPES.includes(file.type)
    );
  };

  const isDuplicate = (nf, prevFiles) => {
    return prevFiles.some(
      (pf) => pf.name === nf.name && pf.lastModified === nf.lastModified
    );
  };

  const handleFileChange = (event) => {
    const selectedFiles = event.target.files;
    if (selectedFiles && selectedFiles.length > 0) {
      const newFiles = Array.from(selectedFiles).filter(isValidFile);
      setFiles((prevFiles) => [
        ...prevFiles,
        ...newFiles.filter((nf) => !isDuplicate(nf, prevFiles)),
      ]);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const droppedFiles = event.dataTransfer.files;
    if (droppedFiles.length > 0) {
      const newFiles = Array.from(droppedFiles).filter(isValidFile);
      setFiles((prevFiles) => [
        ...prevFiles,
        ...newFiles.filter((nf) => !isDuplicate(nf, prevFiles)),
      ]);
    }
  };

  const handleRemoveFile = (index) => {
    setFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
  };

  return (
    <section className="drag-drop" style={{ width: width, height: height }}>
      <div
        className={`document-uploader ${
          files.length > 0 || (existingPictures && existingPictures.length > 0)
            ? "upload-box active"
            : "upload-box"
        }`}
        onDrop={handleDrop}
        onDragOver={(event) => event.preventDefault()}
      >
        <div className="upload-info">
          <AiOutlineCloudUpload />
          <div className="upload-text-container">
            <p className="upload-text-container-drop-here-or">
              Drop files here or{" "}
            </p>
            <label htmlFor="browse" className="browse-btn">
              browse
            </label>
          </div>
        </div>
        <input
          type="file"
          hidden
          id="browse"
          onChange={handleFileChange}
          accept="image/jpeg,image/png,image/webp"
          multiple
        />

        {(existingPictures.length > 0 || files.length > 0) && (
          <div
            className="file-list"
            style={{
              display: "flex",
              gap: 12,
              marginTop: 12,
              flexWrap: "nowrap",
              alignItems: "center",
            }}
          >
            {existingPictures.map((pic, index) => (
              <div
                className="file-item"
                key={pic.id || `existing-${index}`}
                style={{ position: "relative" }}
              >
                <img
                  src={
                    pic.path.startsWith("http")
                      ? pic.path
                      : `${BE_URL}${pic.path}`
                  }
                  alt={pic.path}
                  style={{
                    width: 80,
                    height: 80,
                    objectFit: "cover",
                    borderRadius: 4,
                  }}
                />
                {onRemoveExistingPicture && (
                  <button
                    type="button"
                    style={{
                      position: "absolute",
                      top: 2,
                      right: 2,
                      background: "rgba(255,255,255,0.8)",
                      border: "none",
                      borderRadius: "50%",
                      cursor: "pointer",
                      padding: 2,
                      zIndex: 2,
                    }}
                    onClick={() => onRemoveExistingPicture(pic)}
                    title="Remove existing picture"
                  >
                    <MdClear color="#e53e3e" size={20} />
                  </button>
                )}
              </div>
            ))}
            {files.map((file, index) => (
              <div
                className="file-item"
                key={`new-${index}`}
                style={{ position: "relative" }}
              >
                <img
                  src={URL.createObjectURL(file)}
                  alt={file.name}
                  style={{
                    width: 80,
                    height: 80,
                    objectFit: "cover",
                    borderRadius: 4,
                  }}
                />
                <button
                  type="button"
                  style={{
                    position: "absolute",
                    top: 2,
                    right: 2,
                    background: "rgba(255,255,255,0.8)",
                    border: "none",
                    borderRadius: "50%",
                    cursor: "pointer",
                    padding: 2,
                  }}
                  onClick={() => handleRemoveFile(index)}
                  title="Remove"
                >
                  <MdClear color="#e53e3e" size={20} />
                </button>
              </div>
            ))}
          </div>
        )}

        {(files.length > 0 ||
          (existingPictures && existingPictures.length > 0)) && (
          <div className="success-file" style={{ marginTop: 10 }}>
            <AiOutlineCheckCircle
              style={{ color: "#6DC24B", marginRight: 4 }}
            />
            <p>
              {existingPictures.length > 0
                ? `${existingPictures.length} existing image(s)`
                : ""}
              {existingPictures.length > 0 && files.length > 0 ? " + " : ""}
              {files.length > 0 ? `${files.length} new image(s) selected` : ""}
            </p>
          </div>
        )}
      </div>
    </section>
  );
};

export default DragAndDrop;