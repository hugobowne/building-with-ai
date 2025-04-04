# Synthetic Data Experiments

This document outlines the synthetic data experiments conducted using the Evaluation-Driven Development (EDD) framework.

## Experiment Overview

We've successfully implemented the first steps of the EDD flywheel:

1. **Defined Test Cases**: Used the existing personas and scenarios in `definitions.py`
2. **Generated Synthetic Data**: Created 24 synthetic questions across different persona/scenario combinations
3. **Evaluated Responses**: Used the LLM judge to evaluate sample responses

## Generated Questions

We generated 24 synthetic questions covering:
- 3 user types: student, data_scientist, ml_engineer
- 4 scenarios: cohort_student, general, technical, factual
- 2 questions per persona/scenario combination

The questions focus on LLM application development topics such as:
- Prompt engineering best practices
- Evaluation methodologies
- Synthetic data usage
- LLM application reliability
- Integration with existing workflows

## Evaluation Results

We used the LLM judge to evaluate sample responses, which demonstrated:
- The ability to distinguish between acceptable and unacceptable responses
- Detailed reasoning for judgments
- Consistent evaluation criteria

## Next Steps

To complete the EDD flywheel:

1. **Generate Responses**: Run our synthetic questions through a RAG system
   ```bash
   # Example command (would need to be implemented)
   python synthetic-data-EDD/generate_responses.py \
       --questions-file synthetic-data-EDD/data/questions.json \
       --output-file synthetic-data-EDD/data/responses_new.json
   ```

2. **Evaluate New Responses**: Use the LLM judge to evaluate the responses
   ```bash
   python synthetic-data-EDD/simple_llm_judge.py \
       --input-file synthetic-data-EDD/data/responses_new.json \
       --examples-file synthetic-data-EDD/data/evaluated_responses_20250328_190348.json \
       --output-prefix synthetic-data-EDD/data/new_evaluated
   ```

3. **Analyze Results**: Use the HTML viewers to analyze the evaluation results
   ```bash
   # Start HTTP server in the synthetic-data-EDD directory
   cd synthetic-data-EDD && python -m http.server
   
   # Then open in browser:
   # http://localhost:8000/viewers/evaluation_comparison.html
   ```

4. **Iterate**: Based on the evaluation results, improve the system and repeat the process

## Conclusion

The synthetic data generation and evaluation framework provides a powerful methodology for systematically improving LLM applications. By generating diverse test cases and using an LLM judge for evaluation, we can identify areas for improvement and track progress over time.
