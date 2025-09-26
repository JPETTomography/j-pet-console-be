import React, { useState, useEffect, useCallback, useMemo } from "react";
import api from "../../api";
import Comment from "./Comment";
import DragAndDrop from "./DragAndDrop";
import SimpleMDE from "react-simplemde-editor";
import { marked } from "marked";
import "easymde/dist/easymde.min.css";

// Constants
const EDITOR_OPTIONS_BASE = {
  spellChecker: false,
  status: false,
  autofocus: false,
  previewRender: (plainText) =>
    marked(plainText, {
      gfm: true,
      breaks: true,
      smartLists: true,
      smartypants: true,
    }),
  toolbar: [
    "bold", "italic", "strikethrough", "heading", "|",
    "unordered-list", "ordered-list", "|",
    "link", "table", "|",
    "preview", "guide",
  ],
};

const INITIAL_FORM_STATE = {
  editorValue: "",
  files: [],
  existingPictures: [],
  deletedPictureIds: [],
};

const MeasurementComments = ({ measurement, setMeasurement }) => {
  const [loading, setLoading] = useState(false);
  const [editingCommentId, setEditingCommentId] = useState(null);
  const [formState, setFormState] = useState(INITIAL_FORM_STATE);
  const [dragAndDropKey, setDragAndDropKey] = useState(0);

  const { editorValue, files, existingPictures, deletedPictureIds } = formState;

  // Memoized values
  const isEditing = editingCommentId !== null;
  const isFormEmpty = !editorValue.trim() && files.length === 0;
  const editingComment = useMemo(() => 
    isEditing ? measurement.comments.find(c => c.id === editingCommentId) : null,
    [isEditing, measurement.comments, editingCommentId]
  );

  const editorOptions = useMemo(() => ({
    ...EDITOR_OPTIONS_BASE,
    placeholder: isEditing ? "Edit your comment..." : "Add a comment...",
  }), [isEditing]);

  // State management helpers
  const resetFormState = useCallback(() => {
    setFormState(INITIAL_FORM_STATE);
    setDragAndDropKey(prev => prev + 1);
  }, []);

  const updateFormState = useCallback((updates) => {
    setFormState(prev => ({ ...prev, ...updates }));
  }, []);

  // Effects
  useEffect(() => {
    if (isEditing && editingComment) {
      setFormState({
        editorValue: editingComment.content || "",
        files: [],
        existingPictures: editingComment.pictures || [],
        deletedPictureIds: [],
      });
      setDragAndDropKey(prev => prev + 1);
    } else if (!isEditing) {
      resetFormState();
    }
  }, [editingCommentId, editingComment, isEditing, resetFormState]);

  // Event handlers
  const handleEditorChange = useCallback((value) => {
    updateFormState({ editorValue: value });
  }, [updateFormState]);

  const handleRemoveExistingPicture = useCallback((pic) => {
    updateFormState({
      existingPictures: existingPictures.filter(p => !p.id || p.id !== pic.id),
      deletedPictureIds: [...deletedPictureIds, pic.id],
    });
  }, [existingPictures, deletedPictureIds, updateFormState]);

  const handleFilesSelected = useCallback((newFiles) => {
    updateFormState({ files: newFiles });
  }, [updateFormState]);

  // API operations
  const saveComment = useCallback(async () => {
    const currentContent = editorValue.trim();
    
    if (!currentContent) {
      alert("Please enter some content for the comment.");
      return;
    }
    
    setLoading(true);
    try {
      const endpoint = isEditing
        ? `/measurements/${measurement.id}/comments/${editingCommentId}`
        : `/measurements/${measurement.id}/comments`;

      const formData = new FormData();
      formData.append("content", currentContent);
      
      files.forEach(file => formData.append("files", file));
      
      if (isEditing && deletedPictureIds.length > 0) {
        deletedPictureIds.forEach(id => formData.append("deleted_picture_ids", id));
      }

      const response = await api[isEditing ? "patch" : "post"](endpoint, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const updatedComment = response.data.comment;
      
      setMeasurement(prev => ({
        ...prev,
        comments: isEditing
          ? prev.comments.map(c => c.id === editingCommentId ? updatedComment : c)
          : [...prev.comments, updatedComment],
      }));
      
      if (isEditing) {
        setEditingCommentId(null);
      } else {
        resetFormState();
      }
    } catch (error) {
      console.error("Error saving comment:", error);
      alert("Failed to save comment. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [
    editorValue, files, deletedPictureIds, isEditing, editingCommentId,
    measurement.id, setMeasurement, resetFormState
  ]);

  const deleteComment = useCallback(async (commentId) => {
    if (!window.confirm("Are you sure you want to delete this comment?")) return;
    
    setLoading(true);
    try {
      await api.delete(`/measurements/${measurement.id}/comments/${commentId}`);
      setMeasurement(prev => ({
        ...prev,
        comments: prev.comments.filter(c => c.id !== commentId),
      }));
    } catch (error) {
      console.error("Error deleting comment:", error);
      alert("Failed to delete comment. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [measurement.id, setMeasurement]);

  const cancelEdit = useCallback(() => {
    setEditingCommentId(null);
  }, []);

  const startEdit = useCallback((commentId) => {
    setEditingCommentId(commentId);
  }, []);

  return (
    <div className="p-6 bg-white rounded shadow-md">
      <h3 className="text-xl font-semibold mb-4">
        Comments for{" "}
        <strong className="text-sky-700">{measurement.name}</strong>
      </h3>
      
      {/* Comments List */}
      {measurement.comments?.length > 0 ? (
        <ul className="space-y-4">
          {measurement.comments.map((comment) => (
            <Comment
              key={comment.id}
              comment={comment}
              onEdit={() => startEdit(comment.id)}
              onDelete={() => deleteComment(comment.id)}
            />
          ))}
        </ul>
      ) : (
        <p className="text-slate-500 italic">
          No comments available for this measurement.
        </p>
      )}
      
      {/* Comment Form */}
      <div className="mt-6 markdown">
        <SimpleMDE
          value={editorValue}
          onChange={handleEditorChange}
          options={editorOptions}
        />
        
        <p className="text-sm text-gray-600 mt-2">Drop file here or browse</p>
        
        <DragAndDrop
          key={dragAndDropKey}
          onFilesSelected={handleFilesSelected}
          existingPictures={existingPictures}
          onRemoveExistingPicture={handleRemoveExistingPicture}
        />
        
        {/* Form Actions */}
        <div className="flex items-center gap-4 mt-4">
          {isEditing && (
            <button
              onClick={cancelEdit}
              className="px-4 py-2 rounded bg-red-500 hover:bg-red-700 text-white font-medium disabled:opacity-50 transition-colors"
              disabled={loading}
              type="button"
            >
              Cancel
            </button>
          )}
          
          <button
            onClick={saveComment}
            className={`px-4 py-2 rounded font-medium transition-colors ${
              isFormEmpty || loading
                ? "bg-gray-400 cursor-not-allowed text-gray-600"
                : "bg-sky-700 hover:bg-sky-900 text-white"
            }`}
            disabled={isFormEmpty || loading}
          >
            {loading ? (
              isEditing ? "Saving..." : "Adding..."
            ) : (
              isEditing ? "Save Changes" : "Add Comment"
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default MeasurementComments;