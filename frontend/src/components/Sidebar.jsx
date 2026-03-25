import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { ragAPI } from '../utils/api';

export default function Sidebar({ onUploadSuccess }) {
  const { user, logout } = useAuth();
  const [docs, setDocs] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState('');
  const [dragOver, setDragOver] = useState(false);

  const initials = user?.full_name
    ?.split(' ')
    .map(n => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase() || '?';

  const isUploader = ['admin', 'manager'].includes(user?.role);

  useEffect(() => {
    ragAPI.documents()
      .then(res => setDocs(res.data.documents))
      .catch(() => {});
  }, [uploadMsg]);

  const handleFile = async (file) => {
    if (!file || !file.name.endsWith('.pdf')) {
      setUploadMsg('❌ Only PDF files are supported.');
      return;
    }
    setUploading(true);
    setUploadMsg('');
    try {
      const res = await ragAPI.ingest(file);
      setUploadMsg(`✅ Ingested "${res.data.filename}" (${res.data.chunks_created} chunks)`);
      if (onUploadSuccess) onUploadSuccess();
    } catch (err) {
      setUploadMsg(`❌ ${err.response?.data?.detail || 'Upload failed'}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <span className="sidebar-logo-icon">🏢</span>
        <span className="sidebar-logo-text">DocTalk AI</span>
        <span className="status-dot" style={{ marginLeft: 'auto' }} title="System online" />
      </div>

      {/* Documents list */}
      <div className="sidebar-section-label">Knowledge Base</div>
      {docs.length === 0 ? (
        <div style={{ fontSize: 12, color: 'var(--text-3)', padding: '4px 8px' }}>
          No documents ingested yet
        </div>
      ) : (
        docs.map(doc => (
          <div key={doc} className="sidebar-doc-item">
            <span>📄</span>
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={doc}>
              {doc}
            </span>
          </div>
        ))
      )}

      {/* Upload (admin/manager only) */}
      {isUploader && (
        <>
          <div className="sidebar-section-label" style={{ marginTop: 20 }}>Upload Document</div>
          <div
            className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
            onDragOver={e => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-upload').click()}
          >
            {uploading ? '⏳ Uploading…' : '📎 Drop PDF here or click to upload'}
            <input
              id="file-upload"
              type="file"
              accept=".pdf"
              style={{ display: 'none' }}
              onChange={e => { if (e.target.files[0]) handleFile(e.target.files[0]); }}
            />
          </div>
          {uploadMsg && (
            <div className="upload-success" style={uploadMsg.startsWith('❌') ? { color: '#f87171', background: 'rgba(239,68,68,0.1)', borderColor: 'rgba(239,68,68,0.2)' } : {}}>
              {uploadMsg}
            </div>
          )}
        </>
      )}

      {/* User chip */}
      <div className="sidebar-bottom">
        <div className="user-chip">
          <div className="user-avatar">{initials}</div>
          <div className="user-info">
            <div className="user-name">{user?.full_name}</div>
            <div className="user-role">{user?.role} {user?.department ? `· ${user.department}` : ''}</div>
          </div>
          <button className="logout-btn" onClick={logout} title="Sign out">
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/>
            </svg>
          </button>
        </div>
      </div>
    </aside>
  );
}