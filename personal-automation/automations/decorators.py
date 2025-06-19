"""
Composable decorators for batch LLM classification with human-in-the-loop validation.

This module provides decorators that can be composed with existing Mirascope decorators:
- @batch/@abatch: Enables batch processing of items through LLM functions
- @hitl_validation/@ahitl_validation: Adds human-in-the-loop validation to classification results
"""

import functools
from functools import reduce, wraps
from typing import Any, Callable, Optional, TypeVar, TypeAlias

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

T = TypeVar('T')  # Input item type
R = TypeVar('R')  # Response/classification type


def batch(
    batch_size: int,
    reduce_fn: Optional[Callable[[R, R], R]] = None
) -> Callable:
    """
    Decorator that enables batch processing of items through a sync LLM function.
    
    Args:
        batch_size: Maximum items per batch
        reduce_fn: Function that merges two results into one. Defaults to addition.
    
    Example:
        @batch(batch_size=5, reduce_fn=lambda a, b: a + b)
        @llm.call(model="gpt-4", response_model=list[str])
        def classify_items(items: list[str]) -> list[str]:
            return items
    """
    if reduce_fn is None:
        reduce_fn = lambda a, b: a + b # noqa: E731
    
    def decorator(func: Callable[[list[T]], R]) -> Callable[[list[T]], R]:
        @wraps(func)
        def wrapper(items: list[T], *args, **kwargs) -> R:
            if len(items) <= batch_size:
                return func(items, *args, **kwargs)
            
            # Multi-batch case
            results = []
            for i in range(0, len(items), batch_size):
                batch_items = items[i:i + batch_size]
                batch_result = func(batch_items, *args, **kwargs)
                results.append(batch_result)
            
            return reduce(reduce_fn, results)
        
        return wrapper
    return decorator


def hitl_validation(
    max_steps: int = 3,
    render_fn: Callable[[R], JSON] | None = None,
    hl_instance: Optional[Any] = None
) -> Callable:
    """
    Decorator that adds human-in-the-loop validation to sync classification results.
    
    Args:
        max_steps: Maximum number of human approval rounds
        hl_instance: HumanLayer instance (defaults to global)
    
    Example:
        @hitl_validation(max_steps=2)
        @llm.call(model="gpt-4", response_model=list[str])
        def classify_with_approval(items: list[str], *, 
                                 prev_result: list[str] = None, 
                                 feedback: str = None) -> list[str]:
            return items
    """
    if render_fn is None:
        render_fn = lambda x: x # noqa: E731

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> R:
            print(f"hitl_validation wrapper called for {func.__name__}")
            hl = hl_instance or _get_default_humanlayer()
            @hl.require_approval()
            def approve_fn(*, x: R) -> R:
                return x

            for i in range(max_steps):
                print(f"Attempt {i+1} of {max_steps} for human approval of {func.__name__}")
                # Get classifications from the wrapped function
                result = func(*args, **kwargs)
                
                # Request human approval (sync version)
                approved_result = approve_fn(x=render_fn(result))

                import ipdb; ipdb.set_trace()
                
                if not _is_reject(approved_result):
                    return approved_result
                
                # If rejected, add feedback for next iteration
                kwargs['prev_result'] = result
                kwargs['feedback'] = approved_result
                    
            raise ValueError(f"Failed to get human approval after {max_steps} attempts")
        
        return wrapper
    return decorator


def self_consistency(
    k: int,
    aggregate_fn: Callable[[list[R]], R]
) -> Callable:
    """
    Decorator that calls the function k times and aggregates results for self-consistency.
    
    Args:
        k: Number of times to call the function
        aggregate_fn: Function that combines k results into a single result
    
    Example:
        @self_consistency(k=3, aggregate_fn=lambda results: max(set(results), key=results.count))
        @llm.call(model="gpt-4", response_model=str)
        def classify_item(item: str) -> str:
            return "classification"
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> R:
            print(f"Running {func.__name__} {k} times for self-consistency")
            results = []
            for _ in range(k):
                result = func(*args, **kwargs)
                results.append(result)
            
            return aggregate_fn(results)
        
        return wrapper
    return decorator


def _is_reject(response: Any) -> bool:
    """Check if a human response indicates rejection."""
    return isinstance(response, str) and response.startswith('User denied')


@functools.lru_cache(maxsize=1)
def _get_default_humanlayer():
    """Get default HumanLayer instance."""
    try:
        from humanlayer import HumanLayer
        return HumanLayer(verbose=True)
    except ImportError:
        raise ImportError(
            "HumanLayer is required for hitl_validation decorator. "
            "Install with: pip install humanlayer"
        )