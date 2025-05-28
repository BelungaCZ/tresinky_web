import React, { useState, useEffect } from 'react';
import { Modal } from 'react-bootstrap';
import Masonry from 'react-masonry-css';

const Gallery = () => {
  const [folders, setFolders] = useState([]);
  const [selectedFolder, setSelectedFolder] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    // Fetch folders and their cover images
    const fetchFolders = async () => {
      try {
        const response = await fetch('/api/gallery/folders');
        const data = await response.json();
        setFolders(data);
      } catch (error) {
        console.error('Error fetching folders:', error);
      }
    };

    fetchFolders();
  }, []);

  const handleFolderClick = (folder) => {
    setSelectedFolder(folder);
    setShowModal(true);
  };

  const breakpointColumns = {
    default: 4,
    1100: 3,
    700: 2,
    500: 1
  };

  return (
    <div className="container py-5">
      <h2 className="text-center mb-4">Galerie fotografií</h2>
      <Masonry
        breakpointCols={breakpointColumns}
        className="masonry-grid"
        columnClassName="masonry-grid_column"
      >
        {folders.map((folder) => (
          <div
            key={folder.name}
            className="folder-card mb-4"
            onClick={() => handleFolderClick(folder)}
          >
            <div className="folder-cover">
              <img
                src={folder.coverImage}
                alt={folder.name}
                className="img-fluid rounded"
              />
              <div className="folder-name">
                <h3>{folder.name}</h3>
              </div>
            </div>
          </div>
        ))}
      </Masonry>

      <Modal
        show={showModal}
        onHide={() => setShowModal(false)}
        size="xl"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>{selectedFolder?.name}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedFolder && (
            <Masonry
              breakpointCols={breakpointColumns}
              className="masonry-grid"
              columnClassName="masonry-grid_column"
            >
              {selectedFolder.images.map((image, index) => (
                <div key={index} className="mb-4">
                  <img
                    src={image}
                    alt={`${selectedFolder.name} - ${index + 1}`}
                    className="img-fluid rounded"
                  />
                </div>
              ))}
            </Masonry>
          )}
        </Modal.Body>
      </Modal>

      <style jsx>{`
        .masonry-grid {
          display: flex;
          margin-left: -30px;
          width: auto;
        }
        .masonry-grid_column {
          padding-left: 30px;
          background-clip: padding-box;
        }
        .folder-card {
          cursor: pointer;
          transition: transform 0.2s;
        }
        .folder-card:hover {
          transform: scale(1.02);
        }
        .folder-cover {
          position: relative;
          overflow: hidden;
        }
        .folder-name {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          background: rgba(0, 0, 0, 0.7);
          color: white;
          padding: 10px;
        }
        .folder-name h3 {
          margin: 0;
          font-size: 1.2rem;
        }
      `}</style>
    </div>
  );
};

export default Gallery; 