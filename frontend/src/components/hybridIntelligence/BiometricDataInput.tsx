/**
 * Biometric Data Input Component
 * Layer 2 of Hybrid Intelligence: Physiological Modulation
 * Collects real-time bio-data for personalization
 */

import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import { useHybridIntelligenceStore } from '@/store/hybridIntelligenceStore';
import { 
  type UserBiometrics, 
  type BiomarkerData 
} from '@/services/api/hybridIntelligence.service';
import { 
  Activity, 
  Heart, 
  Moon, 
  Zap, 
  Shield, 
  Brain,
  RotateCcw,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Upload,
  Smartphone,
  Watch
} from 'lucide-react';

interface BiometricDataInputProps {
  onComplete?: () => void;
  className?: string;
}

export const BiometricDataInput: React.FC<BiometricDataInputProps> = ({
  onComplete,
  className
}) => {
  const [biometrics, setBiometrics] = useState<UserBiometrics>({
    sleep_quality: undefined,
    sleep_duration: undefined,
    stress_level: undefined,
    energy_level: undefined,
    recovery_status: undefined,
    heart_rate_variability: undefined,
    resting_heart_rate: undefined,
    readiness_score: undefined
  });

  const [biomarkers, setBiomarkers] = useState<BiomarkerData>({
    testosterone: undefined,
    cortisol: undefined,
    vitamin_d: undefined,
    b12: undefined,
    inflammation_markers: undefined,
    glucose: undefined
  });

  const [activeTab, setActiveTab] = useState('biometrics');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { 
    updateBiometrics, 
    updateBiomarkers, 
    currentBiometrics,
    biomarkers: currentBiomarkers,
    isLoading 
  } = useHybridIntelligenceStore();

  // Initialize with current data
  React.useEffect(() => {
    if (currentBiometrics) {
      setBiometrics(currentBiometrics);
    }
    if (currentBiomarkers) {
      setBiomarkers(currentBiomarkers);
    }
  }, [currentBiometrics, currentBiomarkers]);

  // Handle biometric data changes
  const handleBiometricChange = useCallback((key: keyof UserBiometrics, value: number) => {
    setBiometrics(prev => ({ ...prev, [key]: value }));
  }, []);

  // Handle biomarker data changes
  const handleBiomarkerChange = useCallback((key: keyof BiomarkerData, value: number) => {
    setBiomarkers(prev => ({ ...prev, [key]: value }));
  }, []);

  // Submit biometric data
  const handleSubmitBiometrics = useCallback(async () => {
    setIsSubmitting(true);
    try {
      // Filter out undefined values
      const validBiometrics = Object.entries(biometrics).reduce((acc, [key, value]) => {
        if (value !== undefined && value !== null) {
          acc[key as keyof UserBiometrics] = value;
        }
        return acc;
      }, {} as UserBiometrics);

      await updateBiometrics(validBiometrics);
      onComplete?.();
    } catch (error) {
      console.error('Failed to update biometrics:', error);
    } finally {
      setIsSubmitting(false);
    }
  }, [biometrics, updateBiometrics, onComplete]);

  // Submit biomarker data
  const handleSubmitBiomarkers = useCallback(async () => {
    setIsSubmitting(true);
    try {
      // Filter out undefined values
      const validBiomarkers = Object.entries(biomarkers).reduce((acc, [key, value]) => {
        if (value !== undefined && value !== null) {
          acc[key as keyof BiomarkerData] = value;
        }
        return acc;
      }, {} as BiomarkerData);

      await updateBiomarkers({
        ...validBiomarkers,
        last_updated: new Date().toISOString()
      });
      onComplete?.();
    } catch (error) {
      console.error('Failed to update biomarkers:', error);
    } finally {
      setIsSubmitting(false);
    }
  }, [biomarkers, updateBiomarkers, onComplete]);

  // Get quality indicator for biometric values
  const getBiometricQuality = (key: keyof UserBiometrics, value: number | undefined) => {
    if (value === undefined || value === null) return null;
    
    switch (key) {
      case 'sleep_quality':
        return value > 0.8 ? 'excellent' : value > 0.6 ? 'good' : value > 0.4 ? 'fair' : 'poor';
      case 'sleep_duration':
        return value >= 7 && value <= 9 ? 'excellent' : value >= 6 && value <= 10 ? 'good' : 'fair';
      case 'stress_level':
        return value < 0.3 ? 'excellent' : value < 0.5 ? 'good' : value < 0.7 ? 'fair' : 'poor';
      case 'energy_level':
        return value > 0.8 ? 'excellent' : value > 0.6 ? 'good' : value > 0.4 ? 'fair' : 'poor';
      case 'recovery_status':
        return value > 0.8 ? 'excellent' : value > 0.6 ? 'good' : value > 0.4 ? 'fair' : 'poor';
      case 'readiness_score':
        return value > 80 ? 'excellent' : value > 60 ? 'good' : value > 40 ? 'fair' : 'poor';
      default:
        return 'good';
    }
  };

  const getQualityColor = (quality: string | null) => {
    switch (quality) {
      case 'excellent': return 'text-green-600 bg-green-50 border-green-200';
      case 'good': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'fair': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'poor': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getCompletionPercentage = () => {
    const biometricFields = Object.values(biometrics).filter(v => v !== undefined && v !== null).length;
    const biomarkerFields = Object.values(biomarkers).filter(v => v !== undefined && v !== null).length;
    const totalFields = Object.keys(biometrics).length + Object.keys(biomarkers).length - 1; // -1 for last_updated
    return Math.round(((biometricFields + biomarkerFields) / totalFields) * 100);
  };

  return (
    <div className={cn("max-w-4xl mx-auto p-6", className)}>
      {/* Header */}
      <div className="text-center mb-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4"
        >
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
            Datos Biométricos
          </h1>
          <p className="text-gray-600 mt-2">
            Capa 2 del Hybrid Intelligence: Modulación Fisiológica en Tiempo Real
          </p>
        </motion.div>
        
        {/* Completion Status */}
        <div className="flex items-center justify-center gap-4 mb-4">
          <Badge variant="outline" className="text-sm">
            {getCompletionPercentage()}% completado
          </Badge>
          <div className="text-sm text-gray-500">
            Datos más precisos = Personalización más efectiva
          </div>
        </div>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="biometrics" className="flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Biométricos
          </TabsTrigger>
          <TabsTrigger value="biomarkers" className="flex items-center gap-2">
            <Brain className="w-4 h-4" />
            Biomarcadores
          </TabsTrigger>
        </TabsList>

        {/* Biometrics Tab */}
        <TabsContent value="biometrics" className="space-y-6">
          {/* Sleep Data */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Moon className="w-5 h-5 text-blue-500" />
                Datos de Sueño
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Sleep Quality */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <Label>Calidad del Sueño</Label>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">
                      {biometrics.sleep_quality ? Math.round(biometrics.sleep_quality * 100) + '%' : 'No establecido'}
                    </span>
                    {biometrics.sleep_quality && (
                      <Badge 
                        variant="outline" 
                        className={cn("text-xs", getQualityColor(getBiometricQuality('sleep_quality', biometrics.sleep_quality)))}
                      >
                        {getBiometricQuality('sleep_quality', biometrics.sleep_quality)}
                      </Badge>
                    )}
                  </div>
                </div>
                <Slider
                  value={[biometrics.sleep_quality ? biometrics.sleep_quality * 100 : 50]}
                  onValueChange={([value]) => handleBiometricChange('sleep_quality', value / 100)}
                  max={100}
                  step={5}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Muy malo (0%)</span>
                  <span>Excelente (100%)</span>
                </div>
              </div>

              {/* Sleep Duration */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <Label>Duración del Sueño (horas)</Label>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">
                      {biometrics.sleep_duration ? biometrics.sleep_duration.toFixed(1) + 'h' : 'No establecido'}
                    </span>
                    {biometrics.sleep_duration && (
                      <Badge 
                        variant="outline" 
                        className={cn("text-xs", getQualityColor(getBiometricQuality('sleep_duration', biometrics.sleep_duration)))}
                      >
                        {getBiometricQuality('sleep_duration', biometrics.sleep_duration)}
                      </Badge>
                    )}
                  </div>
                </div>
                <Slider
                  value={[biometrics.sleep_duration || 7]}
                  onValueChange={([value]) => handleBiometricChange('sleep_duration', value)}
                  min={3}
                  max={12}
                  step={0.5}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>3h</span>
                  <span>12h</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Energy & Stress */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-500" />
                Energía y Estrés
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Energy Level */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <Label>Nivel de Energía</Label>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">
                      {biometrics.energy_level ? Math.round(biometrics.energy_level * 100) + '%' : 'No establecido'}
                    </span>
                    {biometrics.energy_level && (
                      <Badge 
                        variant="outline" 
                        className={cn("text-xs", getQualityColor(getBiometricQuality('energy_level', biometrics.energy_level)))}
                      >
                        {getBiometricQuality('energy_level', biometrics.energy_level)}
                      </Badge>
                    )}
                  </div>
                </div>
                <Slider
                  value={[biometrics.energy_level ? biometrics.energy_level * 100 : 50]}
                  onValueChange={([value]) => handleBiometricChange('energy_level', value / 100)}
                  max={100}
                  step={5}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Agotado (0%)</span>
                  <span>Máxima energía (100%)</span>
                </div>
              </div>

              {/* Stress Level */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <Label>Nivel de Estrés</Label>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">
                      {biometrics.stress_level ? Math.round(biometrics.stress_level * 100) + '%' : 'No establecido'}
                    </span>
                    {biometrics.stress_level && (
                      <Badge 
                        variant="outline" 
                        className={cn("text-xs", getQualityColor(getBiometricQuality('stress_level', biometrics.stress_level)))}
                      >
                        {getBiometricQuality('stress_level', biometrics.stress_level)}
                      </Badge>
                    )}
                  </div>
                </div>
                <Slider
                  value={[biometrics.stress_level ? biometrics.stress_level * 100 : 30]}
                  onValueChange={([value]) => handleBiometricChange('stress_level', value / 100)}
                  max={100}
                  step={5}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Muy relajado (0%)</span>
                  <span>Muy estresado (100%)</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Heart Rate Data */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Heart className="w-5 h-5 text-red-500" />
                Datos Cardíacos
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Resting Heart Rate */}
              <div>
                <Label className="mb-2 block">Frecuencia Cardíaca en Reposo (bpm)</Label>
                <Input
                  type="number"
                  value={biometrics.resting_heart_rate || ''}
                  onChange={(e) => handleBiometricChange('resting_heart_rate', parseFloat(e.target.value) || 0)}
                  placeholder="ej. 65"
                  min="40"
                  max="120"
                />
              </div>

              {/* HRV */}
              <div>
                <Label className="mb-2 block">Variabilidad de Frecuencia Cardíaca (ms)</Label>
                <Input
                  type="number"
                  value={biometrics.heart_rate_variability || ''}
                  onChange={(e) => handleBiometricChange('heart_rate_variability', parseFloat(e.target.value) || 0)}
                  placeholder="ej. 45"
                  min="10"
                  max="200"
                />
              </div>
            </CardContent>
          </Card>

          {/* Recovery Data */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <RotateCcw className="w-5 h-5 text-green-500" />
                Recuperación
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Recovery Status */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <Label>Estado de Recuperación</Label>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">
                      {biometrics.recovery_status ? Math.round(biometrics.recovery_status * 100) + '%' : 'No establecido'}
                    </span>
                    {biometrics.recovery_status && (
                      <Badge 
                        variant="outline" 
                        className={cn("text-xs", getQualityColor(getBiometricQuality('recovery_status', biometrics.recovery_status)))}
                      >
                        {getBiometricQuality('recovery_status', biometrics.recovery_status)}
                      </Badge>
                    )}
                  </div>
                </div>
                <Slider
                  value={[biometrics.recovery_status ? biometrics.recovery_status * 100 : 50]}
                  onValueChange={([value]) => handleBiometricChange('recovery_status', value / 100)}
                  max={100}
                  step={5}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>No recuperado (0%)</span>
                  <span>Completamente recuperado (100%)</span>
                </div>
              </div>

              {/* Readiness Score */}
              <div>
                <Label className="mb-2 block">Puntuación de Readiness (0-100)</Label>
                <Input
                  type="number"
                  value={biometrics.readiness_score || ''}
                  onChange={(e) => handleBiometricChange('readiness_score', parseFloat(e.target.value) || 0)}
                  placeholder="ej. 75"
                  min="0"
                  max="100"
                />
              </div>
            </CardContent>
          </Card>

          {/* Submit Button */}
          <div className="flex justify-center">
            <Button
              onClick={handleSubmitBiometrics}
              disabled={isSubmitting || isLoading}
              className="px-8 py-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
            >
              {isSubmitting || isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Actualizando...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Actualizar Biométricos
                </div>
              )}
            </Button>
          </div>
        </TabsContent>

        {/* Biomarkers Tab */}
        <TabsContent value="biomarkers" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-500" />
                Biomarcadores de Laboratorio
              </CardTitle>
              <div className="text-sm text-gray-600">
                Datos opcionales de análisis de sangre para personalización avanzada
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Hormones */}
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <Label className="mb-2 block">Testosterona (ng/dL)</Label>
                  <Input
                    type="number"
                    value={biomarkers.testosterone || ''}
                    onChange={(e) => handleBiomarkerChange('testosterone', parseFloat(e.target.value) || 0)}
                    placeholder="ej. 650"
                  />
                </div>
                <div>
                  <Label className="mb-2 block">Cortisol (μg/dL)</Label>
                  <Input
                    type="number"
                    value={biomarkers.cortisol || ''}
                    onChange={(e) => handleBiomarkerChange('cortisol', parseFloat(e.target.value) || 0)}
                    placeholder="ej. 12"
                  />
                </div>
              </div>

              {/* Vitamins */}
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <Label className="mb-2 block">Vitamina D (ng/mL)</Label>
                  <Input
                    type="number"
                    value={biomarkers.vitamin_d || ''}
                    onChange={(e) => handleBiomarkerChange('vitamin_d', parseFloat(e.target.value) || 0)}
                    placeholder="ej. 35"
                  />
                </div>
                <div>
                  <Label className="mb-2 block">Vitamina B12 (pg/mL)</Label>
                  <Input
                    type="number"
                    value={biomarkers.b12 || ''}
                    onChange={(e) => handleBiomarkerChange('b12', parseFloat(e.target.value) || 0)}
                    placeholder="ej. 450"
                  />
                </div>
              </div>

              {/* Other Markers */}
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <Label className="mb-2 block">Marcadores de Inflamación (mg/L)</Label>
                  <Input
                    type="number"
                    value={biomarkers.inflammation_markers || ''}
                    onChange={(e) => handleBiomarkerChange('inflammation_markers', parseFloat(e.target.value) || 0)}
                    placeholder="ej. 1.2"
                  />
                </div>
                <div>
                  <Label className="mb-2 block">Glucosa en Ayunas (mg/dL)</Label>
                  <Input
                    type="number"
                    value={biomarkers.glucose || ''}
                    onChange={(e) => handleBiomarkerChange('glucose', parseFloat(e.target.value) || 0)}
                    placeholder="ej. 95"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Device Integration Options */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Smartphone className="w-5 h-5 text-blue-500" />
                Integración con Dispositivos
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                <Button variant="outline" className="p-4 h-auto flex-col">
                  <Watch className="w-8 h-8 mb-2 text-blue-500" />
                  <span className="font-medium">Apple Health</span>
                  <span className="text-xs text-gray-500">Conectar próximamente</span>
                </Button>
                <Button variant="outline" className="p-4 h-auto flex-col">
                  <Activity className="w-8 h-8 mb-2 text-green-500" />
                  <span className="font-medium">Oura Ring</span>
                  <span className="text-xs text-gray-500">Conectar próximamente</span>
                </Button>
                <Button variant="outline" className="p-4 h-auto flex-col">
                  <Heart className="w-8 h-8 mb-2 text-red-500" />
                  <span className="font-medium">WHOOP</span>
                  <span className="text-xs text-gray-500">Conectar próximamente</span>
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Submit Button */}
          <div className="flex justify-center">
            <Button
              onClick={handleSubmitBiomarkers}
              disabled={isSubmitting || isLoading}
              className="px-8 py-2 bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700"
            >
              {isSubmitting || isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Actualizando...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Actualizar Biomarcadores
                </div>
              )}
            </Button>
          </div>
        </TabsContent>
      </Tabs>

      {/* Info Card */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mt-8 p-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg border border-blue-200"
      >
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-500 mt-0.5" />
          <div>
            <h3 className="font-semibold text-blue-800 mb-1">Capa 2: Modulación Fisiológica</h3>
            <p className="text-blue-700 text-sm">
              Esta información permite al Hybrid Intelligence Engine modular las recomendaciones en tiempo real 
              basándose en tu estado fisiológico actual. Datos más precisos = personalización más efectiva.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};