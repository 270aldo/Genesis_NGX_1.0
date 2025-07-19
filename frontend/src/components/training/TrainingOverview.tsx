
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Dumbbell, 
  Target, 
  Calendar, 
  TrendingUp, 
  Clock, 
  CheckCircle,
  Play,
  BarChart3
} from 'lucide-react';
import { useTrainingStore } from '@/store/trainingStore';
import { PDFUpload } from './PDFUpload';

export const TrainingOverview: React.FC = () => {
  const { currentPlan, completeWorkout } = useTrainingStore();

  if (!currentPlan) {
    return (
      <div className="space-y-6">
        <PDFUpload />
        
        <Card className="glass-ultra border-white/10 bg-white/5">
          <CardContent className="p-8 text-center">
            <Dumbbell className="h-16 w-16 text-white/20 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">
              No Training Plan Active
            </h3>
            <p className="text-white/60 mb-6">
              Upload your training plan PDF to get started with AI-powered workout tracking
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const progressPercentage = (currentPlan.completedWorkouts / currentPlan.totalWorkouts) * 100;

  return (
    <div className="space-y-6">
      {/* Current Plan Overview */}
      <Card className="glass-ultra border-white/10 bg-white/5">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-white flex items-center gap-2">
              <Target className="h-5 w-5" />
              {currentPlan.name}
            </CardTitle>
            <Badge variant="secondary" className="bg-blue-500/20 text-blue-300">
              {currentPlan.duration} weeks
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-white/60">Overall Progress</span>
              <span className="text-white/60">
                {currentPlan.completedWorkouts}/{currentPlan.totalWorkouts} workouts
              </span>
            </div>
            <Progress value={progressPercentage} className="h-3" />
            <p className="text-center text-white/80 font-medium">
              {progressPercentage.toFixed(1)}% Complete
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-white/5 rounded-lg border border-white/10">
              <Calendar className="h-8 w-8 text-blue-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{currentPlan.workoutDays.length}</div>
              <div className="text-sm text-white/60">Workout Days</div>
            </div>
            <div className="text-center p-4 bg-white/5 rounded-lg border border-white/10">
              <CheckCircle className="h-8 w-8 text-green-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{currentPlan.completedWorkouts}</div>
              <div className="text-sm text-white/60">Completed</div>
            </div>
            <div className="text-center p-4 bg-white/5 rounded-lg border border-white/10">
              <Clock className="h-8 w-8 text-purple-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{currentPlan.duration}</div>
              <div className="text-sm text-white/60">Weeks</div>
            </div>
            <div className="text-center p-4 bg-white/5 rounded-lg border border-white/10">
              <TrendingUp className="h-8 w-8 text-orange-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">94%</div>
              <div className="text-sm text-white/60">Adherence</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Workout Days */}
      <Card className="glass-ultra border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Dumbbell className="h-5 w-5" />
            Workout Schedule
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {currentPlan.workoutDays.map((day, index) => (
              <div
                key={day.id}
                className="p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                      day.completed 
                        ? 'bg-green-500/20 text-green-300 border border-green-500/30' 
                        : 'bg-white/10 text-white/60 border border-white/20'
                    }`}>
                      {day.completed ? <CheckCircle className="h-4 w-4" /> : index + 1}
                    </div>
                    <div>
                      <h4 className="text-white font-medium">{day.name}</h4>
                      <p className="text-white/60 text-sm">{day.exercises.length} exercises</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {day.completed ? (
                      <Badge variant="secondary" className="bg-green-500/20 text-green-300">
                        Completed
                      </Badge>
                    ) : (
                      <Button
                        size="sm"
                        onClick={() => completeWorkout(day.id)}
                        className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
                      >
                        <Play className="h-4 w-4 mr-2" />
                        Start
                      </Button>
                    )}
                  </div>
                </div>
                
                {/* Exercise Preview */}
                <div className="mt-3 ml-11 space-y-1">
                  {day.exercises.slice(0, 3).map((exercise) => (
                    <div key={exercise.id} className="text-sm text-white/60">
                      {exercise.name} - {exercise.sets} sets × {exercise.reps}
                    </div>
                  ))}
                  {day.exercises.length > 3 && (
                    <div className="text-sm text-white/40">
                      +{day.exercises.length - 3} more exercises
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="glass-ultra border-white/10 bg-white/5">
          <CardContent className="p-6">
            <Button className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
              <BarChart3 className="h-4 w-4 mr-2" />
              View Progress Charts
            </Button>
          </CardContent>
        </Card>
        <Card className="glass-ultra border-white/10 bg-white/5">
          <CardContent className="p-6">
            <PDFUpload />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
