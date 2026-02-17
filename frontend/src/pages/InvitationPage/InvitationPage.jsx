import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import acsApi from '../../api/apiService.js';
import Header from '../../components/header/Header';
import Footer from '../../components/footer/Footer';
import './InvitationPage.css';

const InvitationPage = () => {
  const { token } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [invitation, setInvitation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [showDeclineReason, setShowDeclineReason] = useState(false);
  const [declineReason, setDeclineReason] = useState('');
  const [successMessage, setSuccessMessage] = useState(null);

  useEffect(() => {
    // Auto-redirect if user is already logged in
    const authToken = localStorage.getItem('authToken');
    if (authToken && location.pathname.includes('/invitations/')) {
      // Allow viewing invitation even if logged in
      // (in case logged-in user wants to accept on behalf of org)
    }
    
    loadInvitation();
  }, [token]);

  const loadInvitation = async () => {
    if (!token) {
      setError('No invitation token provided. Please check your email for the invitation link.');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const data = await acsApi.invitations.getInvitationStatus(token);
      setInvitation(data);
      
      // Check if token is expired
      if (data.is_expired) {
        setError('This invitation has expired. Please contact the editor to request a new invitation.');
      }
    } catch (err) {
      console.error('Failed to load invitation:', err);
      if (err.response?.status === 404) {
        setError('Invitation not found. The token may be invalid or expired.');
      } else if (err.response?.status === 410) {
        setError('This invitation has expired. Please contact the editor to request a new invitation.');
      } else {
        setError('Failed to load invitation details. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async () => {
    if (processing || !token) return;

    try {
      setProcessing(true);
      setError(null);
      
      const response = await acsApi.invitations.acceptInvitation(token);
      
      setSuccessMessage(
        `Thank you! You have accepted the review invitation for "${invitation.paper_title}". ` +
        `Your review is due on ${new Date(response.accepted_on).toLocaleDateString()}.`
      );
      
      // Redirect after 3 seconds
      setTimeout(() => {
        // Redirect to reviewer dashboard or home
        const authToken = localStorage.getItem('authToken');
        if (authToken) {
          navigate('/reviewer-dashboard');
        } else {
          navigate('/');
        }
      }, 3000);
    } catch (err) {
      console.error('Failed to accept invitation:', err);
      if (err.response?.status === 410) {
        setError('This invitation has expired.');
      } else if (err.response?.status === 409) {
        setError(err.response.data?.detail || 'You are already assigned as a reviewer for this paper. Duplicate assignments are not allowed.');
      } else if (err.response?.status === 400) {
        setError(err.response.data?.detail || 'Unable to accept invitation. It may have already been accepted or declined.');
      } else {
        setError('Failed to accept invitation. Please try again later.');
      }
    } finally {
      setProcessing(false);
    }
  };

  const handleDecline = async () => {
    if (processing || !token) return;

    try {
      setProcessing(true);
      setError(null);
      
      const response = await acsApi.invitations.declineInvitation(token, declineReason);
      
      setSuccessMessage(
        `You have declined the review invitation for "${invitation.paper_title}". ` +
        `The editor has been notified.`
      );
      
      // Redirect after 3 seconds
      setTimeout(() => {
        navigate('/');
      }, 3000);
    } catch (err) {
      console.error('Failed to decline invitation:', err);
      if (err.response?.status === 410) {
        setError('This invitation has expired.');
      } else if (err.response?.status === 400) {
        setError(err.response.data?.detail || 'Unable to decline invitation.');
      } else {
        setError('Failed to decline invitation. Please try again later.');
      }
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="invitation-page">
      <Header />
      
      <main className="invitation-container">
        <div className="invitation-content">
          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading invitation details...</p>
            </div>
          ) : successMessage ? (
            <div className="success-state">
              <div className="success-icon">✓</div>
              <h2>Success!</h2>
              <p>{successMessage}</p>
              <p className="redirect-message">Redirecting in 3 seconds...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <div className="error-icon">⚠</div>
              <h2>Invitation Issue</h2>
              <p>{error}</p>
              <button 
                className="button button-secondary"
                onClick={() => navigate('/')}
              >
                Return to Home
              </button>
            </div>
          ) : invitation ? (
            <div className="invitation-card">
              <div className="invitation-header">
                <h1>Review Invitation</h1>
                <div className="status-badge">
                  {invitation.is_expired ? 'Expired' : 'Active'}
                </div>
              </div>

              <div className="invitation-details">
                <div className="detail-section">
                  <h3>Paper Details</h3>
                  <div className="detail-item">
                    <label>Title:</label>
                    <p className="paper-title">{invitation.paper_title}</p>
                  </div>
                </div>

                <div className="detail-section">
                  <h3>Review Information</h3>
                  <div className="detail-item">
                    <label>Reviewer:</label>
                    <p>{invitation.reviewer_name}</p>
                  </div>
                  <div className="detail-item">
                    <label>Due Date:</label>
                    <p>
                      {new Date(invitation.due_date).toLocaleDateString()} 
                      {invitation.days_remaining > 0 && (
                        <span className="days-remaining">
                          ({invitation.days_remaining} days remaining)
                        </span>
                      )}
                    </p>
                  </div>
                  <div className="detail-item">
                    <label>Status:</label>
                    <p className="status-text">{invitation.status.charAt(0).toUpperCase() + invitation.status.slice(1)}</p>
                  </div>
                </div>

                {!invitation.is_expired && invitation.status === 'pending' && (
                  <div className="action-section">
                    <h3>Your Response</h3>
                    <p className="instruction-text">
                      Please indicate whether you can provide a peer review for this paper.
                    </p>

                    <div className="button-group">
                      <button 
                        className="button button-primary"
                        onClick={handleAccept}
                        disabled={processing}
                      >
                        {processing ? 'Processing...' : 'Accept Review Invitation'}
                      </button>

                      {!showDeclineReason ? (
                        <button 
                          className="button button-secondary"
                          onClick={() => setShowDeclineReason(true)}
                          disabled={processing}
                        >
                          Decline
                        </button>
                      ) : (
                        <div className="decline-reason-box">
                          <label htmlFor="decline-reason">Why are you declining? (optional)</label>
                          <textarea
                            id="decline-reason"
                            className="decline-reason-input"
                            placeholder="Please let us know if there's a specific reason..."
                            value={declineReason}
                            onChange={(e) => setDeclineReason(e.target.value)}
                            maxLength={500}
                            rows={4}
                          />
                          <div className="decline-button-group">
                            <button 
                              className="button button-danger"
                              onClick={handleDecline}
                              disabled={processing}
                            >
                              {processing ? 'Processing...' : 'Confirm Decline'}
                            </button>
                            <button 
                              className="button button-outline"
                              onClick={() => {
                                setShowDeclineReason(false);
                                setDeclineReason('');
                              }}
                              disabled={processing}
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {invitation.is_expired && (
                  <div className="expired-notice">
                    <p>
                      <strong>This invitation has expired.</strong> If you're still interested in reviewing this paper, 
                      please contact the editor directly.
                    </p>
                  </div>
                )}

                {invitation.status === 'accepted' && (
                  <div className="already-accepted-notice">
                    <p>
                      <strong>You have already accepted this invitation.</strong> 
                      You can now log in to access the paper and submit your review.
                    </p>
                  </div>
                )}

                {invitation.status === 'declined' && (
                  <div className="already-declined-notice">
                    <p>
                      <strong>You have already declined this invitation.</strong> 
                      If you would like to change your response, please contact the editor.
                    </p>
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default InvitationPage;
