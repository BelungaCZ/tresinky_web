import fs from 'fs';
import path from 'path';
import { promisify } from 'util';

const readdir = promisify(fs.readdir);
const stat = promisify(fs.stat);

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const uploadsDir = path.join(process.cwd(), 'static', 'uploads');
    const folders = await readdir(uploadsDir);

    const folderData = await Promise.all(
      folders
        .filter(folder => !folder.startsWith('.')) // Skip hidden folders
        .map(async (folder) => {
          const folderPath = path.join(uploadsDir, folder);
          const stats = await stat(folderPath);

          if (stats.isDirectory()) {
            const files = await readdir(folderPath);
            const images = files
              .filter(file => {
                const ext = path.extname(file).toLowerCase();
                return ['.jpg', '.jpeg', '.png', '.gif'].includes(ext);
              })
              .map(file => `/uploads/${folder}/${file}`);

            // Sort images by file size to get the highest quality one as cover
            const imageStats = await Promise.all(
              images.map(async (image) => {
                const imagePath = path.join(process.cwd(), 'static', image);
                const imageStat = await stat(imagePath);
                return { path: image, size: imageStat.size };
              })
            );

            imageStats.sort((a, b) => b.size - a.size);
            const coverImage = imageStats[0]?.path || '';

            return {
              name: folder,
              coverImage,
              images
            };
          }
          return null;
        })
    );

    const validFolders = folderData.filter(folder => folder !== null);
    res.status(200).json(validFolders);
  } catch (error) {
    console.error('Error reading folders:', error);
    res.status(500).json({ message: 'Error reading folders' });
  }
} 