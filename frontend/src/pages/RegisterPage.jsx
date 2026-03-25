import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    department: '',
  });
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));
    setErrors(er => ({ ...er, [e.target.name]: '' }));
  };

  const validate = () => {
    const errs = {};
    if (!form.full_name.trim()) errs.full_name = 'Full name is required';
    if (!form.email) errs.email = 'Email is required';
    if (form.password.length < 8) errs.password = 'Password must be at least 8 characters';
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setServerError('');
    setLoading(true);
    try {
      await register(form);
      navigate('/chat');
    } catch (err) {
      setServerError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-brand">
        <div className="brand-logo">🏢</div>
        <div className="brand-title">DocTalk AI</div>
        <div className="brand-subtitle">
          Join your team on the intelligent policy assistant platform.
        </div>
        <div className="brand-features">
          {[
            'Get instant answers to HR questions',
            'Find policies in seconds',
            'Never miss important updates',
            'All answers backed by source docs',
          ].map(f => (
            <div key={f} className="brand-feature">
              <span className="brand-feature-dot" />
              {f}
            </div>
          ))}
        </div>
      </div>

      <div className="auth-form-panel">
        <div className="auth-form-inner">
          <h1>Create account</h1>
          <p className="subtitle">Set up your DocTalk AI access</p>

          {serverError && <div className="error-banner">{serverError}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="full_name">Full Name</label>
              <input
                id="full_name" name="full_name" type="text"
                className={`form-input ${errors.full_name ? 'error' : ''}`}
                placeholder="Jane Smith"
                value={form.full_name} onChange={handleChange} autoFocus
              />
              {errors.full_name && <div className="field-error">{errors.full_name}</div>}
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="email">Work Email</label>
              <input
                id="email" name="email" type="email"
                className={`form-input ${errors.email ? 'error' : ''}`}
                placeholder="jane@company.com"
                value={form.email} onChange={handleChange}
              />
              {errors.email && <div className="field-error">{errors.email}</div>}
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="department">Department <span style={{color:'var(--text-3)',fontWeight:400,textTransform:'none'}}>(optional)</span></label>
              <input
                id="department" name="department" type="text"
                className="form-input"
                placeholder="e.g. Engineering, HR, Finance"
                value={form.department} onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="password">Password</label>
              <input
                id="password" name="password" type="password"
                className={`form-input ${errors.password ? 'error' : ''}`}
                placeholder="Min. 8 characters"
                value={form.password} onChange={handleChange}
              />
              {errors.password && <div className="field-error">{errors.password}</div>}
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating account…' : 'Create Account →'}
            </button>
          </form>

          <div className="auth-link">
            Already have an account? <Link to="/login">Sign in</Link>
          </div>
        </div>
      </div>
    </div>
  );
}