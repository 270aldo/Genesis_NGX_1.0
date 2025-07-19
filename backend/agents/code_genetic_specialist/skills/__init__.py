"""
CODE Skills Module
==================

Skills for the CODE Genetic Specialist agent.
"""

from .genetic_analysis import GeneticAnalysisSkill
from .nutrigenomics import NutrigenomicsSkill
from .sport_genetics import SportGeneticsSkill
from .epigenetic_optimization import EpigeneticOptimizationSkill
from .risk_assessment import RiskAssessmentSkill

__all__ = [
    "GeneticAnalysisSkill",
    "NutrigenomicsSkill",
    "SportGeneticsSkill",
    "EpigeneticOptimizationSkill",
    "RiskAssessmentSkill"
]