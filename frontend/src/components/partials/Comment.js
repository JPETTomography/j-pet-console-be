import React, { useState } from "react";
import { FiMoreHorizontal, FiEdit2, FiTrash2, FiX } from "react-icons/fi";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const BE_URL = process.env.REACT_APP_API_SOURCE || "http://localhost:8000";

const Comment = ({ comment, onEdit, onDelete }) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [previewImg, setPreviewImg] = useState(null);
  const currentUser = JSON.parse(localStorage.getItem("user"));
  const initials = comment.user.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase();

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return `${date.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" })} • ${date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}`;
  };

  return (
    <li className="flex gap-3 p-4 bg-white rounded shadow-sm border border-slate-200 relative group">
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-sky-500 flex items-center justify-center text-white font-bold">
        {initials}
      </div>
      <div className="flex flex-col flex-grow">
        <div className="flex flex-col sm:flex-row sm:items-center gap-1">
          <strong className="text-slate-800 font-semibold">{comment.user.name}</strong>
          <span className="text-xs text-slate-500">{formatDate(comment.created_at)}</span>
        </div>
        <div className="text-slate-700 text-sm mt-1 markdown-content">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{comment.content}</ReactMarkdown>
        </div>
        {comment.pictures && comment.pictures.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {comment.pictures.map((pic) => (
              <button
                key={pic.id}
                type="button"
                className="block p-0 border-none bg-transparent"
                onClick={() => setPreviewImg(`${BE_URL}${pic.path}`)}
                style={{ cursor: "zoom-in" }}
              >
                <img
                  src={`${BE_URL}${pic.path}`}
                  alt="Comment attachment"
                  className="w-24 h-24 object-cover rounded border border-slate-200 hover:shadow-lg transition"
                />
              </button>
            ))}
          </div>
        )}
      </div>
      {currentUser?.id === comment.user.id && (
        <div className="absolute top-4 right-4">
          <FiMoreHorizontal
            className="text-slate-500 cursor-pointer"
            onClick={() => setMenuOpen(!menuOpen)}
          />
          {menuOpen && (
            <div className="absolute top-6 right-0 bg-white border border-slate-300 rounded shadow-md z-10">
              <button className="flex items-center gap-2 px-4 py-2 text-sm text-slate-700 hover:bg-slate-100 w-full" onClick={() => onEdit(comment)}>
                <FiEdit2 />Edit
              </button>
              <button className="flex items-center gap-2 px-4 py-2 text-sm text-red-500 hover:bg-slate-100 w-full" onClick={() => onDelete(comment)}>
                <FiTrash2 />Delete
              </button>
            </div>
          )}
        </div>
      )}
      {previewImg && (
        <div
          className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50"
          onClick={() => setPreviewImg(null)}
        >
          <div className="relative">
            <img
              src={previewImg}
              alt="Preview"
              className="max-h-[80vh] max-w-[90vw] rounded shadow-lg"
              onClick={e => e.stopPropagation()}
            />
            <button
              className="absolute top-2 right-2 bg-white rounded-full p-1 shadow"
              onClick={() => setPreviewImg(null)}
              type="button"
            >
              <FiX size={24} />
            </button>
          </div>
        </div>
      )}
    </li>
  );
};

export default Comment;