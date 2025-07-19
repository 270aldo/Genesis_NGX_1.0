
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useNutritionStore } from '@/store/nutritionStore';
import { PDFUpload } from './PDFUpload';
import { CalendarDays, Target, Clock, FileText } from 'lucide-react';

export const NutritionOverview: React.FC = () => {
  const { currentPlan, clearCurrentPlan } = useNutritionStore();

  if (!currentPlan) {
    return (
      <div className="space-y-6">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-light text-white/90 mb-2">Centro de Nutrición</h2>
          <p className="text-white/60">Carga tu plan nutricional para comenzar</p>
        </div>
        <PDFUpload />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-light text-white/90 mb-2">Plan Nutricional Activo</h2>
          <p className="text-white/60">{currentPlan.name}</p>
        </div>
        <Button
          variant="outline"
          onClick={clearCurrentPlan}
          className="border-white/20 text-white/80 hover:bg-white/5"
        >
          Cambiar Plan
        </Button>
      </div>

      {/* Plan Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="glass-ultra border-white/10 bg-white/5">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Target className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <p className="text-white/60 text-sm">Calorías Diarias</p>
                <p className="text-white font-semibold">{currentPlan.macros.calories}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-ultra border-white/10 bg-white/5">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-500/20 rounded-lg">
                <CalendarDays className="w-5 h-5 text-green-400" />
              </div>
              <div>
                <p className="text-white/60 text-sm">Duración</p>
                <p className="text-white font-semibold">{currentPlan.duration} días</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-ultra border-white/10 bg-white/5">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <Clock className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <p className="text-white/60 text-sm">Comidas</p>
                <p className="text-white font-semibold">{currentPlan.meals.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-ultra border-white/10 bg-white/5">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-500/20 rounded-lg">
                <FileText className="w-5 h-5 text-orange-400" />
              </div>
              <div>
                <p className="text-white/60 text-sm">Proteína</p>
                <p className="text-white font-semibold">{currentPlan.macros.protein}g</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Macros Breakdown */}
      <Card className="glass-ultra border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle className="text-white">Distribución de Macronutrientes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto bg-red-500/20 rounded-full flex items-center justify-center mb-2">
                <span className="text-red-400 font-bold">{currentPlan.macros.protein}g</span>
              </div>
              <p className="text-white/80 font-medium">Proteína</p>
              <p className="text-white/60 text-sm">
                {Math.round((currentPlan.macros.protein * 4 / currentPlan.macros.calories) * 100)}%
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 mx-auto bg-blue-500/20 rounded-full flex items-center justify-center mb-2">
                <span className="text-blue-400 font-bold">{currentPlan.macros.carbs}g</span>
              </div>
              <p className="text-white/80 font-medium">Carbohidratos</p>
              <p className="text-white/60 text-sm">
                {Math.round((currentPlan.macros.carbs * 4 / currentPlan.macros.calories) * 100)}%
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 mx-auto bg-yellow-500/20 rounded-full flex items-center justify-center mb-2">
                <span className="text-yellow-400 font-bold">{currentPlan.macros.fat}g</span>
              </div>
              <p className="text-white/80 font-medium">Grasas</p>
              <p className="text-white/60 text-sm">
                {Math.round((currentPlan.macros.fat * 9 / currentPlan.macros.calories) * 100)}%
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Today's Meals */}
      <Card className="glass-ultra border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle className="text-white">Comidas de Hoy</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {currentPlan.meals.map((meal) => (
              <div key={meal.id} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div>
                  <h3 className="text-white font-medium">{meal.name}</h3>
                  <p className="text-white/60 text-sm">{meal.time}</p>
                  <p className="text-white/80 text-sm">{meal.ingredients.join(', ')}</p>
                </div>
                <div className="text-right">
                  <p className="text-white font-medium">{meal.calories} cal</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
