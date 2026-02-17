import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider, ToastContext } from './contexts/ToastContext';
import { ModalProvider, ModalContext } from './contexts/ModalContext';
import { ProtectedRoute } from './components/shared/ProtectedRoute';
import ProtectedAdminRoute from './components/shared/ProtectedAdminRoute';
import ProtectedAuthorRoute from './components/shared/ProtectedAuthorRoute';
import ProtectedEditorRoute from './components/shared/ProtectedEditorRoute';
import ProtectedReviewerRoute from './components/shared/ProtectedReviewerRoute';
import Header from './components/header/Header';
import Footer from './components/footer/Footer';
import ToastContainer from './components/toast/ToastContainer';
import Modal from './components/modal/Modal';
import { JournalsPage } from './pages/JournalsPage/JournalsPage';
import JournalDetailPage from './pages/JournalDetailPage/JournalDetailPage';
import { LoginPage } from './pages/LoginPage/LoginPage';
import { SignupPage } from './pages/SignupPage/SignupPage';
import { DashboardPage } from './pages/DashboardPage/DashboardPage';
import { SubmitPage } from './pages/SubmitPage/SubmitPage';
import InvitationPage from './pages/InvitationPage/InvitationPage';
// Admin layouts and pages
import AdminLayout from './layouts/AdminLayout/AdminLayout.jsx';
import AdminDashboard from './pages/AdminDashboard/AdminDashboard.jsx';
import AdminUsers from './pages/AdminUsers/AdminUsers.jsx';
import AdminJournals from './pages/AdminJournals/AdminJournals.jsx';
import AdminSubmissions from './pages/AdminSubmissions/AdminSubmissions.jsx';
import AdminSettings from './pages/AdminSettings/AdminSettings.jsx';
// Author layouts and pages
import AuthorLayout from './layouts/AuthorLayout/AuthorLayout.jsx';
import AuthorDashboard from './pages/AuthorDashboard/AuthorDashboard.jsx';
import AuthorSubmissions from './pages/AuthorSubmissions/AuthorSubmissions.jsx';
// Editor layouts and pages
import EditorLayout from './layouts/EditorLayout/EditorLayout.jsx';
import EditorDashboard from './pages/EditorDashboard/EditorDashboard.jsx';
import EditorPaperQueue from './pages/EditorPaperQueue/EditorPaperQueue.jsx';
import EditorPendingDecision from './pages/EditorPendingDecision/EditorPendingDecision.jsx';
import EditorReviewerList from './pages/EditorReviewerList/EditorReviewerList.jsx';
// Reviewer layouts and pages
import ReviewerLayout from './layouts/ReviewerLayout/ReviewerLayout.jsx';
import ReviewerDashboard from './pages/ReviewerDashboard/ReviewerDashboard.jsx';
import ReviewerAssignments from './pages/ReviewerAssignments/ReviewerAssignments.jsx';
import ReviewerInvitations from './pages/ReviewerInvitations/ReviewerInvitations.jsx';
import ReviewerProfile from './pages/ReviewerProfile/ReviewerProfile.jsx';
import ReviewerHistory from './pages/ReviewerHistory/ReviewerHistory.jsx';
import ReviewerGuidelines from './pages/ReviewerGuidelines/ReviewerGuidelines.jsx';
import ReviewPage from './pages/ReviewPage/ReviewPage.jsx';
// Editor Decision Panel
import EditorDecisionPanel from './components/EditorDecisionPanel.jsx';
// Paper Details Page
import PaperDetailsPage from './pages/PaperDetailsPage/PaperDetailsPage.jsx';

function App() {
  return (
    <Router>
      <AuthProvider>
        <ToastProvider>
          <ModalProvider>
            <AppContent />
          </ModalProvider>
        </ToastProvider>
      </AuthProvider>
    </Router>
  );
}

function AppContent() {
  const { toasts, removeToast } = React.useContext(ToastContext);
  const { isOpen, title, message, confirmText, cancelText, type, onConfirm, onCancel, closeModal } = React.useContext(ModalContext);

  const handleModalConfirm = () => {
    if (onConfirm) onConfirm();
    closeModal();
  };

  const handleModalCancel = () => {
    if (onCancel) onCancel();
    closeModal();
  };

  return (
    <div className="App">
      <Header />
      <main className="app-main">
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<DashboardPage />} />
          <Route path="/journals" element={<JournalsPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />

          {/* Protected routes */}
          <Route path="/journal/:id" element={<ProtectedRoute><JournalDetailPage /></ProtectedRoute>} />
          <Route path="/paper/:id" element={<ProtectedRoute><PaperDetailsPage /></ProtectedRoute>} />
          <Route path="/submit" element={<ProtectedRoute><SubmitPage /></ProtectedRoute>} />
          <Route path="/invitations/:token" element={<ProtectedRoute><InvitationPage /></ProtectedRoute>} />

          {/* Admin routes */}
          <Route path="/admin/*" element={<ProtectedAdminRoute />}>
            <Route element={<AdminLayout />}>
              <Route path="" element={<AdminDashboard />} />
              <Route path="users" element={<AdminUsers />} />
              <Route path="journals" element={<AdminJournals />} />
              <Route path="submissions" element={<AdminSubmissions />} />
              <Route path="submissions/:id" element={<PaperDetailsPage />} />
              <Route path="settings" element={<AdminSettings />} />
            </Route>
          </Route>

          {/* Author routes */}
          <Route path="/author/*" element={<ProtectedAuthorRoute />}>
            <Route element={<AuthorLayout />}>
              <Route path="" element={<AuthorDashboard />} />
              <Route path="submissions" element={<AuthorSubmissions />} />
              <Route path="submissions/:id" element={<PaperDetailsPage />} />
            </Route>
          </Route>

          {/* Editor routes */}
          <Route path="/editor/*" element={<ProtectedEditorRoute />}>
            <Route element={<EditorLayout />}>
              <Route path="dashboard" element={<EditorDashboard />} />
              <Route path="" element={<EditorDashboard />} />
              <Route path="papers" element={<EditorPaperQueue />} />
              <Route path="papers/pending-decision" element={<EditorPendingDecision />} />
              <Route path="papers/:id" element={<PaperDetailsPage />} />
              <Route path="papers/:paperId/decision" element={<EditorDecisionPanel />} />
              <Route path="reviewers" element={<EditorReviewerList />} />
            </Route>
          </Route>

          {/* Reviewer routes */}
          <Route path="/reviewer/*" element={<ProtectedReviewerRoute />}>
            <Route element={<ReviewerLayout />}>
              <Route path="dashboard" element={<ReviewerDashboard />} />
              <Route path="" element={<ReviewerDashboard />} />
              <Route path="assignments" element={<ReviewerAssignments />} />
              <Route path="assignments/:id" element={<PaperDetailsPage />} />
              <Route path="assignments/:id/review" element={<ReviewPage />} />
              <Route path="invitations" element={<ReviewerInvitations />} />
              <Route path="history" element={<ReviewerHistory />} />
              <Route path="profile" element={<ReviewerProfile />} />
              <Route path="guidelines" element={<ReviewerGuidelines />} />
            </Route>
          </Route>

          {/* Protected routes */}
          <Route
            path="/home"
            element={<Navigate to="/" replace />}
          />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <ToastContainer toasts={toasts} onRemoveToast={removeToast} />
      <Modal
        isOpen={isOpen}
        title={title}
        message={message}
        confirmText={confirmText}
        cancelText={cancelText}
        type={type}
        onConfirm={handleModalConfirm}
        onCancel={handleModalCancel}
      />
    </div>
  );
}

export default App;
