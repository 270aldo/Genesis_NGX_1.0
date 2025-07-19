import React, { useState, useCallback, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { X, FileText, Image, Upload, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { FileAttachment as FileAttachmentType } from '@/store/chatStore';
import { useImageCompression } from '@/hooks/useImageCompression';
interface FileAttachmentProps {
  files: FileAttachmentType[];
  onFilesAdded: (files: FileAttachmentType[]) => void;
  onFileRemoved: (fileId: string) => void;
  disabled?: boolean;
}

interface FileProgress {
  id: string;
  progress: number;
  status: 'uploading' | 'processing' | 'success' | 'error';
}
const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25MB
const ACCEPTED_FILE_TYPES = {
  'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
  'application/pdf': ['.pdf'],
  'application/msword': ['.doc'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'text/plain': ['.txt']
};
export const FileAttachmentComponent: React.FC<FileAttachmentProps> = ({
  files,
  onFilesAdded,
  onFileRemoved,
  disabled
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [fileProgress, setFileProgress] = useState<FileProgress[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { compressImage } = useImageCompression();
  const processFiles = useCallback(async (acceptedFiles: File[]) => {
    setIsProcessing(true);
    
    const processPromises = acceptedFiles.map(async (file, index) => {
      const id = Date.now().toString() + Math.random() + index;
      
      // Initialize progress
      setFileProgress(prev => [...prev, { id, progress: 0, status: 'uploading' }]);
      
      // Simulate upload progress
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 50));
        setFileProgress(prev => 
          prev.map(p => p.id === id ? { ...p, progress } : p)
        );
      }
      
      // Process image compression if needed
      setFileProgress(prev => 
        prev.map(p => p.id === id ? { ...p, status: 'processing' } : p)
      );
      
      let processedFile = file;
      if (file.type.startsWith('image/') && file.size > 2 * 1024 * 1024) {
        try {
          processedFile = await compressImage(file);
        } catch (error) {
          console.warn('Image compression failed, using original:', error);
        }
      }
      
      const url = URL.createObjectURL(processedFile);
      let preview = url;
      if (processedFile.type.startsWith('image/')) {
        preview = url;
      }
      
      setFileProgress(prev => 
        prev.map(p => p.id === id ? { ...p, status: 'success' } : p)
      );
      
      return {
        id,
        name: processedFile.name,
        type: processedFile.type,
        size: processedFile.size,
        url,
        preview
      };
    });
    
    try {
      const newFiles = await Promise.all(processPromises);
      onFilesAdded(newFiles);
    } catch (error) {
      console.error('Error processing files:', error);
    } finally {
      // Clear progress after a delay
      setTimeout(() => {
        setFileProgress([]);
        setIsProcessing(false);
      }, 1000);
    }
  }, [onFilesAdded, compressImage]);
  const {
    getRootProps,
    getInputProps
  } = useDropzone({
    onDrop: processFiles,
    onDragEnter: () => setIsDragOver(true),
    onDragLeave: () => setIsDragOver(false),
    accept: ACCEPTED_FILE_TYPES,
    maxSize: MAX_FILE_SIZE,
    maxFiles: 5,
    disabled: disabled || isProcessing,
    noClick: true
  });
  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <Image className="w-4 h-4" />;
    return <FileText className="w-4 h-4" />;
  };
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };
  return <div className="w-full">
      {/* File Upload Area */}
      <div 
        {...getRootProps()} 
        className={cn(
          "relative transition-all duration-200", 
          isDragOver && "bg-violet-900/20 rounded-lg",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500"
        )}
        role="region"
        aria-label="File upload area"
      >
        <input 
          {...getInputProps()} 
          ref={fileInputRef}
          aria-label="File input"
        />
        
        {isDragOver && (
          <div className="absolute inset-0 border-2 border-dashed border-violet-500 rounded-lg bg-violet-900/10 flex items-center justify-center z-10 animate-fade-in">
            <div className="text-center">
              <Upload className="w-6 h-6 text-violet-400 mx-auto mb-2" />
              <p className="text-sm text-violet-300">Drop files here</p>
            </div>
          </div>
        )}

        {/* Processing Indicator */}
        {isProcessing && (
          <div className="flex items-center gap-2 p-2 bg-violet-900/20 rounded-lg mb-2">
            <Loader2 className="w-4 h-4 text-violet-400 animate-spin" />
            <span className="text-sm text-violet-300">Processing files...</span>
          </div>
        )}

        {/* File Progress */}
        {fileProgress.length > 0 && (
          <div className="space-y-2 p-2 bg-black/20 rounded-lg mb-2">
            {fileProgress.map((progress) => (
              <div key={progress.id} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-violet-300">
                    {progress.status === 'uploading' ? 'Uploading...' : 
                     progress.status === 'processing' ? 'Processing...' : 
                     progress.status === 'success' ? 'Complete' : 'Error'}
                  </span>
                  <span className="text-violet-400">{progress.progress}%</span>
                </div>
                <div className="w-full bg-violet-900/30 rounded-full h-1.5">
                  <div 
                    className="bg-gradient-to-r from-violet-500 to-violet-400 h-1.5 rounded-full transition-all duration-300 relative overflow-hidden"
                    style={{ width: `${progress.progress}%` }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-[upload-progress_2s_infinite]" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* File Previews */}
        {files.length > 0 && (
          <div className="flex flex-wrap gap-2 p-2 border-t border-violet-800">
            {files.map((file, index) => (
              <div 
                key={file.id} 
                className="relative group bg-black/50 border border-violet-700 rounded-lg p-2 flex items-center gap-2 max-w-xs hover:border-violet-500 transition-all duration-200 animate-[stagger-fade-in_0.3s_ease-out] touch-manipulation"
                style={{ animationDelay: `${index * 100}ms` }}
                role="article"
                aria-label={`Attached file: ${file.name}`}
              >
                {file.type.startsWith('image/') ? (
                  <div className="flex-shrink-0">
                    <img 
                      src={file.preview} 
                      alt={`Preview of ${file.name}`} 
                      className="w-8 h-8 object-cover rounded"
                      loading="lazy"
                    />
                  </div>
                ) : (
                  <div className="flex-shrink-0 text-violet-400" aria-hidden="true">
                    {getFileIcon(file.type)}
                  </div>
                )}
                
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-white truncate" title={file.name}>{file.name}</p>
                  <p className="text-xs text-gray-400">{formatFileSize(file.size)}</p>
                </div>
                
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => onFileRemoved(file.id)} 
                  className="h-8 w-8 p-0 text-gray-400 hover:text-white hover:bg-red-500/20 opacity-0 group-hover:opacity-100 transition-all duration-200 touch-manipulation"
                  aria-label={`Remove ${file.name}`}
                  tabIndex={0}
                >
                  <X className="w-3 h-3" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Hidden file input for programmatic access */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={(e) => {
          const files = Array.from(e.target.files || []);
          if (files.length > 0) {
            processFiles(files);
          }
        }}
        multiple
        accept={Object.keys(ACCEPTED_FILE_TYPES).join(',')}
        className="hidden"
        disabled={disabled || isProcessing}
      />
    </div>;
};