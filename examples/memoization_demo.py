"""
Memoization Demo

Demonstrates the performance benefits of pipeline memoization when exploring
parameter variants. Shows how shared computation stages are cached and reused.
"""

import numpy as np
import pandas as pd
import time
from sigchain import Pipeline
from sigchain.blocks import LFMGenerator, StackPulses, RangeCompress, DopplerCompress
from sigchain.diagnostics import plot_range_doppler_map

try:
    import staticdash as sd
    STATICDASH_AVAILABLE = True
except ImportError:
    STATICDASH_AVAILABLE = False


def create_dashboard() -> sd.Dashboard:
    """
    Create memoization demo dashboard.
    
    Demonstrates the performance benefits of automatic memoization when
    exploring parameter variants.
    
    Returns:
        Dashboard object ready to be added to a Directory
    """
    dashboard = sd.Dashboard('Memoization Performance')
    page = sd.Page('memoization-demo', 'Memoization Demo')
    
    page.add_header("Pipeline Memoization Performance", level=1)
    page.add_text("""
    When exploring parameter variants, pipelines automatically cache (memoize) intermediate results.
    This means shared computation stages only execute once, dramatically improving performance.
    """)
    
    # Demo 1: Show the concept
    page.add_header("Understanding Memoization", level=2)
    page.add_text("""
    Consider exploring different window functions for range and Doppler compression.
    Without memoization, you'd repeat expensive operations:
    
    - Signal generation runs N×M times
    - Pulse stacking runs N×M times
    - Range compression runs M times per range window
    - Doppler compression runs once per combination
    
    With memoization:
    
    - Signal generation runs **once** (cached and reused)
    - Pulse stacking runs **once** (cached and reused)
    - Range compression runs N times (once per range window)
    - Doppler compression runs N×M times (can't be shared)
    
    For 3 range windows × 2 Doppler windows = 6 combinations, this means:
    - Without cache: 12 signal generations, 6 range compressions
    - With cache: 1 signal generation, 3 range compressions
    """)
    
    page.add_header("Code Example", level=2)
    code_example = """
from sigchain import Pipeline
from sigchain.blocks import LFMGenerator, StackPulses, RangeCompress, DopplerCompress
import time

# Exploring 3×2 = 6 combinations with memoization enabled (default)
start = time.time()
results_cached = (Pipeline("Radar", enable_cache=True)
    .add(LFMGenerator(num_pulses=128))  # Runs once, cached
    .add(StackPulses())                  # Runs once, cached
    .variants(lambda w: RangeCompress(window=w), 
              ['hamming', 'hann', 'blackman'],
              names=['Hamming', 'Hann', 'Blackman'])  # Runs 3 times
    .variants(lambda w: DopplerCompress(window=w), 
              ['hamming', 'hann'],
              names=['Hamming', 'Hann'])              # Runs 6 times
    .run()
)
cached_time = time.time() - start

# Same pipeline without memoization
start = time.time()
results_uncached = (Pipeline("Radar", enable_cache=False)
    .add(LFMGenerator(num_pulses=128))  # Runs 6 times
    .add(StackPulses())                  # Runs 6 times
    .variants(lambda w: RangeCompress(window=w), 
              ['hamming', 'hann', 'blackman'],
              names=['Hamming', 'Hann', 'Blackman'])  # Runs 6 times
    .variants(lambda w: DopplerCompress(window=w), 
              ['hamming', 'hann'],
              names=['Hamming', 'Hann'])              # Runs 6 times
    .run()
)
uncached_time = time.time() - start

speedup = uncached_time / cached_time
print(f"With cache: {cached_time:.2f}s")
print(f"Without cache: {uncached_time:.2f}s")
print(f"Speedup: {speedup:.1f}x")
"""
    page.add_syntax(code_example, language='python')
    
    # Live performance comparison
    page.add_header("Live Performance Comparison", level=2)
    page.add_text("Running the same parameter exploration with and without memoization:")
    
    # Test with cache enabled
    page.add_text("\\n**Running with memoization enabled...**")
    start_cached = time.time()
    results_cached = (Pipeline("CachedPipeline", enable_cache=True)
        .add(LFMGenerator(num_pulses=128, target_delay=2e-6, target_doppler=200.0, noise_power=0.01))
        .add(StackPulses())
        .variants(lambda w: RangeCompress(window=w, oversample_factor=2), 
                 ['hamming', 'hann', 'blackman'],
                 names=['Hamming', 'Hann', 'Blackman'])
        .variants(lambda w: DopplerCompress(window=w, oversample_factor=2), 
                 ['hamming', 'hann'],
                 names=['Hamming', 'Hann'])
        .run(verbose=False)
    )
    cached_time = time.time() - start_cached
    
    # Clear cache before uncached run
    Pipeline._global_cache.clear()
    
    # Test without cache
    page.add_text("\\n**Running without memoization...**")
    start_uncached = time.time()
    results_uncached = (Pipeline("UncachedPipeline", enable_cache=False)
        .add(LFMGenerator(num_pulses=128, target_delay=2e-6, target_doppler=200.0, noise_power=0.01))
        .add(StackPulses())
        .variants(lambda w: RangeCompress(window=w, oversample_factor=2), 
                 ['hamming', 'hann', 'blackman'],
                 names=['Hamming', 'Hann', 'Blackman'])
        .variants(lambda w: DopplerCompress(window=w, oversample_factor=2), 
                 ['hamming', 'hann'],
                 names=['Hamming', 'Hann'])
        .run(verbose=False)
    )
    uncached_time = time.time() - start_uncached
    
    # Calculate speedup
    speedup = uncached_time / cached_time
    time_saved = uncached_time - cached_time
    
    # Create results table
    results_data = {
        'Configuration': ['With Memoization', 'Without Memoization', 'Time Saved', 'Speedup'],
        'Execution Time': [
            f'{cached_time:.3f}s',
            f'{uncached_time:.3f}s',
            f'{time_saved:.3f}s',
            f'{speedup:.2f}x'
        ],
        'Description': [
            'Shared stages cached',
            'All stages re-executed',
            'Performance improvement',
            'Relative speedup'
        ]
    }
    
    results_df = pd.DataFrame(results_data)
    page.add_table(results_df)
    
    page.add_text(f"""
    **Result**: Memoization provides a **{speedup:.1f}x speedup** for this parameter exploration!
    
    The speedup comes from:
    - Signal generation (expensive FFT operations) runs once instead of 6 times
    - Pulse stacking runs once instead of 6 times
    - Range compression runs 3 times instead of 6 times
    """)
    
    # Scaling analysis
    page.add_header("Scaling with Parameter Space Size", level=2)
    page.add_text("""
    The benefits of memoization scale with the size of your parameter space.
    Let's see how speedup changes with different numbers of variants:
    """)
    
    scaling_data = []
    
    for n_variants in [2, 3, 4, 5]:
        windows = ['hamming', 'hann', 'blackman', 'bartlett', 'kaiser'][:n_variants]
        names = ['Hamming', 'Hann', 'Blackman', 'Bartlett', 'Kaiser'][:n_variants]
        
        # With cache
        Pipeline._global_cache.clear()
        start = time.time()
        _ = (Pipeline("Test", enable_cache=True)
            .add(LFMGenerator(num_pulses=64, target_delay=2e-6, target_doppler=200.0))
            .add(StackPulses())
            .variants(lambda w: RangeCompress(window=w), windows, names=names)
            .variants(lambda w: DopplerCompress(window=w), windows[:2], names=names[:2])
            .run(verbose=False)
        )
        cached = time.time() - start
        
        # Without cache
        Pipeline._global_cache.clear()
        start = time.time()
        _ = (Pipeline("Test", enable_cache=False)
            .add(LFMGenerator(num_pulses=64, target_delay=2e-6, target_doppler=200.0))
            .add(StackPulses())
            .variants(lambda w: RangeCompress(window=w), windows, names=names)
            .variants(lambda w: DopplerCompress(window=w), windows[:2], names=names[:2])
            .run(verbose=False)
        )
        uncached = time.time() - start
        
        scaling_data.append({
            'Range Windows': n_variants,
            'Doppler Windows': 2,
            'Total Combinations': n_variants * 2,
            'Time (Cached)': f'{cached:.3f}s',
            'Time (Uncached)': f'{uncached:.3f}s',
            'Speedup': f'{uncached/cached:.2f}x'
        })
    
    scaling_df = pd.DataFrame(scaling_data)
    page.add_table(scaling_df)
    
    page.add_text("""
    As you can see, the speedup increases with more combinations because:
    - More combinations = more repeated work without cache
    - Cached version still only runs shared stages once
    """)
    
    # Show a few example results
    page.add_header("Example Results", level=2)
    page.add_text("Here are a few of the parameter combinations we explored:")
    
    # Show first 3 results
    for i, (params, result) in enumerate(results_cached[:3]):
        title = f"Range: {params['variant'][0]}, Doppler: {params['variant'][1]}"
        fig = plot_range_doppler_map(result, title=title, height=400,
                                     use_db=True, mark_target=True)
        page.add_plot(fig, height=400)
    
    # Best practices
    page.add_header("Best Practices", level=2)
    page.add_text("""
    To maximize the benefits of memoization:
    
    1. **Structure pipelines strategically**: Put expensive operations that are common 
       across variants early in the pipeline, before the first `.variants()` call.
    
    2. **Use `.variants()` not loops**: Instead of manually looping over parameters,
       use `.variants()` to let the framework handle caching automatically.
    
    3. **Group similar explorations**: If exploring multiple parameter dimensions,
       do them in one pipeline rather than separate runs.
    
    4. **Clear cache when needed**: The cache is shared across all Pipeline instances.
       Clear it with `Pipeline._global_cache.clear()` when starting a new experiment.
    
    5. **Disable cache for debugging**: Use `enable_cache=False` when debugging or when
       you explicitly want fresh execution (e.g., testing randomness).
    """)
    
    page.add_header("When Memoization Helps Most", level=2)
    page.add_text("""
    Memoization provides the biggest benefits when:
    
    - **Exploring parameter spaces**: Testing different processing parameters
    - **Expensive early stages**: Signal generation, filtering, or other costly operations
    - **Many combinations**: Large cartesian products of variants
    - **Branching pipelines**: Multiple processing paths from the same source
    - **Iterative development**: Re-running similar experiments during development
    
    It's less helpful when:
    - Running a single linear pipeline (no variants)
    - Every stage is unique (no shared computation)
    - Intermediate results are very large (cache memory overhead)
    """)
    
    dashboard.add_page(page)
    return dashboard


if __name__ == "__main__":
    if not STATICDASH_AVAILABLE:
        print("staticdash not available. Install with: pip install staticdash")
    else:
        print("Creating memoization demo dashboard...")
        dashboard = create_dashboard()
        
        # Publish standalone
        directory = sd.Directory(title='Memoization Demo', page_width=1000)
        directory.add_dashboard(dashboard, slug='memoization-demo')
        directory.publish('staticdash')
        
        print("✓ Dashboard published to staticdash/")
        print("  Open staticdash/index.html in a web browser")
