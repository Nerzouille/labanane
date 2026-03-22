"""Pipeline registry — assembles the ordered list of steps.

To insert a step: add the import and insert the instance at the desired index.
The engine reads len(PIPELINE) at run-start for total_steps; no engine changes needed.
"""
from .step_base import Step
from .steps.s01_description import ProductDescriptionStep
from .steps.s02_keyword_refinement import KeywordRefinementStep
from .steps.s03_keyword_confirmation import KeywordConfirmationStep
from .steps.s04_product_research import ProductResearchStep
from .steps.s05_product_validation import ProductValidationStep
from .steps.s06_market_research import MarketResearchStep
from .steps.s07_ai_analysis import AiAnalysisStep
from .steps.s08_persona_generation import PersonaGenerationStep
from .steps.s09_final_criteria import FinalCriteriaStep
from .steps.s10_report import ReportGenerationStep

PIPELINE: list[Step] = [
    ProductDescriptionStep(),
    KeywordRefinementStep(),
    KeywordConfirmationStep(),
    ProductResearchStep(),
    ProductValidationStep(),
    MarketResearchStep(),
    AiAnalysisStep(),
    PersonaGenerationStep(),
    FinalCriteriaStep(),
    ReportGenerationStep(),
]
