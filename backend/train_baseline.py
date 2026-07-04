import sys
import os

# Add parent directory to path so app can be resolved
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import SessionLocal
from app.profiler.baseline_trainer import train_baseline

def main():
    print("=========================================")
    print("Kavalar Baseline Training Utility")
    print("=========================================")
    print("Initializing database session...")
    db = SessionLocal()
    try:
        print("Starting training of baseline profile (25 simulated runs)...")
        baseline, stats = train_baseline(db=db, num_runs=25, use_real_agent=False)
        print("-----------------------------------------")
        print("Training Completed Successfully!")
        print(f"Model Version : {baseline.model_version}")
        print(f"Baseline ID   : {baseline.id}")
        print(f"Total Runs    : {stats['total_runs']}")
        print(f"Tools Used    : {', '.join(stats['unique_tools_used'])}")
        print(f"Avg Exec Count: {stats['avg_execution_count_per_run']:.2f}")
        print(f"Avg Exec Time : {stats['avg_execution_time']:.4f}s")
        print(f"Avg Param Len : {stats['avg_parameter_length']:.2f} chars")
        print("=========================================")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR: Baseline training failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
