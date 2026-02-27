import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer-wrapper">
      <div className="footer-container">
        <div className="footer-content">
          {/* Branding Column */}
          <div className="footer-branding">
            <span className="footer-logo-text">Breakthrough Publishers</span>
            <p className="footer-description">
              Dedicated to the global advancement of combinatorial sciences through rigorous peer-reviewed research and scholarly excellence.
            </p>
          </div>

          {/* Quick Links Column */}
          <div className="footer-section">
            <h5 className="footer-section-title">Quick Links</h5>
            <ul className="footer-links">
              <li><Link to="/journals" className="footer-link">Publishing Policy</Link></li>
              <li><Link to="/submit" className="footer-link">Author Guidelines</Link></li>
              <li><Link to="/journals" className="footer-link">Editorial Board</Link></li>
              <li><a href="#ethics" className="footer-link">Ethics & Malpractice</a></li>
            </ul>
          </div>

          {/* Contact Column */}
          <div className="footer-section">
            <h5 className="footer-section-title">Contact</h5>
            <ul className="footer-links">
              <li className="footer-contact-item">
                <span className="material-icons">email</span>
                <span>editorial@breakthroughpublishers.org</span>
              </li>
              <li className="footer-contact-item">
                <span className="material-icons">location_on</span>
                <span>123 Academic Way, Science City</span>
              </li>
              <li className="footer-contact-item">
                <span className="material-icons">phone</span>
                <span>+1 (555) 123-4567</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="footer-bottom">
          <p>© 2024 Breakthrough Publishers. All rights reserved.</p>
          <div className="footer-bottom-links">
            <a href="#privacy" className="footer-bottom-link">Privacy Policy</a>
            <a href="#terms" className="footer-bottom-link">Terms of Service</a>
            <a href="#cookies" className="footer-bottom-link">Cookie Policy</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;