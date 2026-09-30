import React, { useState } from 'react';
import { usePWAInstall } from '../hooks/usePWAInstall';
import { Download, Share, PlusSquare, X } from 'lucide-react';

export const PWAInstallPrompt: React.FC = () => {
  const { canInstall, isInstalled, isIOS, installApp } = usePWAInstall();
  const [showIOSModal, setShowIOSModal] = useState(false);

  if (isInstalled || !canInstall) return null;

  const handleInstallClick = () => {
    if (isIOS) {
      setShowIOSModal(true);
    } else {
      installApp();
    }
  };

  return (
    <>
      <button
        type="button"
        className="mobile-install-btn"
        onClick={handleInstallClick}
        aria-label="Install mobile app"
      >
        <Download size={14} className="icon-pulse" />
        <span>Install App</span>
      </button>

      {showIOSModal && (
        <div className="ios-modal-backdrop" onClick={() => setShowIOSModal(false)}>
          <div className="ios-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="ios-modal-header">
              <h3>Install on iPhone / iPad</h3>
              <button
                type="button"
                className="ios-modal-close"
                onClick={() => setShowIOSModal(false)}
                aria-label="Close"
              >
                <X size={18} />
              </button>
            </div>
            <p className="ios-modal-desc">
              Install <strong>Sponsor Atlas</strong> to your home screen for full-screen immersive exploration:
            </p>
            <ol className="ios-steps">
              <li>
                Tap the <Share size={15} className="inline-icon" /> <strong>Share</strong> button in Safari toolbar.
              </li>
              <li>
                Scroll down and tap <PlusSquare size={15} className="inline-icon" /> <strong>Add to Home Screen</strong>.
              </li>
              <li>
                Tap <strong>Add</strong> in the top right corner.
              </li>
            </ol>
          </div>
        </div>
      )}
    </>
  );
};
