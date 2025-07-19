
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Upload, FileText, X, Loader2 } from 'lucide-react';
import { useNutritionStore } from '@/store/nutritionStore';
import { toastSuccess, toastError } from '@/components/ui/enhanced-toast';
import { cn } from '@/lib/utils';

export const PDFUpload: React.FC = () => {
  const { setCurrentPlan, setUploading, setUploadProgress, isUploading } = useNutritionStore();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
    } else {
      toastError('Please upload a valid PDF file');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const processPDF = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadProgress(0);

    try {
      // Simulate PDF processing
      for (let i = 0; i <= 100; i += 10) {
        setUploadProgress(i);
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      // Extract content (this would normally use a PDF parsing library)
      const mockContent = `
        PLAN NUTRICIONAL - 30 DÍAS
        
        DESAYUNO (400 cal):
        - 2 huevos revueltos
        - 1 tostada integral
        - 1/2 aguacate
        
        ALMUERZO (600 cal):
        - 150g pollo a la plancha
        - 1 taza arroz integral
        - Ensalada mixta
        
        CENA (500 cal):
        - 120g salmón
        - Verduras al vapor
        - 1 batata pequeña
        
        SNACKS (300 cal):
        - 1 manzana con almendras
        - Yogur griego
      `;

      const newPlan = {
        id: Date.now().toString(),
        name: selectedFile.name.replace('.pdf', ''),
        file: selectedFile,
        content: mockContent,
        uploadDate: new Date(),
        duration: 30,
        macros: {
          calories: 1800,
          protein: 120,
          carbs: 180,
          fat: 70
        },
        meals: [
          {
            id: '1',
            name: 'Desayuno',
            time: '08:00',
            calories: 400,
            ingredients: ['2 huevos', '1 tostada integral', '1/2 aguacate']
          },
          {
            id: '2',
            name: 'Almuerzo',
            time: '13:00',
            calories: 600,
            ingredients: ['150g pollo', '1 taza arroz integral', 'ensalada mixta']
          },
          {
            id: '3',
            name: 'Cena',
            time: '19:00',
            calories: 500,
            ingredients: ['120g salmón', 'verduras al vapor', '1 batata']
          }
        ]
      };

      setCurrentPlan(newPlan);
      setSelectedFile(null);
      toastSuccess('Plan nutricional cargado exitosamente');
    } catch (error) {
      toastError('Error al procesar el PDF');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <Card className="glass-ultra border-white/10 bg-white/5">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Upload className="w-5 h-5" />
          Cargar Plan Nutricional
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {!selectedFile ? (
          <div
            {...getRootProps()}
            className={cn(
              "border-2 border-dashed border-white/20 rounded-lg p-8 text-center cursor-pointer transition-colors",
              isDragActive ? "border-blue-400 bg-blue-400/10" : "hover:border-white/40"
            )}
          >
            <input {...getInputProps()} />
            <FileText className="w-12 h-12 text-white/60 mx-auto mb-4" />
            <p className="text-white/80 mb-2">
              {isDragActive ? "Suelta el archivo aquí" : "Arrastra tu plan nutricional en PDF"}
            </p>
            <p className="text-white/60 text-sm">o haz clic para seleccionar (máx. 10MB)</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
              <div className="flex items-center gap-3">
                <FileText className="w-8 h-8 text-green-400" />
                <div>
                  <p className="text-white font-medium">{selectedFile.name}</p>
                  <p className="text-white/60 text-sm">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSelectedFile(null)}
                className="text-white/60 hover:text-white"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
            
            <Button
              onClick={processPDF}
              disabled={isUploading}
              className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Procesando... {Math.round(useNutritionStore.getState().uploadProgress)}%
                </>
              ) : (
                'Procesar Plan Nutricional'
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
