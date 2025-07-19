
import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { FileText, Upload, X, CheckCircle } from 'lucide-react';
import { useTrainingStore } from '@/store/trainingStore';

export const PDFUpload: React.FC = () => {
  const { isUploading, uploadProgress, setCurrentPlan, setUploading, setUploadProgress } = useTrainingStore();
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const onDrop = async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploadedFile(file);
    setUploading(true);
    setUploadProgress(0);

    // Simulate upload progress
    for (let i = 0; i <= 100; i += 10) {
      await new Promise(resolve => setTimeout(resolve, 100));
      setUploadProgress(i);
    }

    // Create a mock training plan from the PDF
    const mockPlan = {
      id: Date.now().toString(),
      name: file.name.replace('.pdf', ''),
      file: file,
      content: 'PDF content parsed...',
      uploadDate: new Date(),
      duration: 12, // weeks
      workoutDays: [
        {
          id: '1',
          name: 'Day 1 - Push',
          exercises: [
            { id: '1', name: 'Bench Press', sets: 4, reps: '8-10', weight: '80kg' },
            { id: '2', name: 'Overhead Press', sets: 3, reps: '10-12', weight: '50kg' },
            { id: '3', name: 'Incline Dumbbell Press', sets: 3, reps: '12-15', weight: '30kg' }
          ]
        },
        {
          id: '2',
          name: 'Day 2 - Pull',
          exercises: [
            { id: '4', name: 'Deadlift', sets: 4, reps: '6-8', weight: '120kg' },
            { id: '5', name: 'Pull-ups', sets: 3, reps: '8-12', weight: 'Bodyweight' },
            { id: '6', name: 'Barbell Rows', sets: 3, reps: '10-12', weight: '70kg' }
          ]
        },
        {
          id: '3',
          name: 'Day 3 - Legs',
          exercises: [
            { id: '7', name: 'Squats', sets: 4, reps: '8-10', weight: '100kg' },
            { id: '8', name: 'Romanian Deadlift', sets: 3, reps: '10-12', weight: '80kg' },
            { id: '9', name: 'Leg Press', sets: 3, reps: '15-20', weight: '200kg' }
          ]
        }
      ],
      totalWorkouts: 36,
      completedWorkouts: 0
    };

    setCurrentPlan(mockPlan);
    setUploading(false);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1
  });

  const removeFile = () => {
    setUploadedFile(null);
  };

  return (
    <Card className="glass-ultra border-white/10 bg-white/5">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Upload Training Plan
        </CardTitle>
      </CardHeader>
      <CardContent>
        {!uploadedFile ? (
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-blue-500 bg-blue-500/10'
                : 'border-white/20 hover:border-white/40'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="h-12 w-12 text-white/40 mx-auto mb-4" />
            {isDragActive ? (
              <p className="text-white/80">Drop your training plan PDF here...</p>
            ) : (
              <div>
                <p className="text-white/80 mb-2">
                  Drag & drop your training plan PDF here, or click to select
                </p>
                <p className="text-white/40 text-sm">
                  Supports PDF files up to 10MB
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10">
              <div className="flex items-center gap-3">
                <FileText className="h-8 w-8 text-blue-400" />
                <div>
                  <p className="text-white font-medium">{uploadedFile.name}</p>
                  <p className="text-white/60 text-sm">
                    {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              {!isUploading && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={removeFile}
                  className="text-white/60 hover:text-white hover:bg-white/10"
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
              {isUploading && uploadProgress === 100 && (
                <CheckCircle className="h-5 w-5 text-green-400" />
              )}
            </div>

            {isUploading && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-white/60">Processing...</span>
                  <span className="text-white/60">{uploadProgress}%</span>
                </div>
                <Progress value={uploadProgress} className="h-2" />
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
